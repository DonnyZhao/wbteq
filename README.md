# Wrapper for Teradata BTEQ Command

**BTEQ** is a Teradata utility for execute BTEQ command, it supports read value from environment, but only for Unix/Linux platform. I could **not** find a way to ask **BTEQ** to read %VAR% from Windows platform.


## Design
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
- param_type ('D','P','S') D - Direct / Python / SQL
- param_name
- param_value

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
