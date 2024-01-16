from os import truncate

create_parameters_table = """CREATE TABLE student_data_ods.student1.DA_PARAMETERS
(
    PARAM_NAME  VARCHAR(100) NOT NULL
        CONSTRAINT DA_PARAMETERS_PK
            PRIMARY KEY,
    PARAM_VALUE VARCHAR(100),
    TS_CREATED  TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    NOTES       VARCHAR(4000),
    PARAM_TYPE  VARCHAR(100)
)
    TABLESPACE dataplatform_ts;

COMMENT ON TABLE student_data_ods.student1.DA_PARAMETERS IS 'Parameters and variables used in the ODS packages';
COMMENT ON COLUMN student_data_ods.student1.DA_PARAMETERS.PARAM_VALUE IS 'value of parameter';
COMMENT ON COLUMN student_data_ods.student1.DA_PARAMETERS.PARAM_TYPE IS 'Intended type of value: string or number';"""

insert_into_parameters_table = """-- Initial values
-- INSERT INTO student_data_ods.student1.DA_PARAMETERS (param_name, param_value, NOTES)
-- VALUES ('semester_start_date', '27/03/2023', 'Start of semester in use DD/MM/YYYY');
-- INSERT INTO student_data_ods.student1.DA_PARAMETERS (param_name, param_value, NOTES)
-- VALUES ('semester_end_date', '15/06/2023', 'End of semester in use DD/MM/YYYY');

INSERT INTO student_data_ods.student1.DA_PARAMETERS (param_name, param_value, NOTES)
VALUES ('location_cd ', '1', 'Location Code');

INSERT INTO student_data_ods.student1.DA_PARAMETERS (param_name, param_value, NOTES)
VALUES ('avail_yr', '2022', 'Availability Year');

INSERT INTO student_data_ods.student1.DA_PARAMETERS (param_name, param_value, NOTES)
VALUES ('sprd_cd', '2', 'Study Period code');"""


create_get_param_function= """--------------------------------------------------------------------------------
-- get parameter function, returns string.
--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION student_data_ods.student1.get_param(IN pname TEXT)
    RETURNS TEXT
    LANGUAGE sql
    STABLE
AS
$$
SELECT param_value
FROM student_data_ods.student1.da_parameters
WHERE param_name = pname ;
$$;"""

create_set_param_function = """-- set parameter
-- parameter must exist
-- returns:
--  null if parameter does not exist
-- parameter name if successfull
-- example:
-- select student1.set_param('location_cd','1');

CREATE OR REPLACE FUNCTION student_data_ods.student1.set_param(pname TEXT, pvalue TEXT) RETURNS TEXT
    VOLATILE
    LANGUAGE sql
AS
$$
UPDATE student_data_ods.student1.da_parameters
SET param_value = set_param.pvalue
WHERE param_name = set_param.pname
RETURNING param_name;
$$;

ALTER FUNCTION student_data_ods.student1.set_param(pname TEXT, pvalue TEXT) OWNER TO dataplatform;"""


create_student_mv_default_function = """-- create_student_mv_default(caller_name)
--  create the materialised view from da_stdent_vw, using the existing
-- year and semester values from da_parameters table.
-- run as:
-- Input string is the identifies the caller in logs.
-- SELECT student_data_ods.student1.create_student_mv_default('SQL Test');
CREATE OR REPLACE FUNCTION student_data_ods.student1.create_student_mv_default(caller_name TEXT) RETURNS TEXT
    LANGUAGE plpgsql
AS
$$
DECLARE
    v_year     TEXT;
    v_semester TEXT;
BEGIN
    v_year := get_param('avail_yr');
    v_semester := get_param('sprd_cd');

    EXECUTE 'DROP MATERIALIZED VIEW if exists student_data_ods.student1.da_student_mv';

    EXECUTE 'CREATE MATERIALIZED VIEW student_data_ods.student1.da_student_mv
    TABLESPACE dataplatform_ts
AS
(
SELECT *
FROM student_data_ods.student1.da_student_vw
ORDER BY stu_id)';

    -- note string cat cannot use null variable - the whole string will disappear
    RETURN 'create_student_mv_default  testing: year: ' || v_year || ' semester: ' || v_semester || ' caller:' ||
           caller_name;
END ;
$$;

ALTER FUNCTION student_data_ods.student1.create_student_mv_default(caller_name TEXT) OWNER TO dataplatform;
"""


