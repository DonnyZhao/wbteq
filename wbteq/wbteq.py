# coding=utf-8
#!/usr/bin/env python

import argparse
import sys
import os
from datetime import datetime
import os.path
from collections import namedtuple
import logging
from subprocess import call
import pyodbc
from string import Formatter


from . import __version__
from .udf import exec_udf
from .comm import send_notification




Job = namedtuple('Job',['job_id','job_name','job_email'])
Step = namedtuple('Step',['job_id','step_id','filename','seq_num'])
Param = namedtuple('Param',['step_id','param_name','param_value'])


# Setup the logger
logger = logging.getLogger('WBTEQ')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Build the DB connection string
db_url = os.environ.get('WBTEQ_DB_URL','N/A')
logger.info('Get the WBTEQ_DB_URL {}'.format(db_url))

db_name = os.environ.get('WBTEQ_DB_NAME','N/A')
logger.info('Get the WBTEQ_DB_NAME {}'.format(db_name))

if db_url == 'N/A' or db_name == 'N/A':
    raise SystemExit('Please make sure WBTEQ_DB_URL / WBTEQ_DB_NAME has been created in Envrionment Variable')


TERADATA_DSN = "DRIVER=Teradata;DBCNAME=" + db_url.strip()+ ";UID={u};PWD={p};QUIETMODE=YES"
TERADATA_DSN = TERADATA_DSN + ";Database="+db_name

def _check_folder(folder_name):
    if not isinstance(folder_name, str):
        raise TypeError('{} is not a valid folder name'.format(folder_name))
    if os.path.isdir(folder_name):
        logger.info('[{}] already exist'.format(folder_name))
        return folder_name
    else:
        try:
            os.mkdir(folder_name)
            logger.info('[{}] has been created'.format(folder_name))
            return folder_name
        except FileExistsError:
            raise
        else:
            raise

def _get_full_path(d=None):
    if d is None:
        return os.getcwd()
    else:
        return os.path.join(os.getcwd(), d)

def _delete_older_files(wf, no_of_days):
    logger.info('Delete old logs/scripts in [{}]'.format(_get_full_path(wf)))
    logger.info('Delete old logs/scripts [{}] days before'.format(no_of_days))
    curr_date = datetime.now()
    counter = 0
    for _file in os.listdir(wf):
        if _file.endswith('cmd') or _file.endswith('log'):
            dt_str = _file.split('_')[-2]
            dt_date = datetime.strptime(dt_str, "%Y%m%d")
            delta = curr_date - dt_date
            if delta.days >= int(no_of_days):
                os.remove(os.path.join(wf,_file))
                counter = counter + 1
                logger.info('{} has been deleted'.format(_file))
    return counter

def get_all_jobs(cursor):
    """
    Query the jobs table, and return valid jobs
    TODO Need to use ENV for schema
    """
    return_jobs = []
    sql_fetch_jobs = """
                    select
                    	job_id
                    , 	job_name
                    , 	job_owner_email
                    from c4ustcrm.wbteq_jobs j
                    JOIN SYS_CALENDAR.Calendar c
                    ON   c.Calendar_date = Current_Date

                    where
                    	j.is_enabled = 'Y'
                    and (
                    		j.freq = 'D'
                    	OR (j.freq = 'M' and c.day_of_month = j.day_of_month)
                    	OR (j.freq = 'W' and c.day_of_week = j.day_of_week)
                    	);"""

    logger.info('Running SQL Query for jobs')
    cursor.execute(sql_fetch_jobs)
    rows = cursor.fetchall()
    for row in rows:
        j = Job(row.job_id, row.job_name, row.job_owner_email)
        return_jobs.append(j)
    return return_jobs

def get_all_steps(cursor):
    return_steps = []
    sql_fetch_steps = """
                        select
                    	step_id
                    ,	job_id
                    ,	seq_num
                    ,	filename
                    from wbteq_steps;"""

    cursor.execute(sql_fetch_steps)
    rows = cursor.fetchall()
    for row in rows:
        s = Step(row.job_id, row.step_id, row.filename, row.seq_num)
        return_steps.append(s)
    return return_steps

