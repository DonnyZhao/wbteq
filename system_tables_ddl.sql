/*
	The table design for wbteq
	Author: Zhong Dai <zhongdai.au@gmail.com>
    
    Replace <your database> to the actual database name (schema), and run the whole 
    script to install tables and SPs
*/
database <your database>;

/* Required System tables */

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


/* System SPs  for easy create Jobs, Steps and Params */

REPLACE PROCEDURE WBTEQ_C_JOB( 
   	IN 	Job_Name 		varchar(30)
, 	IN  Freq	 		Char(1)
,	IN	Day_Of_Month	Integer
,	IN	Day_Of_Week		Integer
,	IN	Hour24			Integer
,	IN	Job_Owner		Varchar(10)
,	IN	Job_Owner_Email	Varchar(100)
,	OUT Message			Varchar(100)
) 

SQL SECURITY INVOKER

RESET: BEGIN

	DECLARE vMaxJobId 			INTEGER;


	DECLARE Exit HANDLER FOR SQLEXCEPTION
	BEGIN
		GET DIAGNOSTICS EXCEPTION 1 Message = MESSAGE_TEXT;
    END;
	
	Select Max(job_id) INTO vMaxJobId
	FROM <your database>.wbteq_jobs;
	
	
	INSERT INTO <your database>.wbteq_jobs Values (
		:vMaxJobId + 1
	,	:Freq
	,	:Day_Of_Month
	,	:Day_Of_Week
	,	:Hour24
	,	:Job_Name
	,	:Job_Owner
	,	:Job_Owner_Email
	,	'Y'
	,	Current_Date
	,	Current_Date
	);
	
	Set Message = 'Job ' || Job_Name || ' has been created, the ID = ' || Trim(vMaxJobId + 1);
	
END RESET;





REPLACE PROCEDURE WBTEQ_C_Step( 
   	IN 	Job_ID 			Integer
,	IN	Seq_Num			Integer
,	IN	File_Name		VARCHAR(100)
,	OUT Message			Varchar(100)
) 

SQL SECURITY INVOKER

RESET: BEGIN

	DECLARE vMaxStepId 			INTEGER;
	DECLARE vJobId				INTEGER;


	DECLARE Exit HANDLER FOR SQLEXCEPTION
	BEGIN
		GET DIAGNOSTICS EXCEPTION 1 Message = MESSAGE_TEXT;
    END;
	
	Select Job_Id INTO vJobId
	FROM <your database>.wbteq_jobs
	Where Job_Id = :Job_ID;
	
	Select Max(step_id) INTO vMaxStepId
	FROM <your database>.wbteq_steps;
	
	
	IF vJobId = Job_ID THEN
		INSERT INTO <your database>.wbteq_steps Values (
					:vMaxStepId + 1
				,	:Job_ID
				,	:Seq_Num
				,	:File_Name
				,	Current_Date
				,	Current_Date
				);
				
		Set Message = 'Step ' || File_Name || ' has been created, the ID = ' || Trim(vMaxStepId + 1);
	ELSE
		Set Message = 'JOB ID ' || Trim(Job_ID) || ' not found';
	END IF;
	
END RESET;



database <your database>;

REPLACE PROCEDURE WBTEQ_C_Param( 
   	IN 	Step_ID 		Integer
,	IN	Param_Type		Char(1)
,	IN	Param_Name		VARCHAR(50)
,	IN	Param_Value		VARCHAR(2000)
,	OUT Message			Varchar(100)
) 

SQL SECURITY INVOKER

RESET: BEGIN

	DECLARE vMaxParamId 		INTEGER;
	DECLARE vStepId				INTEGER;


	DECLARE Exit HANDLER FOR SQLEXCEPTION
	BEGIN
		GET DIAGNOSTICS EXCEPTION 1 Message = MESSAGE_TEXT;
    END;
	
	Select step_id INTO vStepId
	FROM <your database>.wbteq_steps
	Where step_id = :Step_ID;
	
	Select Max(param_id) INTO vMaxParamId
	FROM <your database>.wbteq_params;
	
	
	IF vStepId = Step_ID THEN
		INSERT INTO <your database>.wbteq_params Values (
					:vMaxParamId + 1
				,	:Step_ID
				,	:Param_Type
				,	:Param_Name
				,	:Param_Value
				,	Current_Date
				,	Current_Date
				);
				
		Set Message = 'Param ' || Param_Name || ' has been created, the ID = ' || Trim(vMaxParamId + 1);
	ELSE
		Set Message = 'STEP ID ' || Trim(Step_ID) || ' not found';
	END IF;
	
END RESET;


REPLACE PROCEDURE WBTEQ_D_Job( 
   	IN 	Job_Id 		Integer
,	OUT Message			Varchar(100)
) 

SQL SECURITY INVOKER

RESET: BEGIN

	DECLARE vJobDeleted 		INTEGER;
	DECLARE vStepDeleted		INTEGER;
	DECLARE vParampDeleted		INTEGER;


	DECLARE Exit HANDLER FOR SQLEXCEPTION
	BEGIN
		GET DIAGNOSTICS EXCEPTION 1 Message = MESSAGE_TEXT;
    END;
	
	DELETE <your database>.wbteq_params WHERE step_id IN (
		Select step_id 
		from <your database>.wbteq_steps s
		JOIN <your database>.wbteq_jobs j
		ON   s.job_Id = j.job_Id
		Where j.job_id = :Job_Id
	);
	
	SET vParampDeleted = ACTIVITY_COUNT;
	
	DELETE <your database>.wbteq_steps WHERE job_id IN (
		Select job_id 
		FROM <your database>.wbteq_jobs
		Where job_id = :Job_Id
	);
	
	SET vStepDeleted = ACTIVITY_COUNT;
	
	DELETE <your database>.wbteq_jobs WHERE job_id = :Job_Id;
	
	SET vJobDeleted = ACTIVITY_COUNT;	
	
	Set Message = 'Deleted ' || trim(vJobDeleted) || ' jobs, ' || trim(vStepDeleted) || ' steps, ' || trim(vParampDeleted) || ' params';
	
END RESET;

