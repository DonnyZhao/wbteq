# coding=utf-8
"""
This is the module to parse log and send email notification
"""

from os.path import basename
import os
try:
    import win32com.client as win32
except ImportError as e:
    pass
import re


def deliver_email(email_addr, subject, body, attached_files=[]):
    """
    Delivery email by launch outlook
    """
    if not isinstance(attached_files, list):
        raise TypeError('please give file path as list')

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = email_addr
    mail.Subject = subject
    mail.Body = 'This is an automatic email from WBTEQ'
    mail.HTMLBody = """This is an automatic email from WBTEQ"""

    #In case you want to attach a file to the email
    if len(attached_files) > 0:
        for f_path in attached_files:
            mail.Attachments.Add(f_path)
    mail.Send()


def send_notification(rcode, cmd_file, emails):
    if rcode != 0:
        title = '[Error: {}]'.format(rcode) + basename(cmd_file)
    else:
        title = '[Success]' + basename(cmd_file)

    curr_dir = os.getcwd()
    attach_file_list = []
    # .cmd file is not able to be attached
    # attach_file_list.append(cmd_file)

    lines = [x.strip() for x in open(cmd_file) if x.startswith('bteq')]
    for line in lines:
        bteq_file = line.split('<')[1].split('>>')[0].strip()
        attach_file_list.append(os.path.join(curr_dir,bteq_file))

        log_file = os.path.join(curr_dir,line.split('>>')[1].strip())
        # the log file name must be duplicated in the file
        if log_file not in attach_file_list:
            attach_file_list.append(log_file)

    print('title:{}'.format(title))
    print('email:{}'.format(emails))
    print('logs:{}'.format('\n'.join(attach_file_list)))
    deliver_email(emails, title, 'body', attach_file_list)
