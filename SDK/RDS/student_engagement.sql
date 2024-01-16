SET SEARCH_PATH = 'student1';
--------------------------------------------------------------------------------------------------------
-- new main query
-------------------------------------------------------------------------------------------------------

--  2022--08-29: 11:17
-- Base Query
-- modified for ss.sprd_cd = '1'		study period 1
create view da_student_vw as
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
       ssp.LOAD_CAT_CD                              -- Load Category is what is defined at start of course. It is not determined based on student load
FROM s1ssp_stu_spk ssp
         JOIN s1spk_det spk
              ON spk.spk_no = ssp.spk_no
                  AND spk.spk_ver_no = ssp.spk_ver_no
         JOIN S1CAT_TYPE cat ON
    spk.SPK_CAT_TYPE_CD = cat.SPK_CAT_TYPE_CD
         JOIN S1CYR_LOC_DT ss
              ON ss.CALDR_YR = ssp.AVAIL_YR
                  AND ss.LOCATION_CD = ssp.LOCATION_CD
                  AND ss.SPRD_CD = ssp.SPRD_CD
                  AND ss.DT_TYPE_CD = 'SS'
         JOIN S1CYR_LOC_DT rp
              ON rp.CALDR_YR = ssp.AVAIL_YR
                  AND rp.LOCATION_CD = ssp.LOCATION_CD
                  AND rp.SPRD_CD = ssp.SPRD_CD
                  AND rp.DT_TYPE_CD = 'RP'
         LEFT JOIN (SELECT spko.SPK_NO, spko.SPK_VER_NO, spko.ORG_UNIT_CD, so.ORG_UNIT_NM
                    FROM S1SPK_ORG_UNIT spko
                             LEFT JOIN (SELECT org_unit_cd, ORG_UNIT_NM
                                        FROM S1ORG_UNIT
                                        WHERE EXPIRY_DT = '01-JAN-1900') so
                                       ON spko.ORG_UNIT_CD = so.ORG_UNIT_CD
                    WHERE RESP_CAT_CD = 'O') org
                   ON ssp.SPK_NO = org.SPK_NO
                       AND ssp.SPK_VER_NO = org.SPK_VER_NO
         JOIN S1STU_DET stu
              ON ssp.stu_id = stu.STU_ID
         JOIN S1STU_DISABILITY sdis
              ON ssp.stu_id = sdis.STU_ID
WHERE                                -- rel: swap first two commented dates
--     ss.START_DT <= CURRENT_DATE    -- Study periods where the current date is between study period start and result publication
--   AND rp.START_DT >= CURRENT_DATE
    avail_yr = 2022                  -- Restrict availability year
  AND ss.sprd_cd = '2'               -- Restrict study period to semester one
  AND cat.SPK_CAT_LVL_CD = 'UG'      -- Restrict to undergraduate
  AND ssp.LOCATION_CD = '1'          -- Restrict to Bentley
  AND ssp.parent_ssp_no = ssp.ssp_no -- Restrict to Course
  AND ssp.SSP_STTS_CD = 'ADM'        -- Restrict to Admitted Courses
  AND NOT EXISTS -- This will check that a pass or a fail has not occurred in a study period with a start date before the current study period
    (SELECT ssp2.stu_id
     FROM S1SSP_STU_SPK ssp2
              JOIN S1CYR_LOC_DT ss2
                   ON ss2.CALDR_YR = ssp2.AVAIL_YR
                       AND ss2.LOCATION_CD = ssp2.LOCATION_CD
                       AND ss2.SPRD_CD = ssp2.SPRD_CD
                       AND ss2.DT_TYPE_CD = 'SS'
     WHERE SSP.SSP_NO = ssp2.PARENT_SSP_NO
       AND ssp.LOCATION_CD = ssp2.LOCATION_CD
       AND ssp2.SSP_STTS_CD IN ('PASS', 'FAIL')
       AND ss2.START_DT < ss.START_DT)
)
;


