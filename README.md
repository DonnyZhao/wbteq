# Wrapper for Teradata BTEQ Command

**BTEQ** is a Teradata utility for execute BTEQ command, it supports read value from envrionment, but only for Unix/Linux platform. I could find a way to ask **BTEQ** to read %VAR% from Windows platform.


The main purpose for this **wbteq** is to define variables in the bteq scripts.


## Sample wbteq script
```sql
-- file name : sample_bteq.sql
var1 = abc
var2 = customers

-- following are normal bteq script
.login someurl.com/userid,{password};

select column from {var2} where name = '{var1}';
```

```batch
C:\>wbteq sample_bteq.sql
```
