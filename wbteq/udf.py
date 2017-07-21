# coding=utf-8
from datetime import datetime, date, timedelta


def udf_call(command):
    """
    pass the command with this format func$fmt$offset
    func - month_end
    fmt  - str, month_key, date, or a given format
    offset - -1, 0, 1 or any number of month offset
    """
    func, p1, p2 = command.split('$')

    fund_library = {}
    def month_end(fmt='str', offset=0):
        today = datetime.now()
        next_month_begin = date(today.year, (today.month + 1 + offset) % 12, 1)
        one_day = timedelta(days=-1)
        month_end_date = next_month_begin + one_day
        if fmt == 'str':
            return month_end_date.strftime('%Y%m%d')
        elif fmt == 'month_key':
            return month_end_date.strftime('%Y%m')
        elif fmt == 'date':
            return "CAST('{}' AS DATE FORMAT 'DD/MM/YYYY')".format(month_end_date.strftime('%d/%m/%Y'))
        else:
            return month_end_date.strftime(fmt)
    fund_library['month_end'] = month_end

    if func not in fund_library.keys():
        raise SystemExit('{} has not been defined')

    return fund_library[func](fmt=p1, offset=int(p2))