create_student_view = """--------------------------------------------------------------------------------------------------------
-- main query for cohort selection
-------------------------------------------------------------------------------------------------------

--  2022--08-29: 11:17
-- Base Query
-- update to use values from parameter table

CREATE OR REPLACE VIEW student_data_ods.student1.da_student_vw AS
(
SELECT SSP.STU_ID,
       ssp.SSP_NO,
       spk.SPK_CD,
       spk.SPK_VER_NO,
       ssp.SSP_ATT_NO,
       ssp.AVAIL_YR,                                -- Availability Year
       ssp.SPRD_CD,                                 -- Study period
       ssp.EFFCT_START_DT COURSE_COMMENCEMENT_DATE, -- Course Commencement Date
       org.ORG_UNIT_CD,                             -- Owning Org Code
       org.ORG_UNIT_NM,                             -- Owning Org Name
       stu.STU_ABOR_TSI_CD,                         -- To determine indigineous Y - Aboriginal, B - Aboriginal and TSI, T - TSI
       sdis.STU_DISAB_FG,                           -- Disability Flag
       ssp.LIAB_CAT_CD,                             -- Liability code - Used to determine Domestic or International (student type??)
       ssp.ATTNDC_MODE_CD,                          -- Attendance Mode
       ssp.LOAD_CAT_CD,                             -- Load Category is what is defined at start of course. It is not determined based on student load
       rp.END_DT,                                   -- Result publication (end of the study period)
       ss.START_DT                                  -- Study Period start date
       -- add new fields 20221102
FROM student_data_ods.student1.s1ssp_stu_spk ssp
         JOIN student_data_ods.student1.s1spk_det spk
              ON spk.spk_no = ssp.spk_no
                  AND spk.spk_ver_no = ssp.spk_ver_no
         JOIN student_data_ods.student1.S1CAT_TYPE cat ON
    spk.SPK_CAT_TYPE_CD = cat.SPK_CAT_TYPE_CD
         JOIN student_data_ods.student1.S1CYR_LOC_DT ss
              ON ss.CALDR_YR = ssp.AVAIL_YR
                  AND ss.LOCATION_CD = ssp.LOCATION_CD
                  AND ss.SPRD_CD = ssp.SPRD_CD
                  AND ss.DT_TYPE_CD = 'SS'
         JOIN student_data_ods.student1.S1CYR_LOC_DT rp
              ON rp.CALDR_YR = ssp.AVAIL_YR
                  AND rp.LOCATION_CD = ssp.LOCATION_CD
                  AND rp.SPRD_CD = ssp.SPRD_CD
                  AND rp.DT_TYPE_CD = 'RP'
         LEFT JOIN (SELECT spko.SPK_NO, spko.SPK_VER_NO, spko.ORG_UNIT_CD, so.ORG_UNIT_NM
                    FROM student_data_ods.student1.S1SPK_ORG_UNIT spko
                             LEFT JOIN (SELECT org_unit_cd, ORG_UNIT_NM
                                        FROM student_data_ods.student1.S1ORG_UNIT
                                        WHERE EXPIRY_DT = '01-JAN-1900') so
                                       ON spko.ORG_UNIT_CD = so.ORG_UNIT_CD
                    WHERE RESP_CAT_CD = 'O') org
                   ON ssp.SPK_NO = org.SPK_NO
                       AND ssp.SPK_VER_NO = org.SPK_VER_NO
         JOIN student_data_ods.student1.S1STU_DET stu
              ON ssp.stu_id = stu.STU_ID
         JOIN student_data_ods.student1.S1STU_DISABILITY sdis
              ON ssp.stu_id = sdis.STU_ID
WHERE                                                   -- rel: swap first two commented dates
--    ss.START_DT <= CURRENT_DATE    -- Study periods where the current date is between study period start and result publication
--   AND rp.START_DT >= CURRENT_DATE
    avail_yr = TO_NUMBER(student_data_ods.student1.get_param('avail_yr'), '9999') --perf problems with this TO_NUMBER(student_data_ods.student1.get_param('avail_yr'), '9999')
  AND ss.sprd_cd = student_data_ods.student1.get_param('sprd_cd')
  AND cat.SPK_CAT_LVL_CD = 'UG'                         -- Restrict to undergraduate
  AND ssp.LOCATION_CD = '1'                             -- Restrict to Bentley
  AND ssp.parent_ssp_no = ssp.ssp_no                    -- Restrict to Course
  AND ssp.SSP_STTS_CD = 'ADM'                           -- Restrict to Admitted Courses
  AND NOT EXISTS -- This will check that a pass or a fail has not occurred in a study period with a start date before the current study period
    (SELECT ssp2.stu_id
     FROM student_data_ods.student1.S1SSP_STU_SPK ssp2
              JOIN student_data_ods.student1.S1CYR_LOC_DT ss2
                   ON ss2.CALDR_YR = ssp2.AVAIL_YR
                       AND ss2.LOCATION_CD = ssp2.LOCATION_CD
                       AND ss2.SPRD_CD = ssp2.SPRD_CD
                       AND ss2.DT_TYPE_CD = 'SS'
     WHERE SSP.SSP_NO = ssp2.PARENT_SSP_NO
       AND ssp.LOCATION_CD = ssp2.LOCATION_CD
       AND ssp2.SSP_STTS_CD IN ('PASS', 'FAIL')
       AND ss2.START_DT < ss.START_DT)
    )
;"""

create_student_material_view_function = """CREATE OR REPLACE FUNCTION
    student_data_ods.student1.create_student_mv(v_year TEXT DEFAULT null,
                               v_semester TEXT DEFAULT null)
    RETURNS TEXT
    LANGUAGE 'plpgsql'
AS
$$
BEGIN

if v_year is  null and v_semester is  null
then
        --null; -- use existing parameter values
        v_year := get_param('avail_yr');
        v_semester := get_param('sprd_cd');
elseif v_year is not null and v_semester is not null
    then
     -- update parameter TABLE
        update student_data_ods.student1.da_parameters set param_value =  create_student_mv.v_year
        where param_name = 'avail_yr';

        update student_data_ods.student1.da_parameters set param_value =  create_student_mv.v_semester
        where param_name = 'sprd_cd';

        --commit;
else
    return 'Require all or no parameters';
END IF;


-- drop mview if it exists
-- recreate mview
-- note don't use refresh, this has not worked well
--
    EXECUTE 'DROP MATERIALIZED VIEW if exists student_data_ods.student1.da_student_mv';

    EXECUTE 'CREATE MATERIALIZED VIEW student_data_ods.student1.da_student_mv
    TABLESPACE dataplatform_ts
AS
(
SELECT *
FROM student_data_ods.student1.da_student_vw
ORDER BY stu_id)';

--commit;
-- note cannot use null variable - the whole string will disapear
    RETURN 'create_student_mv  testing: year: ' || v_year || ' semester: ' || v_semester;
END;
$$;"""