-- create an  mview on the above for convenience
DROP VIEW da_student_vw;

select * from da_student_vw;

DROP MATERIALIZED VIEW da_student_mv;


-- REFRESH MATERIALIZED VIEW da_student_mv;

CREATE MATERIALIZED VIEW student1.da_student_mv
    TABLESPACE dataplatform_ts
AS
(SELECT * from da_student_vw
ORDER BY stu_id);

------------------------------------------------------------------
SELECT *
FROM da_student_mv;

SELECT COUNT(*) AS total_stu_count
FROM da_student_mv;
-- now 8356 was  109965 was 119166   65s
SELECT COUNT(DISTINCT (stu_id)) AS unique_stu_count
FROM da_student_mv;

SELECT COUNT(*)
FROM da_engagement_stage_current;

SELECT COUNT(DISTINCT stu_id)
FROM da_engagement_stage_current;

---------------------------------------------------------
-- start again
-- truncate the staging table
TRUNCATE da_engagement_stage_current;



-- now 6471, was  31309 was 35001
----------------------------------------------------------------
-- set up student id's to use in the da table
-- put these id's into the table if not there already
-- note this is using unique code
INSERT INTO da_engagement_stage_current (stu_id)
    (SELECT DISTINCT (stu_id)
     FROM da_student_mv ss
     WHERE ss.stu_id NOT IN (SELECT stu_id FROM da_engagement_stage_current dar2))
;

SELECT COUNT(*), COUNT(DISTINCT (stu_id))
FROM da_engagement_stage_current dar;

-- get rid of rows from the old query
-- 11015
SELECT COUNT(*)
FROM da_engagement_stage_current
WHERE stu_id NOT IN (SELECT stu_id FROM da_student_mv)
;

DELETE
FROM da_engagement_stage_current
WHERE stu_id NOT IN (SELECT stu_id FROM da_student_mv)
;
--------------------
-- set some fields from main statement
-- ok

WITH t AS
         (SELECT stu_id,
                 ATTNDC_MODE_CD,
                 ORG_UNIT_NM,
                 CASE WHEN STU_ABOR_TSI_CD IN ('Y', 'B', 'T') THEN 'Yes' ELSE 'No' END stu_abor_tst_fg,
                 STU_DISAB_FG,
                 COURSE_COMMENCEMENT_DATE
          FROM da_student_mv mv)
UPDATE da_engagement_stage_current da
SET (attendance_mode, owning_org, indigenous_fg, disability_fg, course_commencement_dt) =
        (t.ATTNDC_MODE_CD,
         t.ORG_UNIT_NM,
         t.stu_abor_tst_fg,
         t.STU_DISAB_FG,
         t.COURSE_COMMENCEMENT_DATE)
FROM t
WHERE da.stu_id = t.stu_id;

SELECT *
FROM da_engagement_stage_current;
---------------------------------------------------------------------------------------------------------------------

-- To obtain standard code descriptions
-- link on liab_cat_cd = code_id (or equivalent)
SELECT *
FROM s1stc_code sc
WHERE code_type = 'SPRD_CD' -- study periods
ORDER BY code_descr
;

-- To obtain Mobile number
-- Link on stu_id = stu_id
-- rel note just mobile phone ?
SELECT PHONE_NO
FROM S1STU_PHONE
WHERE PHONE_TYPE_CD = '$MOB'
;


-- set if exists
UPDATE da_engagement_stage_current da
SET contact_ph_provided_fg = 'Yes'
WHERE stu_id IN
      (SELECT stu_id
       FROM s1stu_phone sp
       WHERE phone_type_cd = '$MOB')
;


