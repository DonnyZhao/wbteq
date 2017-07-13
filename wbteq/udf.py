# coding=utf-8


def exec_udf(command):
    if not isinstance(command, str):
        raise TypeError('{} must be a str'.format(command))
    return command.upper()