refresh_materialized_view = '''REFRESH MATERIALIZED VIEW student_data_ods.student1.da_student_mv'''

# create_staging_table = '''-- main table for current data
# CREATE TABLE student_data_ods.student1.da_engagement_stage_current
# (
#     student_id                       VARCHAR(10) NOT NULL
#         CONSTRAINT stu_id_pk_current
#             PRIMARY KEY,
#     availability_year                INTEGER,
#     study_period                     VARCHAR(5),
#     mobile_phone_provided_fg         VARCHAR(3),
#     late_offer_provided_fg           VARCHAR(3),
#     late_enrolment_fg                VARCHAR(3),
#     step_up_bonus_atar_fg            VARCHAR(3),
#     first_in_family_fg               VARCHAR(3),
#     tax_file_number_fg               VARCHAR(3),
#     tax_file_cert_fg                 VARCHAR(3),
#     sanctions_with_hold_fg           VARCHAR(3),
#     unique_student_identifier_fg     VARCHAR(3),
#     student_progression_agreement_fg VARCHAR(3),
#     low_socio_economic_postcode_fg   VARCHAR(3),
#     class_registration_fg            VARCHAR(3),
#     fee_payment_complete_fg          VARCHAR(3),
#     class_reg_complete_dt            VARCHAR(100),
#     first_enrolment_dt               VARCHAR(100),
#     first_offer_dt                   VARCHAR(100),
#     student_citizenship_type         VARCHAR(100),
#     attendance_mode                  VARCHAR(100),
#     course_commencement_dt           VARCHAR(100),
#     campus                           VARCHAR(100),
#     owning_org                       VARCHAR(100),
#     teaching_org                     VARCHAR(100),
#     disability_fg                    VARCHAR(3),
#     indigenous_fg                    VARCHAR(3),
#     scholarship_fg                   VARCHAR(10),  -- check filed contents size
#     sponsorship_fg                   VARCHAR(3),
#     late_offer_acceptance_fg         VARCHAR(3),
#     offer_acceptance_dt              VARCHAR(100),
#     stu_postcode                     VARCHAR(20),
#     start_dt                         VARCHAR(100), -- min package start date
#     end_dt                           VARCHAR(100), -- max package end date
#     -- row insert date
#     ts_insert                        VARCHAR(100) DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS')
# )
#     TABLESPACE dataplatform_ts;'''

# alter_staging_table = '''ALTER TABLE student_data_ods.student1.da_engagement_stage_current
#     OWNER TO dataplatform'''

# grant_select_on_staging_table_to_test_user = '''GRANT SELECT ON student_data_ods.student1.da_engagement_stage_current TO test_user'''

# grant_select_on_staging_table_to_dataplatform_read = '''GRANT SELECT ON student_data_ods.student1.da_engagement_stage_current TO dataplatform_read'''



#---------------------------------------------------------------------Ingestion-------------------------------------------------------------
truncate_staging_table = '''TRUNCATE student_data_ods.student1.da_engagement_stage_current'''

select_staging_table = ''' select *  from student_data_ods.student1.da_engagement_stage_current'''

select_staging_table_ordered = """ 
SELECT student_id,
       availability_year,
       study_period,
       mobile_phone_provided_fg,
       late_offer_provided_fg,
       late_enrolment_fg,
       step_up_bonus_atar_fg,
       first_in_family_fg,
       tax_file_number_fg,
       tax_file_cert_fg,
       sanctions_with_hold_fg,
       unique_student_identifier_fg,
       student_progression_agreement_fg,
       low_socio_economic_postcode_fg,
       class_registration_fg,
       fee_payment_complete_fg,
       class_reg_complete_dt,
       first_enrolment_dt,
       first_offer_dt,
       student_citizenship_type,
       attendance_mode,
       course_commencement_dt,
       campus,
       owning_org,
       teaching_org,
       disability_fg,
       indigenous_fg,
       scholarship_fg,
       sponsorship_fg,
       late_offer_acceptance_fg,
       offer_acceptance_dt,
       student_postcode,
       start_dt,
       end_dt,
       ts_insert
FROM student_data_ods.student1.da_engagement_stage_current order by student_id"""

insert_staging_table_distinct_id = '''-- set up student id's to use in the da table
-- put these id's into the table if not there already
-- note this is using unique code
-- theis may need to be adapted later to use stu_id & ssp for students in multiple courses
--FIELD: student_id
INSERT INTO student_data_ods.student1.da_engagement_stage_current (student_id)
    (SELECT DISTINCT (stu_id)
     FROM student_data_ods.student1.da_student_mv ss
     WHERE ss.stu_id NOT IN (SELECT student_id FROM student_data_ods.student1.da_engagement_stage_current dar2))
'''

update_staging_table_set_some_fields = '''-- set some fields from main statement
-- FIELD: attendance_mode, owning_org, indigenous_fg, disability_fg, course_commencement_dt, availability_year,
--      study_period

WITH t AS
         (SELECT stu_id,
                 ATTNDC_MODE_CD,
                 ORG_UNIT_NM,
                 CASE WHEN STU_ABOR_TSI_CD IN ('Y', 'B', 'T') THEN 'Yes' ELSE 'No' END stu_abor_tst_fg,
                 STU_DISAB_FG,
                 COURSE_COMMENCEMENT_DATE,
                 avail_yr,
                 sprd_cd -- study period
          FROM student_data_ods.student1.da_student_mv mv)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET (attendance_mode, owning_org, indigenous_fg, disability_fg, course_commencement_dt, availability_year,
     study_period) =
        (t.ATTNDC_MODE_CD,
         t.ORG_UNIT_NM,
         t.stu_abor_tst_fg,
         t.STU_DISAB_FG,
         TO_CHAR(t.COURSE_COMMENCEMENT_DATE,'YYYY-MM-DD'),
         t.AVAIL_YR,
         t.SPRD_CD)
FROM t
WHERE da.student_id = t.stu_id;'''