UPDATE da_engagement_stage_current
SET contact_ph_provided_fg = 'No'
WHERE contact_ph_provided_fg IS NULL;
---------------------------------------------------------------------------------------------------------------------
-- first offer date
-- To determine the first date of offer
-- Link on ssp_no = ssp_no
SELECT MIN(EFFCT_START_DT)
FROM S1SSP_STTS_HIST
WHERE SSP_STTS_CD = 'OFF'
  AND ssp_no = 'join here'
;

-- get min effective start date
-- NOTE should this be max start date?
SELECT dmv.stu_id, MIN(sh.effct_start_dt) min_start, MAX(sh.effct_start_dt) max_start
FROM S1SSP_STTS_HIST sh,
     da_student_mv dmv
WHERE sh.SSP_STTS_CD = 'OFF'
  AND sh.ssp_no = dmv.ssp_no
GROUP BY dmv.stu_id;

UPDATE da_engagement_stage_current
SET offer_dt = NULL;


-- ok
WITH t AS
         (SELECT dmv.stu_id, MIN(sh.effct_start_dt) min_start, MAX(sh.effct_start_dt) max_start
          FROM S1SSP_STTS_HIST sh,
               da_student_mv dmv
          WHERE sh.SSP_STTS_CD = 'OFF'
            AND sh.ssp_no = dmv.ssp_no
          GROUP BY dmv.stu_id)
UPDATE da_engagement_stage_current da
SET offer_dt = t.min_start
FROM t
WHERE da.STU_ID = t.stu_id
;

SELECT *
FROM da_engagement_stage_current;

--------------------------------------------------------------------------
-- To determine when student was first admitted (accepted their offer)
-- Link on ssp_no = ssp_no
-- rel: we don't seem to use offer accepted.

SELECT dmv.stu_id, MIN(EFFCT_START_DT)
FROM S1SSP_STTS_HIST sh,
     da_student_mv dmv
WHERE sh.SSP_STTS_CD = 'ADM'
  AND sh.ssp_no = dmv.ssp_no
GROUP BY dmv.stu_id
;

WITH t AS
         (SELECT dmv.stu_id, MIN(sh.effct_start_dt) min_start, MAX(sh.effct_start_dt) max_start
          FROM S1SSP_STTS_HIST sh,
               da_student_mv dmv
          WHERE sh.SSP_STTS_CD = 'ADM'
            AND sh.stu_id = dmv.stu_id
          GROUP BY dmv.stu_id)
UPDATE da_engagement_stage_current da
SET offer_acceptance_dt = t.min_start
FROM t
WHERE t.stu_id = da.stu_id
;
--------------------------------------------------------------------------
-- To determine when student first enrolled
-- link on ssp_no = parent_ssp_no
-- This logic will only work if you are looking at this data during the study period
-- It will not work retrospectively for previous study period because the units will no longer have a status of Enrolled. (they will be passed or failed)
-- REL: now doing this with history table

-- try this:
-- To determine when student first enrolled
-- Checking history table will allow to run retrospectively (if student is no longer enrolled they have passed failed WD)
-- link on ssp_no = parent_ssp_no
SELECT mv.stu_id, MIN(sh.EFFCT_START_DT) FIRST_ENR
FROM S1SSP_STTS_HIST sh,
     S1SSP_STU_SPK ssp,
     da_student_mv mv
WHERE sh.SSP_NO = ssp.SSP_NO
  AND sh.SSP_STTS_CD = 'ENR'
  AND mv.ssp_no = ssp.parent_ssp_no
GROUP BY mv.stu_id;


WITH t AS
         (SELECT mv.stu_id, MIN(sh.EFFCT_START_DT) FIRST_ENR
          FROM S1SSP_STTS_HIST sh,
               S1SSP_STU_SPK ssp,
               da_student_mv mv
          WHERE sh.SSP_NO = ssp.SSP_NO
            AND sh.SSP_STTS_CD = 'ENR'
            AND mv.ssp_no = ssp.parent_ssp_no
          GROUP BY mv.stu_id)
