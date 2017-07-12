# coding=utf-8
#!/usr/bin/env python

import argparse
import sys
import os
from datetime import datetime
import os.path
import re
from . import __version__


class BTEQ:
    def __init__(self, filename=None, init_flag=False, exec_flag=False, prefix='wbteq_'):
        if filename is None:
            raise ValueError('Please give a file name as input')
        self.filename = filename
        self.init_flag = init_flag
        self.exec_flag = exec_flag
        self.prefix = prefix

        with open(filename) as f:
            full_text = f.read()

        self.param_list = re.findall(r"\{.+?\}", full_text)


    def _parse(self):
        """
        Get all ENVs
        """
        param = {}
        for k, v in os.environ.items():
            if k.lower().startswith(self.prefix):
                param[k] = v
        return param

    def __repr__(self):
        if self.init_flag is True:
            return 'Inital BTEQ <{}>'.format(self.filename)
        else:
            return 'Executable BTEQ <{}>'.format(self.filename)

    def __str__(self):
        return self.__repr__()

    def run(self):
        if self.init_flag is True:
            print('Setup the ENV variables {}'.format(self.filename))
        else:
            print('Run the BTEQ scrip {}'.format(self.filename))


def get_parser():
    parser = argparse.ArgumentParser(description='run Teradata BTEQ on Windows')
    parser.add_argument('filename', type=str,
                        help='The parameterised BTEQ script file name')
    parser.add_argument('-v', '--version', help='displays the current version of wbteq',
                        action='store_true')
    parser.add_argument('-i','--init', help='this initial step to assign env variables',
                        action='store_true')
    parser.add_argument('-e','--exec', help='execute the BTEQ command',
                        action='store_true')
    parser.add_argument('-p','--prefix', help='prefix for the ENVs', default='wbteq_',
                        action='store')
    return parser


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    b = BTEQ(args['filename'],
             args['init'],
             args['exec'],
             args['prefix'])
    b.run()


if __name__ == '__main__':
    command_line_runner()