update_staging_table_set_start_and_end_dates = """-- FIELD start_dt, end_dt, just used for other calculations
WITH t AS
         (SELECT stu_id, MIN(start_dt) min_start_dt, MAX(end_dt) max_end_dt
FROM student_data_ods.student1.da_student_mv
GROUP BY stu_id
ORDER BY stu_id
)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET (start_dt, end_dt) = (TO_CHAR(t.min_start_dt, 'YYYY-MM-DD'), TO_CHAR(t.max_end_dt, 'YYYY-MM-DD'))
FROM t
WHERE da.STUDENT_ID = t.stu_id"""


update_staging_table_contact_ph_yes = '''-- FIELD first_offer_dt
-- To obtain Mobile number
-- Link on stu_id = stu_id
-- rel note just mobile phone ?
-- set if exists
--
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET mobile_phone_provided_fg = 'Yes'
WHERE student_id IN
      (SELECT stu_id
       FROM student_data_ods.student1.s1stu_phone sp
       WHERE phone_type_cd = '$MOB')'''

update_staging_table_contact_ph_to_no_if_null = '''-- set to no where not recorded
UPDATE student_data_ods.student1.da_engagement_stage_current
SET mobile_phone_provided_fg = 'No'
WHERE mobile_phone_provided_fg IS NULL;'''

update_staging_table_set_first_offer_date = '''-- FIELD: offer_acceptance_date
-- To determine the first date of offer
-- get min effective start date
-- NOTE should this be max start date?

WITH t AS
         (SELECT dmv.stu_id, MIN(sh.effct_start_dt) min_start, MAX(sh.effct_start_dt) max_start
          FROM student_data_ods.student1.S1SSP_STTS_HIST sh,
               student_data_ods.student1.da_student_mv dmv
          WHERE sh.SSP_STTS_CD = 'OFF'
            AND sh.ssp_no = dmv.ssp_no
          GROUP BY dmv.stu_id)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET first_offer_dt = TO_CHAR(t.min_start,'YYYY-MM-DD')
FROM t
WHERE da.STUDENT_ID = t.stu_id
;'''

update_staging_table_set_offer_acceptance_date = '''-- FIELD: offer_acceptance_date
-- To determine when student was first admitted (accepted their offer)
-- Link on ssp_no = ssp_no
-- rel: we don't seem to use offer accepted.

WITH t AS
         (SELECT dmv.stu_id, MIN(sh.effct_start_dt) min_start, MAX(sh.effct_start_dt) max_start
          FROM student_data_ods.student1.S1SSP_STTS_HIST sh,
               student_data_ods.student1.da_student_mv dmv
          WHERE sh.SSP_STTS_CD = 'ADM'
            AND sh.stu_id = dmv.stu_id
          GROUP BY dmv.stu_id)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET offer_acceptance_dt = TO_CHAR(t.min_start,'YYYY-MM-DD')
FROM t
WHERE t.stu_id = da.student_id'''

update_staging_table_set_first_enrolment_date = '''-- FIELD: first_enrolment_dt
-- To determine when student first enrolled
-- link on ssp_no = parent_ssp_no
-- This logic will only work if you are looking at this data during the study period
-- It will not work retrospectively for previous study period because the units will no longer have a status of Enrolled. (they will be passed or failed)
-- REL: now doing this with history table

-- try this:
-- To determine when student first enrolled
-- Checking history table will allow to run retrospectively (if student is no longer enrolled they have passed failed WD)
-- link on ssp_no = parent_ssp_no

WITH t AS
         (SELECT mv.stu_id, MIN(sh.EFFCT_START_DT) FIRST_ENR
          FROM student_data_ods.student1.S1SSP_STTS_HIST sh,
               student_data_ods.student1.S1SSP_STU_SPK ssp,
               student_data_ods.student1.da_student_mv mv
          WHERE sh.SSP_NO = ssp.SSP_NO
            AND sh.SSP_STTS_CD = 'ENR'
            AND mv.ssp_no = ssp.parent_ssp_no
          GROUP BY mv.stu_id)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET first_enrolment_dt = TO_CHAR(t.FIRST_ENR,'YYYY-MM-DD')
FROM t
WHERE t.STU_ID = da.student_id'''

update_staging_table_set_tax_file_number = '''-- FIELD tax_file_number_fg
-- To determine Tax File Number. This column is encrypted backend. You may need to do a data in column query to determine if its been entered. length(TFN) > 1
-- Link on ssp_no = ssp_no

WITH t AS (SELECT stu_id,
                  CASE WHEN LENGTH(TFN) > 1 THEN 'Yes' ELSE 'No' END TFN
           FROM student_data_ods.student1.S1SSP_GAF_DTL)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET tax_file_number_fg = t.tfn
FROM t
WHERE t.STU_ID = da.student_id
'''

update_staging_table_set_tax_file_number_to_no_if_is_null = '''-- set to No if it's not found?
-- # TODO: 11/4/22 a182026k:  check this

UPDATE student_data_ods.student1.da_engagement_stage_current da
SET tax_file_number_fg = 'No'
WHERE tax_file_number_fg IS NULL'''

