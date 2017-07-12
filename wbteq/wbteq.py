# coding=utf-8
#!/usr/bin/env python

import argparse
import sys
import os
from datetime import datetime
import os.path
import re
from . import __version__
from io import TextIOWrapper

class BTEQTemplate:
    def __init__(self,fd=None):
        if not isinstance(fd, TextIOWrapper) or fd is None:
            raise ValueError('Please give a correct text file handler')
        self._text = fd.read()
        self._param_list = re.findall(r"\{[a-zA-Z_]+?\}", self._text)

    @property
    def param_list(self):
        if len(self._param_list) > 0:
            return self._param_list
        else:
            return None



def get_parser():
    parser = argparse.ArgumentParser(description='run Teradata BTEQ on Windows')
    parser.add_argument('filename', type=str, nargs='+',
                        help='The parameterised BTEQ script file names')
    parser.add_argument('-v', '--version', help='displays the current version of wbteq',
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

    print(args)


if __name__ == '__main__':
    command_line_runner()