def get_all_params(cursor):
    return_params = []
    sql_fetch_params = """
                        select
                    	step_id
                    ,	param_type
                    ,	param_name
                    ,	param_value
                    from wbteq_params;"""
    cursor.execute(sql_fetch_params)
    rows = cursor.fetchall()
    for row in rows:
        if row.param_type == 'D':
            v = row.param_value
        elif row.param_type == 'P':
            v = exec_udf(row.param_value)
        elif row.param_type == 'S':
            v = row.param_value
        p = Param(row.step_id, row.param_name, v)
        return_params.append(p)

    logger.debug('run udf {}'.format(exec_udf('hello world')))
    return return_params



def _check_job_files(lib_folder, files):
    if isinstance(files, str):
        return os.path.isfile(os.path.join(lib_folder, files))
    elif isinstance(files, list):
        r = True
        for item in files:
            logger.debug('check {}'.format(os.path.join(lib_folder, item)))
            if not os.path.isfile(os.path.join(lib_folder, item)):
                r = False
                break
            else:
                pass
        return r
    else:
        raise TypeError('files must be a str or list')

def build_job_def_list(lib_folder, user, password):
    logger.info('Connecting to database ...')

    conn = pyodbc.connect(TERADATA_DSN.format(u=user,p=password))
    cursor = conn.cursor()

    jobs = get_all_jobs(cursor)
    steps = get_all_steps(cursor)
    params = get_all_params(cursor)

    logger.info('Closing to database ...')
    cursor.close()
    conn.close()

    job_defs = []
    for job in jobs:
        job_def = {}
        job_def['job_id'] = job.job_id
        job_def['job_name'] = job.job_name
        job_def['job_email'] = job.job_email
        job_def['steps'] = []
        for step in steps:
            if step.job_id == job.job_id:
                step_def = {}
                step_def['step_id'] = step.step_id
                step_def['seq_num'] = step.seq_num
                step_def['filename'] = step.filename
                step_def['params'] = {}
                for param in params:
                    if param.step_id == step.step_id:
                        step_def['params'][param.param_name] = param.param_value
                    else:
                        pass
                job_def['steps'].append(step_def)
            else:
                pass
        # check if the file exists before append
        logger.debug('found {}'.format(job_def))
        if len(job_def['steps']) == 0:
            logger.warning('No steps are defined for job [{}] - IGNORED'.format(job_def['job_name']))
        elif not _check_job_files(lib_folder, [x['filename'] for x in job_def['steps']]):
            logger.warning('At least one file not found for job [{}] - IGNORED'.format(job_def['job_name']))
        else:
            logger.info('New job has been added {}'.format(job_def))
            job_defs.append(job_def)
    return job_defs


def generate_scripts(username, password, lib, work, job):
    """
    Genearte all replaced bteq files and the cmd file,
    return the (full path of command file, email)

    If failed, return None
    """
    dt_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fmt = Formatter()
    success_flag = True
    # sort all steps by seq_num
    sorted_steps = sorted(job['steps'],key=lambda x:x['seq_num'])

    for s in sorted_steps:
        f = s['filename']
        in_param = s['params'] # this is a dict
        in_param['username'] = username
        in_param['password'] = password

        with open(os.path.join(lib,f),mode='tr',encoding='utf8') as fdin, open(os.path.join(work,f),mode='tw',encoding='utf8') as fdout:
            text = fdin.read().replace(u'\ufeff', '') # This is to handle the BOM character

            # data = [x.strip() for x in fdin.read().splitlines() if not x.startswith('--')]
            # text = '\n'.join(data)
            keys_from_file = set([v[1] for v in fmt.parse(text)][:-1])
            # Check if username and password in the template file
            if 'username' not in keys_from_file or 'password' not in keys_from_file:
                logger.warning('password or username not found in {}'.format(f))
                success_flag = False

            # Check if all parameters are defined in the table
            for key in keys_from_file:
                if key not in in_param.keys():
                    success_flag = False
                    logger.warning('{} has not been defined in the wbteq_params'.format(key))
                else: # found the key
                    if key != 'password':
                        logger.info('Parsed : Step - {}, {} -> {}'.format(f, key, in_param[key]))

            # failed to generate the job scripts, because one of above reasons
            if success_flag is False:
                logger.warning('Failed to generate scripts for job {}'.format(job['job_name']))
                break


            fdout.write('/* This file is generated by WBTEQ at {} */\n'.format(datetime.now()))
            fdout.write(text.format(**in_param))
            logger.info('Writing {} with replaced value'.format(f))


    # generate the cmd file
    if success_flag is True:
        cmd_file = job['job_name'].replace(' ','_') + '_' + dt_stamp + '.cmd'
        log_file = job['job_name'].replace(' ','_') + '_' + dt_stamp + '.log'
        with open(os.path.join(work, cmd_file), 'w') as fcmd:
            fcmd.write('REM This file is generated by WBTEQ at {}\n'.format(datetime.now()))
            # fcmd.write('# This file is generated by WBTEQ at {}\n'.format(datetime.now()))
            for s in sorted_steps:
                fcmd.write('bteq < {bteq} >> {log}\n'.format(bteq=os.path.join(work,s['filename']),
                                                             log=os.path.join(work,log_file)))

        return (os.path.join(work, cmd_file), job['job_email'])
    else:
        return None