update_staging_table_set_tax_file_cert_fg = '''-- To determine tax_file_cert_fg (student has a CP sanction)
-- currently not using this
-- use: if tax_file_number_fg is Yes, this is No
-- get start/end date from da_student_mv

-- this i currently not selecting anything because it's the future


WITH t AS (SELECT ss.stu_id, 'Yes' TAX_FILE_CERT_FG
FROM student_data_ods.student1.S1STU_SANCTION ss
WHERE SANCT_TYPE_CD = 'CP'
  AND STU_SANCT_EFFCT_DT <=(select max(end_dt) from student_data_ods.student1.da_student_mv mv where mv.stu_id = ss.stu_id)  --rp.END_DATE -- end of semester
  AND (STU_SANCT_END_DT >  (select min(start_dt) from student_data_ods.student1.da_student_mv mv where mv.stu_id = ss.stu_id) --ss.START_DATE --start of semester
    OR STU_SANCT_END_DT = '01-JAN-1900'))
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET tax_file_cert_fg = t.TAX_FILE_CERT_FG
FROM t
WHERE t.STU_ID = da.student_id'''

update_staging_table_set_tax_file_cert_fg_to_no_if_tax_file_number_fg_is_yes = '''UPDATE student_data_ods.student1.da_engagement_stage_current da
SET tax_file_cert_fg = 'No'
WHERE student_id IN (SELECT student_id FROM student_data_ods.student1.da_engagement_stage_current WHERE tax_file_number_fg = 'Yes')'''

update_staging_table_set_tax_file_cert_fg_to_no_if_is_null = '''UPDATE student_data_ods.student1.da_engagement_stage_current da
SET tax_file_cert_fg = 'No'
WHERE tax_file_cert_fg IS NULL'''

update_staging_table_set_unique_student_identifier_fg_to_yes = '''UPDATE student_data_ods.student1.da_engagement_stage_current da
SET unique_student_identifier_fg = 'Yes'
WHERE student_id IN (SELECT stu_id
                 FROM student_data_ods.student1.S1STU_ALT_ID sai
                 WHERE STU_ALT_ID_TYPE_CD = 'USI'
                   AND LENGTH(stu_alt_id) > 0)'''

update_staging_table_set_unique_student_identifier_fg_to_no_if_is_null = '''UPDATE student_data_ods.student1.da_engagement_stage_current da
SET unique_student_identifier_fg = 'No'
WHERE unique_student_identifier_fg IS NULL'''

update_staging_table_set_step_up_bonus = '''
-- To determine Step up bonus
-- link on stu_id = student_id

WITH t AS (SELECT stu_id, 'Yes' STEP_UP_BONUS
           FROM student_data_ods.student1.S1STU_OTH_SCORE SC
           WHERE SC.PREV_SCORE_TYPE_CD IN ('SIP', 'SIB'))
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET step_up_bonus_atar_fg = t.STEP_UP_BONUS
FROM t
WHERE t.STU_ID = da.student_id'''

update_staging_table_set_step_up_bonus_to_No_if_is_null = '''UPDATE student_data_ods.student1.da_engagement_stage_current da
SET step_up_bonus_atar_fg = 'No'
WHERE step_up_bonus_atar_fg IS NULL'''

update_staging_table_set_first_in_family = '''-- FIELD: first_in_family_fg
-- To determine first in family

WITH t AS (SELECT stu_id,
                  CASE WHEN guardian_hea_cd IN ('PG', 'BACH', 'OTH') THEN 'No' ELSE 'Yes' END FIRST_IN_FAMILY
           FROM student_data_ods.student1.S1STU_GUARDIAN)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET first_in_family_fg = t.FIRST_IN_FAMILY
FROM t
WHERE t.STU_ID = da.student_id'''

update_staging_table_set_first_in_family_to_No_if_is_null = '''UPDATE student_data_ods.student1.da_engagement_stage_current
SET first_in_family_fg = 'No'
WHERE first_in_family_fg IS NULL;'''

update_staging_table_set_sanctions_with_hold = '''-- FIELD: sanctions_with_hold_fg
-- To determine Sanction with Holds
-- link on stu_id = stu_id
-- rel: modify this for during the historical semester
-- chad: that logic should work using semester 1 start date and result publication date hard coded.
-- commented out line below. if the sanction started before the end of semester and ended anytime after star of semester
-- or is not ended it was in pace at some stage of the semester

UPDATE student_data_ods.student1.da_engagement_stage_current
SET sanctions_with_hold_fg = 'Yes'
WHERE student_id IN (SELECT stu_id
                     FROM student_data_ods.student1.S1STU_SANCTION sct
                     WHERE sct.STU_SANCT_EFFCT_DT <= CURRENT_DATE -- end of semester
                       AND (sct.STU_SANCT_END_DT > CURRENT_DATE --start of semester
                         OR sct.STU_SANCT_END_DT = '01-JAN-1900')
                       -- and sct.stu_sanct_end_dt < to_date('25/07/2022','DD/MM/YYYY') -- rel add this
                       AND EXISTS(SELECT 1
                                  FROM student_data_ods.student1.S1SYS_SCT_HLD_DTL sh
                                  WHERE sct.SANCT_TYPE_CD = sh.SANCT_TYPE_CD))'''


update_staging_table_set_sanctions_with_hold_to_No_if_is_null = '''UPDATE student_data_ods.student1.da_engagement_stage_current
SET sanctions_with_hold_fg = 'No'
WHERE sanctions_with_hold_fg IS NULL'''

