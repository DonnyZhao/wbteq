# Wrapper for Teradata BTEQ Command

Welcome to the project **WBTEQ**, I supppose you are struggling with how to run BTEQ scripts on Windows platform, then you are on the right page.

The purpose of this project is to make life easier to run BTEQ scripts on Windows. To test/intall/deploy **WBTEQ**, here are the basic requirement:

* You need a Windows machine, and you have the permission to install `pip` package, you also need to create Envrionment Variable
* You need the Teradata Utility installed on that machine, try to run `bteq` command from console
* You have the connection detial of a Teradata server, and you have the write permission to at least one schema
* Python 3.5+ is required, and `pyodbc` - https://github.com/mkleehammer/pyodbc is intalled

## How to install

* The first task, create two new envrionment variables  
`WBTEQ_DB_NAME` - the database name you have write permission  
`WBTEQ_DB_URL` - database URL
* Find the file `system_tables_ddl.sql` and execute the SQLs to create system tables on Teradata
* Run the test case by run `python test_wbteq.py` - check if any failed
* Install the package by `python setup.py install` (you may need the permission depends on where to be installed)


## Design and Workflow

![workflow](arts\workflow.png)

TODO: A ER diagram is required

There are three tables in Teradata to store the information about BTEQ jobs. Use SQL query to get the jobs to be run, check `freq`,`is_enabled` and compare to current date/time to decided if the job to be run.

This program will be scheduled as a repeated job for every 1 hour, and it invokes all other BTEQ jobs.

### wbteq_jobs
- job_id `pk`
- freq ('M','W','D')
- day_of_month
- day_of_week
- hour24
- job_name
- job_owner
- job_owner_email
- is_enabled ('Y','N')
- created_at
- updated_at

### wbteq_steps
- step_id `pk`
- job_id `fk`
- seq_num
- filename
- created_at
- updated_at

### wbteq_params
- param_id `pk`
- step_id `fk`
- param_type ('D','P','S')  Direct / Python / SQL
- param_name
- param_value
- created_at
- updated_at

## Usage
```
usage: wbteq [-h] [-l LIB] [-f FOLDER] [-d DAYS] [-v] username password

BTEQ Jobs management on Windows

positional arguments:
  username              The Teradata logon name for running BTEQ(s)
  password              The Teradata logon password for running BTEQ(s)

optional arguments:
  -h, --help            show this help message and exit
  -l LIB, --lib LIB     The library folder for WBTEQ (default _libs)
  -f FOLDER, --folder FOLDER
                        The working folder for WBTEQ (default _wbteq)
  -d DAYS, --days DAYS  The # of days to keep logs/scripts (default 7)
  -v, --version         displays the current version of wbteq
```

This is a sample command to call the program with default
```
C:\>wbteq tduser tdpass
```
