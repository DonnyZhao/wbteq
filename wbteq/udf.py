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
        new_month = today.month + 1 + offset
        if new_month <= 12 and new_month > 0:
            m = today.month + 1 + offset
            y = today.year
        elif new_month == 0:
            m = 12
            y = today.year - 1
        elif new_month > 12:
            delta_y = int(new_month / 12)
            m = new_month % 12
            y = today.year + delta_y
        else:
            # return the current month end if go back to far
            m = today.month + 1
            y = today.year

        next_month_begin = date(y, m, 1)
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