update_staging_table_set_progression_agreement = '''-- FILED: stu_progression_agreement_fg
-- To determine Student Progression Agreement

UPDATE student_data_ods.student1.da_engagement_stage_current
SET student_progression_agreement_fg = 'Yes'
WHERE student_id IN (SELECT stu_id
                 FROM student_data_ods.student1.s1agm_agreement_det ag
                 WHERE ag.agree_type_cd = 'SPA'         -- Type SPA
                   AND ag.ACTUAL_END_DT = '01-JAN-1900' -- not end dated
                   AND ag.AGREE_STTS_CD = '$AC')'''

update_staging_table_set_progression_agreement_to_No_if_is_null = '''UPDATE student_data_ods.student1.da_engagement_stage_current
SET student_progression_agreement_fg = 'No'
WHERE student_progression_agreement_fg IS NULL'''

update_staging_table_set_post_code = '''-- FIELD: stu_pcode
-- To determine Low Socio Economic Postcodes
-- This is not specifically stored in S1. We have postcode in the address but not if low socio economic

-- Student Permanent Address pcode
WITH t AS
         (SELECT stu_id, STU_PCODE
          FROM  student_data_ods.student1.S1STU_ADDR
          WHERE STU_ADDR_TYPE_CD = 'P')
UPDATE  student_data_ods.student1.da_engagement_stage_current da
SET student_postcode = t.stu_pcode
FROM t
WHERE da.student_id = t.stu_id'''

update_staging_table_set_post_code_to_NA_if_is_null = '''UPDATE  student_data_ods.student1.da_engagement_stage_current
SET student_postcode = 'NA'
WHERE student_postcode IS NULL'''

update_staging_table_set_low_socio_economic_postcode = '''-- To determine Low Socio Economic Postcodes
-- This is not specifically stored in S1. We have postcode in the address but not if low socio economic
-- link on stu_id = stu_id
-- # TODO:  no postcode should set to NA
WITH t AS (SELECT stu_id,
                  CASE
                      WHEN STU_PCODE IN
                           ('2306', '2559', '2807', '3026', '3200', '3214', '3588', '4303', '4383', '4662', '4712',
                            '4713', '4828', '4830', '5113', '5279', '5552',
                            '5601', '6218', '6434', '7016', '7253', '7261', '7469', '2326', '2327', '2341', '2409',
                            '2502', '2645', '2770', '2847', '4114', '4714',
                            '5112', '5164', '5260', '5332', '5608', '5722', '6067', '6165', '6436', '6560', '6718',
                            '6760', '7019', '7030', '7257', '854', '2334',
                            '2369', '2730', '2848', '3047', '3335', '3580', '4132', '4421', '4694', '4695', '4739',
                            '4804', '4857', '5108', '5237', '5321', '6431',
                            '6442', '7027', '7140', '7214', '7467', '7470', '852', '2426', '2466', '2470', '2506',
                            '2878', '3177', '3595', '4376', '4508', '4580',
                            '4659', '4673', '4859', '5115', '5253', '5421', '5540', '5550', '5577', '6042', '6225',
                            '6511', '7213', '7260', '2163', '2262', '2336',
                            '2382', '2528', '2551', '2663', '2797', '2845', '3048', '3061', '3840', '4614', '4798',
                            '5017', '5107', '5166', '5346', '5356', '5556',
                            '5734', '6432', '6762', '7011', '7305', '2166', '2263', '2278', '2286', '2440', '2564',
                            '2760', '3472', '4077', '4219', '4401', '4510',
                            '4515', '4671', '4674', '4678', '4737', '4854', '5094', '5160', '6429', '6518', '7010',
                            '7248', '822', '2325', '2641', '2790', '2834',
                            '2842', '3075', '3465', '3556', '3890', '3915', '4311', '4373', '4517', '4605', '4615',
                            '4627', '4756', '4805', '4888', '6215', '6514',
                            '6799', '7182', '7270', '2322', '2346', '2361', '2505', '2555', '2702', '3021', '3074',
                            '3865', '4008', '4660', '4676', '4861', '4871',
                            '4890', '5114', '5163', '5341', '5700', '6043', '6214', '6224', '6770', '7177', '7330',
                            '841', '2168', '2333', '2395', '2460', '2643',
                            '2865', '2880', '3485', '3825', '4021', '4184', '4301', '4342', '4427', '4650', '4735',
                            '4738', '4757', '4849', '5110', '5280', '5290',
                            '6109', '7322', '847', '862', '2427', '2443', '2462', '2706', '3338', '3356', '3639',
                            '3984', '4341', '4606', '4677', '4806', '4808',
                            '4821', '5320', '5422', '6167', '6209', '6321', '7210', '7216', '7264', '7320', '872',
                            '2312', '2403', '2423', '2449', '2472', '2836',
                            '2852', '2868', '3250', '3687', '4133', '4400', '4506', '4799', '4816', '5268', '5277',
                            '5501', '5603', '5724', '6220', '7172', '7184',
                            '7468', '840', '2165', '2319', '2846', '3355', '3380', '3520', '3621', '3902', '3940',
                            '4304', '4313', '4365', '4377', '4387', '4621',
                            '4745', '5013', '5322', '6168', '6232', '6443', '7301', '7310', '2324', '2328', '2371',
                            '2425', '2447', '2471', '2703', '2722', '2787',
                            '2799', '2835', '3337', '3728', '3856', '3987', '4343', '4626', '4699', '4860', '5109',
                            '5121', '5238', '6208', '6640', '7300', '2359',
                            '2429', '3373', '3427', '3496', '3618', '3629', '3644', '3660', '3976', '4205', '4370',
                            '4570', '4754', '4800', '4809', '4850', '4880',
                            '4891', '4895', '5344', '5410', '5581', '6258', '6765', '2353', '2430', '2448', '2463',
                            '2485', '2653', '2700', '4131', '4207', '4357',
                            '4511', '4670', '4717', '4820', '4876', '5168', '5345', '5495', '5558', '6041', '6123',
                            '6317', '6620', '7315', '7325', '2174', '2380',
                            '2541', '2573', '2794', '3022', '3304', '3505', '3641', '3858', '3919', '3981', '3995',
                            '4807', '4829', '5330', '5583', '5602', '5723',
                            '5732', '6037', '7117', '7186', '7290', '7306', '2455', '2527', '2530', '2646', '2720',
                            '2747', '3219', '3305', '3980', '4118', '4600',
                            '4751', '4753', '5012', '5343', '5354', '5554', '6254', '6401', '6516', '6740', '7120',
                            '7190', '7263', '7302', '2284', '2347', '2352',
                            '2428', '2476', '2633', '2651', '2717', '3020', '3201', '3311', '3414', '3612', '3658',
                            '3842', '3903', '4125', '4372', '4625', '4715',
                            '4741', '4815', '5582', '6537', '2164', '2307', '2330', '2343', '2360', '2473', '2563',
                            '2671', '2705', '2827', '3251', '3377', '3478',
                            '3517', '3594', '3737', '4655', '4824', '4887', '5162', '5165', '5606', '6367', '6728',
                            '7116', '2259', '2587', '2647', '3423', '3713',
                            '3909', '4285', '4305', '4375', '4501', '4707', '4742', '4874', '5116', '5161', '5460',
                            '5571', '6058', '6064', '6207', '6318', '6410',
                            '6440', '7307', '7321', '846', '2177', '2431', '2446', '2475', '2486', '2666', '2680',
                            '2839', '3971', '4110', '4124', '4280', '4344',
                            '4354', '4716', '4858', '5084', '5372', '6210', '6638', '6705', '7173', '7179', '7259',
                            '2400', '2452', '2560', '2590', '2681', '2829',
                            '3171', '3174', '3175', '3816', '4346', '4385', '4410', '4505', '4613', '4746', '5098',
                            '5304', '5355', '5373', '5374', '5473', '6716',
                            '6754', '7262', '2566', '2594', '2648', '2675', '2870', '3254', '3370', '3518', '3521',
                            '3555', '3562', '3570', '3623', '3803', '3939',
                            '3977', '4022', '4371', '4472', '4514', '4702', '4718', '5520', '5690', '6720', '2281',
                            '2338', '2404', '2469', '2536', '2539', '2737',
                            '3636', '3965', '3991', '4312', '4356', '4405', '4869', '5088', '6110', '6112', '6227',
                            '6229', '6315', '6530', '7211', '7215', '7254',
                            '2179', '2370', '2388', '2396', '2465', '2766', '3019', '3330', '3500', '3523', '3549',
                            '3579', '3620', '3624', '3630', '3882', '4415',
                            '4481', '5096', '5174', '5462', '5502', '5710', '6271', '7026') THEN 'Yes'
                      ELSE 'No' END LOW_SOCIO
           FROM student_data_ods.student1.S1STU_ADDR
           WHERE STU_ADDR_TYPE_CD = 'P')
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET low_socio_economic_postcode_fg = t.LOW_SOCIO
FROM t
WHERE da.student_id = t.stu_id'''