UPDATE da_engagement_stage_current da
SET enrolment_dt = t.FIRST_ENR
FROM t
WHERE t.STU_ID = da.stu_id
;


select count(*) from da_engagement_stage_current where enrolment_dt is null;
------------------------------------------------------------------

-- To determine Tax File Number. This column is encrypted backend. You may need to do a data in column query to determine if its been entered. length(TFN) > 1
-- Link on ssp_no = ssp_no
SELECT stu_id,
       CASE WHEN LENGTH(TFN) > 1 THEN 'Yes' ELSE 'No' END TFN
FROM S1SSP_GAF_DTL
;

WITH t AS (SELECT stu_id,
                  CASE WHEN LENGTH(TFN) > 1 THEN 'Yes' ELSE 'No' END TFN
           FROM S1SSP_GAF_DTL)
UPDATE da_engagement_stage_current da
SET tax_file_number_fg = t.tfn
FROM t
WHERE t.STU_ID = da.stu_id
;


UPDATE da_engagement_stage_current da
SET tax_file_number_fg = 'NA'
WHERE tax_file_number_fg IS NULL
;

SELECT COUNT(*)
FROM da_engagement_stage_current
WHERE tax_file_number_fg IS NULL;
------------------------------------------------------------------
- tax_file_cert_fg

-- CHANGE THESE DATES to parameter
-- would have to make it pgsqld anonymous block ...
-- dates

------------------------------------------------------------------------------------------------------------------------
define SEM_START_DATE = '25/07/2022' -- s2
define SEM_END_DATE = '11/11/2022'   --s2
------------------------------------------------------------------
    -- To determine tax_file_cert_fg (student has a CP sanction)
SELECT stu_id, 'Yes' TAX_FILE_CERT_FG
FROM S1STU_SANCTION
WHERE SANCT_TYPE_CD = 'CP'
  AND STU_SANCT_EFFCT_DT <= TO_DATE('11/11/2022', 'DD/MM/YYYY') -- end of semester
  AND (STU_SANCT_END_DT > TO_DATE('25/07/2022', 'DD/MM/YYYY') --start of semester
    OR STU_SANCT_END_DT = '01-JAN-1900');

WITH t AS (SELECT stu_id, 'Yes' TAX_FILE_CERT_FG
           FROM S1STU_SANCTION
           WHERE SANCT_TYPE_CD = 'CP'
             AND STU_SANCT_EFFCT_DT <= TO_DATE('11/11/2022', 'DD/MM/YYYY') -- end of semester
             AND (STU_SANCT_END_DT > TO_DATE('25/07/2022', 'DD/MM/YYYY') --start of semester
               OR STU_SANCT_END_DT = '01-JAN-1900'))
UPDATE da_engagement_stage_current da
SET tax_file_cert_fg = t.TAX_FILE_CERT_FG
FROM t
WHERE t.STU_ID = da.stu_id
;

UPDATE da_engagement_stage_current da
SET tax_file_cert_fg = 'No'
WHERE tax_file_cert_fg IS NULL
;
------------------------------------------------------------------
-- To determine USI
-- link on stu_id = stu_id

SELECT STU_ALT_ID
FROM S1STU_ALT_ID
WHERE STU_ALT_ID_TYPE_CD = 'USI'
;
------------------------------------------------------------------
UPDATE da_engagement_stage_current da
SET unique_stu_identifyer_fg = 'Yes'
WHERE stu_id IN (SELECT stu_id
                 FROM S1STU_ALT_ID sai
                 WHERE STU_ALT_ID_TYPE_CD = 'USI'
                   AND LENGTH(stu_alt_id) > 0)
;



UPDATE da_engagement_stage_current da
SET unique_stu_identifyer_fg = 'No'
WHERE unique_stu_identifyer_fg IS NULL;
------------------------------------------------------------------
- new
----------------------------------------------
-- To determine Step up bonus
-- link on stu_id = stu_id
SELECT stu_id, 'Yes' STEP_UP_BONUS
FROM S1STU_OTH_SCORE SC
WHERE SC.PREV_SCORE_TYPE_CD IN ('SIP', 'SIB');