def get_parser():
    parser = argparse.ArgumentParser(description='BTEQ Jobs management on Windows')
    parser.add_argument('username', type=str,
                        help='The Teradata logon name for running BTEQ(s)')

    parser.add_argument('password', type=str,
                        help='The Teradata logon password for running BTEQ(s)')

    parser.add_argument('-l','--lib', default='_libs',
                        help='The library folder for WBTEQ (default _libs)',
                        action='store')

    parser.add_argument('-f','--folder', default='_wbteq',
                        help='The working folder for WBTEQ (default _wbteq)',
                        action='store')

    parser.add_argument('-d','--days', default=7,
                        help='The # of days to keep logs/scripts (default 7)',
                        action='store')

    parser.add_argument('-e','--exec', default=False,
                        help='The flag to execute BTEQ, only for production mode',
                        action='store_true')

    parser.add_argument('-v', '--version', help='displays the current version of wbteq',
                        action='store_true')

    return parser


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if not os.path.isdir(args['lib']):
        raise SystemExit('Please make sure the [{}] folder is created'.format(args['lib']))

    logger.info('The current folder is [{}]'.format(_get_full_path()))

    if _check_folder(_get_full_path(args['folder'])):
        pass
    else:
        raise ValueError('Create folder failed')

    no_of_deleted = _delete_older_files(_get_full_path(args['folder']),args['days'])
    logger.info('{} file(s) have been deleted.'.format(no_of_deleted))

    # build the jobs (all json format)
    # it checks of the job file exists or not
    jobs = build_job_def_list(_get_full_path(args['lib']),
                              user=args['username'],
                              password=args['password'])

    logger.info('[{}] valid job(s) has been found'.format(len(jobs)))
    for j in jobs:
        logger.info('Job name: [{}] has [{}] steps'.format(j['job_name'], len(j['steps'])))

    command_files = []
    for job in jobs:
        cmd_file = generate_scripts( args['username'],
                                     args['password'],
                                     args['lib'],
                                     args['folder'],
                                     job)
        if cmd_file is not None:
            logger.info('[{}] has been created'.format(cmd_file))
            command_files.append(cmd_file)
        else:
            # TODO:
            pass


    for cmd_email in command_files:
        cmd, email = cmd_email
        abs_cmd = _get_full_path(cmd)
        if args['exec'] is False:
            logger.info('Command to be run: {}'.format(abs_cmd))
        else:
            rcode = call(abs_cmd, shell=True)
            # rcode = 0
            if rcode == 0:
                logger.info('Calling {} successful'.format(abs_cmd))
            else:
                logger.warning('Failed to call {}'.format(abs_cmd))
            logger.info('Sending email for {} to {}'.format(abs_cmd, email))
            send_notification(abs_cmd, email)


if __name__ == '__main__':
    command_line_runner()