update_staging_table_set_low_socio_economic_postcode_to_NA_if_is_empty = '''-- revert NA pcode to NA flag, no postcode is usualy a blank character

UPDATE student_data_ods.student1.da_engagement_stage_current
SET low_socio_economic_postcode_fg = 'NA'
WHERE student_postcode = ' ' '''

update_staging_table_set_student_type = '''-- FIELD: stu_type
-- To determine Student Type (Domestic / International)

WITH t AS (SELECT stu_id,
                  CASE
                      WHEN STU_CITIZEN_CD IN ('4', '5') -- 4 and 5 are international others are considered domestic
                          THEN 'International'
                      ELSE 'Domestic'
                      END STUDENT_TYPE
           FROM student_data_ods.student1.s1stu_det)
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET student_citizenship_type = t.student_type
FROM t
WHERE da.STUDENT_ID = t.stu_id'''

update_staging_table_set_class_registeration = """-- FIELD: class_registration_fg
-- To determine if student is class registered
-- Link ssp_no to parent_ssp_no
-- rel: I think this is current classes


UPDATE student_data_ods.student1.da_engagement_stage_current da
SET class_registration_fg = 'Yes'
WHERE student_id IN (SELECT cr.stu_id
                 FROM student_data_ods.student1.s1ssp_stu_spk ssp
                          JOIN student_data_ods.student1.S1SSP_CLASS_REGN cr
                               ON ssp.ssp_no = cr.SSP_NO
                 WHERE CLASS_REGN_STTS_CD = 'R')"""

update_staging_table_set_class_registeration_to_No_if_is_null = """UPDATE student_data_ods.student1.da_engagement_stage_current da
SET class_registration_fg = 'No'
WHERE class_registration_fg IS NULL
"""

update_staging_table_set_late_enrolment = """
-- FIELD: late_enrolment_fg
--  after start of semester + 7

UPDATE student_data_ods.student1.da_engagement_stage_current da
SET late_enrolment_fg = 'Yes'
WHERE student_id IN (SELECT student_id
                 FROM student_data_ods.student1.da_engagement_stage_current
                 WHERE TO_DATE(da.first_enrolment_dt, 'YYYY-MM-DD') > date(START_DT) + 7) -- convert timestamep to date"""

update_staging_table_set_late_enrolment_to_No_if_is_null = """UPDATE student_data_ods.student1.da_engagement_stage_current da
SET late_enrolment_fg = 'No'
WHERE late_enrolment_fg IS NULL"""

