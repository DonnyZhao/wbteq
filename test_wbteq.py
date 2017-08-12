#!/usr/bin/env python

"""Tests for Wbteq"""
import os
import unittest
import pyodbc
from datetime import datetime

os.environ['WBTEQ_DB_URL'] = 'DBURL'
os.environ['WBTEQ_DB_NAME'] = 'DBNAME'

from wbteq import wbteq
from wbteq import udf


class WbteqTestCase(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.today = datetime.now()
        pass

    def tearDown(self):
        pass

    def test_db_connect_string(self):
        items = wbteq.TERADATA_DSN.split(';')
        for item in items:
            value = item.split('=')[1]
            self.assertNotEqual(value, 'N/A')

    def test_check_folder_new(self):
        folder_name = os.path.join(self.cwd,'_temp_new')
        rc = wbteq._check_folder(folder_name)
        os.rmdir(folder_name)
        self.assertEqual(folder_name, rc)

    def test_check_foler_exist_error(self):
        folder_name = os.path.join(self.cwd, '_temp_')
        with open(folder_name, 'w') as f: # actually it is a file
            f.write('xxx')

        with self.assertRaises(FileExistsError):
            rc = wbteq._check_folder(folder_name)
        os.remove(folder_name)

    def test_check_folder_exist_normal(self):
        folder_name = os.path.join(self.cwd, '_temp_exist')
        os.mkdir(folder_name)
        rc = wbteq._check_folder(folder_name)
        os.rmdir(folder_name)
        self.assertEqual(folder_name, rc)

    def test_udf_1(self):
        m = self.today.strftime('%Y%m')
        self.assertEqual(m, udf.udf_call('month_end$month_key$0'))

    def test_udf_to_12(self):
        curr_m = self.today.month
        curr_y = self.today.year
        offset = 12 - curr_m + 1
        next_year = str(curr_y+1) + '0131' # yyyymmdd
        self.assertEqual(next_year, udf.udf_call('month_end$str$'+str(offset)))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(WbteqTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