WITH t AS (SELECT stu_id, 'Yes' STEP_UP_BONUS
           FROM S1STU_OTH_SCORE SC
           WHERE SC.PREV_SCORE_TYPE_CD IN ('SIP', 'SIB'))
UPDATE da_engagement_stage_current da
SET step_up_bonus_atar_fg = t.STEP_UP_BONUS
FROM t
WHERE t.STU_ID = da.stu_id
;

UPDATE da_engagement_stage_current da
SET step_up_bonus_atar_fg = 'No'
WHERE step_up_bonus_atar_fg IS NULL;
------------------------------------------------------------------
-- To determine first in family
-- link on stu_id = stu_id
SELECT CASE WHEN guardian_hea_cd IN ('PG', 'BACH', 'OTH') THEN 'No' ELSE 'Yes' END FIRST_IN_FAMILY
FROM S1STU_GUARDIAN;

WITH t AS (SELECT stu_id,
                  CASE WHEN guardian_hea_cd IN ('PG', 'BACH', 'OTH') THEN 'No' ELSE 'Yes' END FIRST_IN_FAMILY
           FROM S1STU_GUARDIAN)
UPDATE da_engagement_stage_current da
SET first_in_family_fg = t.FIRST_IN_FAMILY
FROM t
WHERE t.STU_ID = da.stu_id
;

SELECT COUNT(*)
FROM da_engagement_stage_current
WHERE first_in_family_fg IS NULL;

UPDATE da_engagement_stage_current
SET first_in_family_fg = 'NA'
WHERE first_in_family_fg IS NULL;
------------------------------------------------------------------
-- To determine Sanction with Holds
-- link on stu_id = stu_id
-- rel: modify this for during the historical semester
-- chad: that logic should work using semester 1 start date and result publication date hard coded.
-- commented out line below. if the sanction started before the end of semester and ended anytime after star of semester
-- or is not ended it was in pace at some stage of the semester
SELECT * --stu_id
FROM S1STU_SANCTION sct
WHERE sct.STU_SANCT_EFFCT_DT <=  to_date('11/11/2022','DD/MM/YYYY') -- end of semester
  AND (sct.STU_SANCT_END_DT >  to_date('25/07/2022','DD/MM/YYYY')  --start of semester
        OR sct.STU_SANCT_END_DT = '01-JAN-1900')
  -- and sct.stu_sanct_end_dt < to_date('25/07/2022','DD/MM/YYYY') -- rel add this
  AND EXISTS(SELECT 1
             FROM S1SYS_SCT_HLD_DTL sh
             WHERE sct.SANCT_TYPE_CD = sh.SANCT_TYPE_CD)
--and stu_id in (select stu_id from da_engagement_stage_current)
;

-- ignore if

UPDATE da_engagement_stage_current
SET sanctions_hold_fg = 'Yes'
WHERE stu_id IN (SELECT stu_id
FROM S1STU_SANCTION sct
WHERE sct.STU_SANCT_EFFCT_DT <=  to_date('11/11/2022','DD/MM/YYYY') -- end of semester
  AND (sct.STU_SANCT_END_DT >  to_date('25/07/2022','DD/MM/YYYY')  --start of semester
        OR sct.STU_SANCT_END_DT = '01-JAN-1900')
  -- and sct.stu_sanct_end_dt < to_date('25/07/2022','DD/MM/YYYY') -- rel add this
  AND EXISTS(SELECT 1
             FROM S1SYS_SCT_HLD_DTL sh
             WHERE sct.SANCT_TYPE_CD = sh.SANCT_TYPE_CD))
;

select count(*) from da_engagement_stage_current da
where da.sanctions_hold_fg = 'Yes';