update_staging_table_set_late_offer_provided = """-- FIELD: late_offer_provided_fg : after start of semester
--late offer : after start of semester
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET late_offer_provided_fg = 'Yes'
WHERE student_id IN (SELECT student_id
                 FROM student_data_ods.student1.da_engagement_stage_current
                 WHERE TO_DATE(da_engagement_stage_current.first_offer_dt, 'YYYY-MM-DD') > TO_DATE(START_DT, 'YYYY-MM-DDD'))"""

update_staging_table_set_late_offer_provided_to_No_if_is_null = """UPDATE student_data_ods.student1.da_engagement_stage_current da
SET late_offer_provided_fg = 'No'
WHERE late_offer_provided_fg IS NULL""" 

update_staging_table_set_late_offer_acceptance = """UPDATE student_data_ods.student1.da_engagement_stage_current da
SET late_offer_acceptance_fg = 'Yes'
WHERE student_id IN (SELECT student_id
                 FROM student_data_ods.student1.da_engagement_stage_current
                 WHERE TO_DATE(offer_acceptance_dt, 'YYYY-MM-DD') > (TO_DATE('25/07/2022', 'DD/MM/YYYY') + 7))"""

update_staging_table_set_late_offer_acceptance_to_No_if_is_null = """UPDATE student_data_ods.student1.da_engagement_stage_current da
SET late_offer_acceptance_fg = 'No'
WHERE late_offer_acceptance_fg IS NULL"""

update_staging_table_set_campus = """UPDATE student_data_ods.student1.da_engagement_stage_current
SET campus ='Bentley'"""


update_staging_table_set_fee_payment_complete_fg = """-- FIELD: fee_payment_complete_fg

-- Note: statement supplied is fee payment complete
-- Fee Payment incomplete
-- link ssp_no = ssp.parent_ssp_no
-- This will obtain students that have a current unit that has a fee with a status of unpaid, overdue - census or overdue due date
UPDATE  student_data_ods.student1.da_engagement_stage_current da
SET fee_payment_complete_fg = 'No'
WHERE student_id IN
      (SELECT sm.stu_id --  FEE_PAYMENT_INCOMPLETE
       FROM  student_data_ods.student1.S1STU_FEES fee
                JOIN  student_data_ods.student1.s1ssp_stu_spk ssp
                     ON ssp.ssp_no = fee.ssp_no
                JOIN  student_data_ods.student1.S1CYR_LOC_DT ss
                     ON ss.CALDR_YR = ssp.AVAIL_YR
                         AND ss.LOCATION_CD = ssp.LOCATION_CD
                         AND ss.SPRD_CD = ssp.SPRD_CD
                         AND ss.DT_TYPE_CD = 'SS'
                JOIN  student_data_ods.student1.S1CYR_LOC_DT rp
                     ON rp.CALDR_YR = ssp.AVAIL_YR
                         AND rp.LOCATION_CD = ssp.LOCATION_CD
                         AND rp.SPRD_CD = ssp.SPRD_CD
                         AND rp.DT_TYPE_CD = 'RP'
                JOIN  student_data_ods.student1.da_student_mv sm
                     ON sm.ssp_no = ssp.parent_ssp_no
       WHERE SSP_FEE_DBT_STTS IN ('UP', 'OC', 'OD')
         AND CURRENT_DATE BETWEEN sm.START_DT AND sm.END_DT);

UPDATE student_data_ods.student1.da_engagement_stage_current da
SET fee_payment_complete_fg = 'Yes'
WHERE fee_payment_complete_fg IS NULL;"""

update_staging_table_set_sponsorship_fg = """-- FIELD: sponsorship_fg
UPDATE student_data_ods.student1.da_engagement_stage_current da
SET sponsorship_fg = 'Yes'
WHERE student_id IN
      (SELECT sp.stu_id
       FROM student_data_ods.student1.s1stu_sponsor sp
                JOIN student_data_ods.student1.da_student_mv sm
                     ON sm.ssp_no = sp.ssp_no
       WHERE sp.stu_spnsr_stts_cd = 'C'
         AND (CURRENT_DATE BETWEEN sp.stu_spnsr_strt_dt
                  AND sp.stu_spnsr_end_dt
           OR sp.stu_spnsr_end_dt = '1-JAN-1900'))
;

UPDATE student_data_ods.student1.da_engagement_stage_current da
SET sponsorship_fg = 'No'
WHERE sponsorship_fg IS NULL;"""

update_staging_table_set_scholarship_fg = """-- FIELD: scholarship_fg
update student_data_ods.student1.da_engagement_stage_current da
set scholarship_fg = 'Yes'
where student_id in
(SELECT rw.stu_id
FROM student_data_ods.student1.S1RSP_STU_REWARD_DET rw
         JOIN student_data_ods.student1.S1RSP_STU_REWARD_SSP rssp
              ON rw.STU_REWARD_ID = rssp.STU_REWARD_ID
    join student_data_ods.student1.da_student_mv sm
        on rssp.ssp_no = sm.ssp_no
WHERE STU_REWARD_STATUS_CD = '$A')
;

UPDATE student_data_ods.student1.da_engagement_stage_current da
SET scholarship_fg = 'No'
WHERE scholarship_fg IS NULL;
"""

update_staging_table_set_disability_fg = """-- FIELD: disability_fg
UPDATE student_data_ods.student1.da_engagement_stage_current
SET disability_fg ='Yes'
WHERE disability_fg = 'Y'
;

UPDATE student_data_ods.student1.da_engagement_stage_current
SET disability_fg ='No'
WHERE disability_fg = 'N' """