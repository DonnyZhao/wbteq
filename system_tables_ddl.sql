/*
	The table design for wbteq
	Author: Zhong Dai <zhongdai.au@gmail.com>
*/
database <your database>;
drop table wbteq_jobs;
create table wbteq_jobs
(
	job_id 				integer not null
,	freq 				char(1) not null compress ('M','W','D')
,	day_of_month		integer null
,	day_of_week			integer null
,	hour24				integer
,	job_name			varchar(30) not null
,	job_owner			varchar(10) not null
,	job_owner_email		varchar(100) not null
,	is_enabled 			char(1) not null compress ('Y','N')
,	created_at			date not null
,	updated_at			date not null
) unique primary index (job_id);

drop table wbteq_steps;
create table wbteq_steps
(
	step_id 			integer not null
,	job_id 				integer not null
,	seq_num				decimal(5,2) not null
,	filename			varchar(100) not null
,	created_at			date
,	updated_at			date
) unique primary index (step_id);


drop table wbteq_params;
create table wbteq_params
(
	param_id  			integer not null
,	step_id  			integer not null
,	param_type 			char(1) not null compress ('D','P','S') -- Direct / Python / SQL
,	param_name			varchar(50) not null
,	param_value			varchar(2000) not null
,	created_at			date
,	updated_at			date
) unique primary index (param_id);