UPDATE da_engagement_stage_current
SET sanctions_hold_fg = 'No'
WHERE sanctions_hold_fg IS NULL;

-- clear all
UPDATE da_engagement_stage_current
SET sanctions_hold_fg = NULL
;

-- To determine Student Progression Agreement
-- link on stu_id = stu_id
SELECT stu_id
FROM s1agm_agreement_det ag
WHERE ag.agree_type_cd = 'SPA'         -- Type SPA
  AND ag.ACTUAL_END_DT = '01-JAN-1900' -- not end dated
  AND ag.AGREE_STTS_CD = '$AC'
;-- status active


UPDATE da_engagement_stage_current
SET stu_progression_agreement_fg = 'Yes'
WHERE stu_id IN (SELECT stu_id
                 FROM s1agm_agreement_det ag
                 WHERE ag.agree_type_cd = 'SPA'         -- Type SPA
                   AND ag.ACTUAL_END_DT = '01-JAN-1900' -- not end dated
                   AND ag.AGREE_STTS_CD = '$AC')
;


UPDATE da_engagement_stage_current
SET stu_progression_agreement_fg = 'No'
WHERE stu_progression_agreement_fg IS NULL
;


-----------------------------------------------------------------------------------------------------------
-- low_socio_econ_postcode_fg
-- To determine Low Socio Economic Postcodes
-- This is not specifically stored in S1. We have postcode in the address but not if low socio economic
-- link on stu_id = stu_id
SELECT stu_id, STU_PCODE
FROM S1STU_ADDR
WHERE STU_ADDR_TYPE_CD = 'P';

-- Student Permanent Address pcode
WITH t AS
         (SELECT stu_id, STU_PCODE
          FROM S1STU_ADDR
          WHERE STU_ADDR_TYPE_CD = 'P')
UPDATE da_engagement_stage_current da
SET stu_pcode = t.stu_pcode
FROM t
WHERE da.stu_id = t.stu_id;

UPDATE da_engagement_stage_current
SET stu_pcode = 'NA'
WHERE da_engagement_stage_current.stu_pcode IS NULL
;

commit;

-- To determine Low Socio Economic Postcodes
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
           FROM S1STU_ADDR
           WHERE STU_ADDR_TYPE_CD = 'P')
UPDATE da_engagement_stage_current da
SET low_socio_econ_postcode_fg = t.LOW_SOCIO
FROM t
WHERE da.stu_id = t.stu_id;

-- revert NA pcode to NA flag, no postcode is usualy a blank character

UPDATE da_engagement_stage_current
SET low_socio_econ_postcode_fg = 'NA'
WHERE da_engagement_stage_current.stu_pcode = ' '
;

select * from da_engagement_stage_current
WHERE da_engagement_stage_current.stu_pcode = ' '
;


-- Student Permanent Address
-------------------------------------------------------------------------------------------------
-- stu_type
-- To determine Student Type (Domestic / International)
-- link on stu_id = stu_id
SELECT stu_id,
       CASE
           WHEN STU_CITIZEN_CD IN ('4', '5') -- 4 and 5 are international others are considered domestic
               THEN 'International'
           ELSE 'Domestic'
           END STUDENT_TYPE
FROM s1stu_det;

WITH t AS (SELECT stu_id,
                  CASE
                      WHEN STU_CITIZEN_CD IN ('4', '5') -- 4 and 5 are international others are considered domestic
                          THEN 'International'
                      ELSE 'Domestic'
                      END STUDENT_TYPE
           FROM s1stu_det)
UPDATE da_engagement_stage_current da
SET stu_type = t.student_type
FROM t
WHERE da.STU_ID = t.stu_id
;
------------------------------------------------------------------
-- To determine if student is class registered
-- Link ssp_no to parent_ssp_no
-- rel: I think this is current classes
update da_engagement_stage_current set class_reg_complete_fg = null;

