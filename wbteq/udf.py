# coding=utf-8
from datetime import datetime

def exec_udf(command):
    now = datetime.now()

    if not isinstance(command, str):
        raise TypeError('{} must be a str'.format(command))
    if command == 'month_end_key': # yyyymmdd
        return now.strftime("%Y%m") + '01'
    elif command == 'month_key':
        return now.strftime("%Y%m")
    else:
        return 'N/A'