SELECT cr.stu_id
FROM s1ssp_stu_spk ssp
         JOIN S1SSP_CLASS_REGN cr
              ON ssp.ssp_no = cr.SSP_NO
WHERE CLASS_REGN_STTS_CD = 'R'
  AND cr.stu_id IN (SELECT stu_id FROM da_student_mv);

UPDATE da_engagement_stage_current da
SET class_reg_complete_fg = 'Yes'
WHERE stu_id IN (SELECT cr.stu_id
                 FROM s1ssp_stu_spk ssp
                          JOIN S1SSP_CLASS_REGN cr
                               ON ssp.ssp_no = cr.SSP_NO
                 WHERE CLASS_REGN_STTS_CD = 'R');

UPDATE da_engagement_stage_current da
SET class_reg_complete_fg = 'No'
WHERE class_reg_complete_fg is null;
------------------------------------------------------------------
-- set some flags based on dates

-- late_enrolment_fg : after start of semester + 1

SELECT (TO_DATE('25/07/2022', 'DD/MM/YYYY') + 7)
;

SELECT stu_id, enrolment_dt
FROM da_engagement_stage_current
WHERE enrolment_dt > (TO_DATE('25/07/2022', 'DD/MM/YYYY') + 7);

UPDATE da_engagement_stage_current da
SET late_enrolment_fg = null;

UPDATE da_engagement_stage_current da
SET late_enrolment_fg = 'Yes'
WHERE stu_id IN (SELECT stu_id
                 FROM da_engagement_stage_current
                 WHERE enrolment_dt > (TO_DATE('25/07/2022', 'DD/MM/YYYY') + 7))
;
UPDATE da_engagement_stage_current da
SET late_enrolment_fg = 'No'
WHERE late_enrolment_fg IS NULL;

------------------------------------------------------------------
--late offer : after start of semester
SELECT stu_id, offer_dt
FROM da_engagement_stage_current
WHERE offer_dt > TO_DATE('25/07/2022', 'DD/MM/YYYY')
;

-- clear them
UPDATE da_engagement_stage_current da
SET late_offer_provided_fg = NULL;


UPDATE da_engagement_stage_current da
SET late_offer_provided_fg = 'Yes'
WHERE stu_id IN (SELECT stu_id
                 FROM da_engagement_stage_current
                 WHERE offer_dt > TO_DATE('25/07/2022', 'DD/MM/YYYY'));

UPDATE da_engagement_stage_current da
SET late_offer_provided_fg = 'No'
WHERE late_offer_provided_fg IS NULL;
------------------------------------------------------------------
-- late_acceptance_fg
SELECT stu_id, offer_dt
FROM da_engagement_stage_current
WHERE offer_acceptance_dt > (TO_DATE('25/07/2022', 'DD/MM/YYYY') + 7)
;

update da_engagement_stage_current da
SET late_offer_acceptance_fg = null;

;


UPDATE da_engagement_stage_current da
SET late_offer_acceptance_fg = 'Yes'
WHERE stu_id IN (SELECT stu_id
                 FROM da_engagement_stage_current
                 WHERE offer_acceptance_dt > (TO_DATE('25/07/2022', 'DD/MM/YYYY') + 7));

UPDATE da_engagement_stage_current da
SET late_offer_acceptance_fg = 'No'
WHERE late_offer_acceptance_fg IS NULL;



-- tidy up some flags

UPDATE da_engagement_stage_current
SET scholarship ='Yes'
WHERE scholarship = 'Y'
;

UPDATE da_engagement_stage_current
SET scholarship ='No'
WHERE scholarship = 'N'
;


UPDATE da_engagement_stage_current
SET disability_fg ='Yes'
WHERE disability_fg = 'Y'
;

UPDATE da_engagement_stage_current
SET disability_fg ='No'
WHERE disability_fg = 'N'
;

-- this is true buy definition of the original select
UPDATE da_engagement_stage_current
SET campus ='Bentley'
;
