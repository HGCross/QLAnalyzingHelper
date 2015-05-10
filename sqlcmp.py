# coding: utf-8

import sqlparse

sql1 = '''
SELECT IFNULL(modu.head_gbn, '') AS head_gbn /*말머리 구분(10129)*/
              ,sbj.grade_gbn
              ,CASE WHEN sbj.semester_gbn = 3 THEN '공통' ELSE sbj.semester_gbn END AS semester_gbn_nm
              ,ishomedb.uf_code_nm(10101, sbj.subj_gbn) AS subj_gbn_nm
              ,CASE WHEN modu.head_gbn = 10001 THEN CONCAT(
                    CASE
                        WHEN
                            sbj.subj_gbn = 10021
                        THEN
                            IFNULL(les.chapter_key, 0)
                        ELSE les.sort
                    END
                    , '장. ', les.subj_lesson_nm) /*예복습*/
                    WHEN modu.head_gbn = 10005 AND sbj.subj_gbn = 10023 AND modu.useq = 1 THEN CONCAT(IF(les.subj_no = 174 || les.subj_no = 175, les.chapter_key, les.sort), '장. ', les.subj_lesson_nm, ' (실력기본)')
                    WHEN modu.head_gbn = 10005 AND sbj.subj_gbn = 10023 AND modu.useq = 2 THEN CONCAT(IF(les.subj_no = 174 || les.subj_no = 175, les.chapter_key, les.sort), '장. ', les.subj_lesson_nm, ' (실력중급)')
                    WHEN modu.head_gbn = 10005 AND sbj.subj_gbn = 10023 AND modu.useq = 3 THEN CONCAT(IF(les.subj_no = 174 || les.subj_no = 175, les.chapter_key, les.sort), '장. ', les.subj_lesson_nm, ' (실력상급)') 
                    WHEN modu.head_gbn = 10005 THEN CONCAT(les.sort, '장. ', les.subj_lesson_nm, ' (', modu.useq, '회차)') /*실력평가*/
                    WHEN modu.head_gbn = 10002 AND sbj.subj_gbn = 10023 AND modu.useq = 1 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (단원중급)') 
                    WHEN modu.head_gbn = 10002 AND sbj.subj_gbn = 10023 AND modu.useq = 2 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (단원상급)') 
                    WHEN modu.head_gbn = 10002 AND sbj.subj_gbn = 10023 AND modu.useq = 3 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (단원기본)') 
                    WHEN modu.head_gbn = 10002 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (', modu.useq, '회차)') /*단원평가*/
                    ELSE CONCAT(les.subj_lesson_nm, ' (', modu.useq, '회차)') /*중기말*/
               END AS subj_lesson_nm
              ,IF(les.lesson_gbn = 10002 OR les.lesson_gbn = 10003, '', CONCAT(' ', SUBSTRING(les.order_key, 1, 2))) AS unit_no
              ,CASE WHEN act.clear_dt IS NOT NULL THEN '완료'
                    ELSE (SELECT IF(COUNT(1) = 0, '학습전', '학습중')
                          FROM tz_lms_act_element 
                          WHERE student_no = act.student_no
                              AND plan_de = act.plan_de
                              AND module_no = modu.module_no
                         )
               END AS clear_txt
              ,CASE WHEN modu.head_gbn = '10001' THEN '0' ELSE '1' END AS lesson_gbn
              ,CASE WHEN act.clear_dt IS NOT NULL THEN 'state complete' ELSE 'state imperfective' END AS clear_css                                           /* 완료 여부 표시 css */
              ,CASE WHEN act.clear_dt IS NOT NULL THEN 'end'
                    ELSE (SELECT IF(COUNT(1) = 0, 'st', 'st02')
                          FROM tz_lms_act_element 
                          WHERE student_no = act.student_no
                              AND plan_de = act.plan_de
                              AND module_no = modu.module_no
                         )
               END AS clear_img
              ,CASE WHEN act.clear_dt IS NOT NULL THEN '1' ELSE  '0' END AS start_txt /*실력평가분리 후 clear_txt, clear_img와 동일*/
              ,'' AS f_test_dt
              ,modu.module_no
              ,les.subj_no
              ,les.subj_lesson_no
              ,'' AS sort  /*추가 황진우 한자서당 장표시를 위해*/
              ,act.act_dt
              ,act.clear_dt
              ,pln.plan_de
              ,DATE_FORMAT(pln.plan_de,  '%Y') AS yy
              ,DATE_FORMAT(pln.plan_de,  '%m') AS mm
              ,DATE_FORMAT(pln.plan_de,  '%d') AS dd
              ,CASE WHEN DAYNAME(pln.plan_de) = 0 THEN '월'
                    WHEN DAYNAME(pln.plan_de) = 1 THEN '화'
                    WHEN DAYNAME(pln.plan_de) = 2 THEN '수'
                    WHEN DAYNAME(pln.plan_de) = 3 THEN '목'
                    WHEN DAYNAME(pln.plan_de) = 4 THEN '금'
                    WHEN DAYNAME(pln.plan_de) = 5 THEN '토'
                    WHEN DAYNAME(pln.plan_de) = 6 THEN '일'
               END AS ww
              ,les.contents_xml_type
              ,(SELECT IFNULL(SUM(tc.pic_mediatime),0) 
                    FROM tz_lcms_contents tl
                    LEFT OUTER JOIN tz_cms_contents tc ON tc.contents_no = tl.porting_value
                    WHERE tl.contents_no = les.contents_no) AS media_time 
              ,(SELECT IFNULL(SUM(study_time),0)
                    FROM tz_lms_act_element
                    WHERE student_no = pln.student_no
                    AND plan_de = pln.plan_de
                    AND module_no = pln.module_no) AS study_duration
        FROM ishomedb.tz_lms_plan_module pln
            INNER JOIN
        ishomedb.tz_lms_module modu ON pln.module_no = modu.module_no
            LEFT OUTER JOIN
        ishomedb.tz_lms_act_module act ON pln.student_no = act.student_no AND pln.plan_de = act.plan_de AND modu.module_no = act.module_no
            INNER JOIN
        ishomedb.tz_lcms_study_lesson les ON modu.subj_lesson_no = les.subj_lesson_no AND les.use_yn = 'Y'
            INNER JOIN
        ishomedb.tz_lms_course cou ON modu.course_no = cou.course_no
            INNER JOIN
        ishomedb.tz_lcms_subj sbj ON cou.subj_no = sbj.subj_no
        WHERE pln.student_no = '272749'
            AND pln.plan_de >= '2015.04.27'
            AND pln.plan_de <= '2015.05.03'
        
        UNION ALL
                        
        SELECT '' AS head_gbn
              ,SUBSTRING_INDEX(REPLACE(ishomedb.uf_lcms_theme_category_connect_by_path('-', b.upper_no, 14), '마쓰연산', '마쓰'), '-', 3) AS grade_gbn
              ,'1' AS semester_gbn_nm
              ,'마쓰' AS subj_gbn_nm
              ,b.category_nm AS subj_lesson_nm
              ,'' AS unit_no
              ,CASE WHEN IFNULL(a.clear_dt, '') != '' THEN '완료' ELSE '학습전' END AS clear_txt  
              ,'' AS lesson_gbn
              ,CASE WHEN IFNULL(a.clear_dt, '') != '' THEN 'state complete' ELSE 'state imperfective' END AS clear_css  
              ,CASE WHEN IFNULL(a.clear_dt, '') != '' THEN 'end' ELSE 'st' END AS clear_img
              ,'' AS start_txt
              ,'' AS f_test_dt
              ,'' AS module_no
              ,'' AS subj_no
              ,'' AS subj_lesson_no
              ,'' AS sort  /*추가 황진우 한자서당 장표시를 위해*/
              ,a.act_dt AS act_dt
              ,a.clear_dt AS clear_dt
              ,a.plan_de
              ,DATE_FORMAT(a.plan_de, '%Y') AS yy
              ,DATE_FORMAT(a.plan_de, '%m') AS mm
              ,DATE_FORMAT(a.plan_de, '%d') AS dd
              ,CASE WHEN DAYNAME(a.plan_de) = 0 THEN '월'
                    WHEN DAYNAME(a.plan_de) = 1 THEN '화'
                    WHEN DAYNAME(a.plan_de) = 2 THEN '수'
                    WHEN DAYNAME(a.plan_de) = 3 THEN '목'
                    WHEN DAYNAME(a.plan_de) = 4 THEN '금'
                    WHEN DAYNAME(a.plan_de) = 5 THEN '토'
                    WHEN DAYNAME(a.plan_de) = 6 THEN '일'
               END AS ww
              ,'' AS contents_xml_type
              ,'' AS media_time
              ,'' AS study_duration
        FROM tz_lcms_plan_math a
        INNER JOIN tz_lcms_theme_category b
        ON a.category_no = b.category_no 
        WHERE a.student_no = '272749'
            AND a.plan_de >= '2015.04.27'
            AND a.plan_de <= '2015.05.03'
        
        UNION ALL
        
        SELECT '' AS head_gbn
              ,SUBSTRING_INDEX(REPLACE(REPLACE(
                  ishomedb.uf_lcms_theme_category_connect_by_path('-', ltm.category_no, 7), '심화특별학습', '심화'), '선사시대 ~ 통일신라', '~통일신라'), '-', 5
               ) AS grade_gbn
              ,'1' AS semester_gbn_nm
              ,'테마자료' AS subj_gbn_nm
              ,ltm.title AS subj_lesson_nm
              ,'' AS unit_no
              ,CASE WHEN IFNULL(lpt.clear_dt, '') != '' THEN '완료' ELSE IF(lpt.act_dt<>'','학습중','학습전') END AS clear_txt  
              ,'' AS lesson_gbn     /* 학습시작일 */
              ,CASE WHEN IFNULL(lpt.clear_dt, '') != '' THEN 'state complete' ELSE 'state imperfective' END AS clear_css  
              ,CASE WHEN IFNULL(lpt.clear_dt, '') != '' THEN 'end' ELSE IF(lpt.act_dt<>'','st02','st') END AS clear_img
              ,'' AS start_txt
              ,'' AS f_test_dt
              ,'' AS module_no
              ,'' AS subj_no
              ,'' AS subj_lesson_no
              , ltm.sort
              ,lpt.act_dt AS act_dt
              ,lpt.clear_dt AS clear_dt
              ,lpt.plan_de
              ,DATE_FORMAT(lpt.plan_de, '%Y') AS yy
              ,DATE_FORMAT(lpt.plan_de, '%m') AS mm
              ,DATE_FORMAT(lpt.plan_de, '%d') AS dd
              ,CASE WHEN DAYNAME(lpt.plan_de) = 0 THEN '월'
                    WHEN DAYNAME(lpt.plan_de) = 1 THEN '화'
                    WHEN DAYNAME(lpt.plan_de) = 2 THEN '수'
                    WHEN DAYNAME(lpt.plan_de) = 3 THEN '목'
                    WHEN DAYNAME(lpt.plan_de) = 4 THEN '금'
                    WHEN DAYNAME(lpt.plan_de) = 5 THEN '토'
                    WHEN DAYNAME(lpt.plan_de) = 6 THEN '일'
               END AS ww
              ,'' AS contents_xml_type
              ,'' AS media_time
              ,'' AS study_duration
        FROM tz_lms_plan_theme lpt
        INNER JOIN tz_lcms_theme_material ltm
        ON lpt.material_no = ltm.material_no
        WHERE lpt.student_no = '272750'
            AND lpt.plan_de >= '2015.04.27'
            AND lpt.plan_de <= '2015.05.03'
        ORDER BY plan_de;
'''

sql2 = '''
SELECT IFNULL(modu.head_gbn, '') AS head_gbn /*말머리 구분(10129)*/
              ,sbj.grade_gbn
              ,CASE WHEN sbj.semester_gbn = 4 THEN '공통' ELSE sbj.semester_gbn END AS semester_gbn_nm
              ,ishomedb.uf_code_nm(10101, sbj.subj_gbn) AS subj_gbn_nm
              ,CASE WHEN modu.head_gbn = 10001 THEN CONCAT(
                    CASE
                        WHEN
                            sbj.subj_gbn = 10021
                        THEN
                            IFNULL(les.chapter_key, 0)
                        ELSE les.sort
                    END
                    , '장. ', les.subj_lesson_nm) /*예복습*/
                    WHEN modu.head_gbn = 10005 AND sbj.subj_gbn = 10023 AND modu.useq = 1 THEN CONCAT(IF(les.subj_no = 174 || les.subj_no = 175, les.chapter_key, les.sort), '장. ', les.subj_lesson_nm, ' (실력기본)')
                    WHEN modu.head_gbn = 10005 AND sbj.subj_gbn = 10023 AND modu.useq = 2 THEN CONCAT(IF(les.subj_no = 174 || les.subj_no = 175, les.chapter_key, les.sort), '장. ', les.subj_lesson_nm, ' (실력중급)')
                    WHEN modu.head_gbn = 10005 AND sbj.subj_gbn = 10023 AND modu.useq = 3 THEN CONCAT(IF(les.subj_no = 174 || les.subj_no = 175, les.chapter_key, les.sort), '장. ', les.subj_lesson_nm, ' (실력상급)') 
                    WHEN modu.head_gbn = 10005 THEN CONCAT(les.sort, '장. ', les.subj_lesson_nm, ' (', modu.useq, '회차)') /*실력평가*/
                    WHEN modu.head_gbn = 10002 AND sbj.subj_gbn = 10023 AND modu.useq = 1 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (단원중급)') 
                    WHEN modu.head_gbn = 10002 AND sbj.subj_gbn = 10023 AND modu.useq = 2 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (단원상급)') 
                    WHEN modu.head_gbn = 10002 AND sbj.subj_gbn = 10023 AND modu.useq = 3 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (단원기본)') 
                    WHEN modu.head_gbn = 10002 THEN CONCAT(les.sort, '. ', les.subj_lesson_nm, ' (', modu.useq, '회차)') /*단원평가*/
                    ELSE CONCAT(les.subj_lesson_nm, ' (', modu.useq, '회차)') /*중기말*/
               END AS subj_lesson_nm
              ,IF(les.lesson_gbn = 10002 OR les.lesson_gbn = 10003, '', CONCAT(' ', SUBSTRING(les.order_key, 1, 2))) AS unit_no
              ,CASE WHEN act.clear_dt IS NOT NULL THEN '완료'
                    ELSE (SELECT IF(COUNT(1) = 0, '학습전', '학습중')
                          FROM tz_lms_act_element 
                          WHERE student_no = act.student_no
                              AND plan_de = act.plan_de
                              AND module_no = modu.module_no
                         )
               END AS clear_txt
              ,CASE WHEN modu.head_gbn = '10001' THEN '0' ELSE '1' END AS lesson_gbn
              ,CASE WHEN act.clear_dt IS NOT NULL THEN 'state complete' ELSE 'state imperfective' END AS clear_css                                           /* 완료 여부 표시 css */
              ,CASE WHEN act.clear_dt IS NOT NULL THEN 'end'
                    ELSE (SELECT IF(COUNT(1) = 0, 'st', 'st02')
                          FROM tz_lms_act_element 
                          WHERE student_no = act.student_no
                              AND plan_de = act.plan_de
                              AND module_no = modu.module_no
                         )
               END AS clear_img
              ,CASE WHEN act.clear_dt IS NOT NULL THEN '1' ELSE  '0' END AS start_txt /*실력평가분리 후 clear_txt, clear_img와 동일*/
              ,'' AS f_test_dt
              ,modu.module_no
              ,les.subj_no
              ,les.subj_lesson_no
              ,'' AS sort  /*추가 황진우 한자서당 장표시를 위해*/
              ,act.act_dt
              ,act.clear_dt
              ,pln.plan_de
              ,DATE_FORMAT(pln.plan_de,  '%Y') AS yy
              ,DATE_FORMAT(pln.plan_de,  '%m') AS mm
              ,DATE_FORMAT(pln.plan_de,  '%d') AS dd
              ,CASE WHEN DAYNAME(pln.plan_de) = 0 THEN '월'
                    WHEN DAYNAME(pln.plan_de) = 1 THEN '화'
                    WHEN DAYNAME(pln.plan_de) = 2 THEN '수'
                    WHEN DAYNAME(pln.plan_de) = 3 THEN '목'
                    WHEN DAYNAME(pln.plan_de) = 4 THEN '금'
                    WHEN DAYNAME(pln.plan_de) = 5 THEN '토'
                    WHEN DAYNAME(pln.plan_de) = 6 THEN '일'
               END AS ww
              ,les.contents_xml_type
              ,(SELECT IFNULL(SUM(tc.pic_mediatime),0) 
                    FROM tz_lcms_contents tl
                    LEFT OUTER JOIN tz_cms_contents tc ON tc.contents_no = tl.porting_value
                    WHERE tl.contents_no = les.contents_no) AS media_time 
              ,(SELECT IFNULL(SUM(study_time),0)
                    FROM tz_lms_act_element
                    WHERE student_no = pln.student_no
                    AND plan_de = pln.plan_de
                    AND module_no = pln.module_no) AS study_duration
        FROM ishomedb.tz_lms_plan_module pln
            INNER JOIN
        ishomedb.tz_lms_module modu ON pln.module_no = modu.module_no
            LEFT OUTER JOIN
        ishomedb.tz_lms_act_module act ON pln.student_no = act.student_no AND pln.plan_de = act.plan_de AND modu.module_no = act.module_no
            INNER JOIN
        ishomedb.tz_lcms_study_lesson les ON modu.subj_lesson_no = les.subj_lesson_no AND les.use_yn = 'Y'
            INNER JOIN
        ishomedb.tz_lms_course cou ON modu.course_no = cou.course_no
            INNER JOIN
        ishomedb.tz_lcms_subj sbj ON cou.subj_no = sbj.subj_no
        WHERE pln.student_no = '272749'
            AND pln.plan_de >= '2015.04.27'
            AND pln.plan_de <= '2015.05.03'
        
        UNION ALL
                        
        SELECT '' AS head_gbn
              ,SUBSTRING_INDEX(REPLACE(ishomedb.uf_lcms_theme_category_connect_by_path('-', b.upper_no, 14), '마쓰연산', '마쓰'), '-', 3) AS grade_gbn
              ,'1' AS semester_gbn_nm
              ,'마쓰' AS subj_gbn_nm
              ,b.category_nm AS subj_lesson_nm
              ,'' AS unit_no
              ,CASE WHEN IFNULL(a.clear_dt, '') != '' THEN '완료' ELSE '학습전' END AS clear_txt  
              ,'' AS lesson_gbn
              ,CASE WHEN IFNULL(a.clear_dt, '') != '' THEN 'state complete' ELSE 'state imperfective' END AS clear_css  
              ,CASE WHEN IFNULL(a.clear_dt, '') != '' THEN 'end' ELSE 'st' END AS clear_img
              ,'' AS start_txt
              ,'' AS f_test_dt
              ,'' AS module_no
              ,'' AS subj_no
              ,'' AS subj_lesson_no
              ,'' AS sort  /*추가 황진우 한자서당 장표시를 위해*/
              ,a.act_dt AS act_dt
              ,a.clear_dt AS clear_dt
              ,a.plan_de
              ,DATE_FORMAT(a.plan_de, '%Y') AS yy
              ,DATE_FORMAT(a.plan_de, '%m') AS mm
              ,DATE_FORMAT(a.plan_de, '%d') AS dd
              ,CASE WHEN DAYNAME(a.plan_de) = 0 THEN '월'
                    WHEN DAYNAME(a.plan_de) = 1 THEN '화'
                    WHEN DAYNAME(a.plan_de) = 2 THEN '수'
                    WHEN DAYNAME(a.plan_de) = 3 THEN '목'
                    WHEN DAYNAME(a.plan_de) = 4 THEN '금'
                    WHEN DAYNAME(a.plan_de) = 5 THEN '토'
                    WHEN DAYNAME(a.plan_de) = 6 THEN '일'
               END AS ww
              ,'' AS contents_xml_type
              ,'' AS media_time
              ,'' AS study_duration
        FROM tz_lcms_plan_math a
        INNER JOIN tz_lcms_theme_category b
        ON a.category_no = b.category_no 
        WHERE a.student_no = '272749'
            AND a.plan_de >= '2015.04.27'
            AND a.plan_de <= '2015.05.03'
        
        UNION ALL
        
        SELECT '' AS head_gbn
              ,SUBSTRING_INDEX(REPLACE(REPLACE(
                  ishomedb.uf_lcms_theme_category_connect_by_path('-', ltm.category_no, 7), '심화특별학습', '심화'), '선사시대 ~ 통일신라', '~통일신라'), '-', 5
               ) AS grade_gbn
              ,'1' AS semester_gbn_nm
              ,'테마자료' AS subj_gbn_nm
              ,ltm.title AS subj_lesson_nm
              ,'' AS unit_no
              ,CASE WHEN IFNULL(lpt.clear_dt, '') != '' THEN '완료' ELSE IF(lpt.act_dt<>'','학습중','학습전') END AS clear_txt  
              ,'' AS lesson_gbn     /* 학습시작일 */
              ,CASE WHEN IFNULL(lpt.clear_dt, '') != '' THEN 'state complete' ELSE 'state imperfective' END AS clear_css  
              ,CASE WHEN IFNULL(lpt.clear_dt, '') != '' THEN 'end' ELSE IF(lpt.act_dt<>'','st02','st') END AS clear_img
              ,'' AS start_txt
              ,'' AS f_test_dt
              ,'' AS module_no
              ,'' AS subj_no
              ,'' AS subj_lesson_no
              , ltm.sort
              ,lpt.act_dt AS act_dt
              ,lpt.clear_dt AS clear_dt
              ,lpt.plan_de
              ,DATE_FORMAT(lpt.plan_de, '%Y') AS yy
              ,DATE_FORMAT(lpt.plan_de, '%m') AS mm
              ,DATE_FORMAT(lpt.plan_de, '%d') AS dd
              ,CASE WHEN DAYNAME(lpt.plan_de) = 0 THEN '월'
                    WHEN DAYNAME(lpt.plan_de) = 1 THEN '화'
                    WHEN DAYNAME(lpt.plan_de) = 2 THEN '수'
                    WHEN DAYNAME(lpt.plan_de) = 3 THEN '목'
                    WHEN DAYNAME(lpt.plan_de) = 4 THEN '금'
                    WHEN DAYNAME(lpt.plan_de) = 5 THEN '토'
                    WHEN DAYNAME(lpt.plan_de) = 6 THEN '일'
               END AS ww
              ,'' AS contents_xml_type
              ,'' AS media_time
              ,'' AS study_duration
        FROM tz_lms_plan_theme lpt
        INNER JOIN tz_lcms_theme_material ltm3
        ON lpt.material_no = ltm.material_no
        WHERE lpt.student_no = '272749'
            AND lpt.plan_de >= '2015.04.27'
            AND lpt.plan_de <= '2015.05.03'
        ORDER BY plan_de;
'''

def extract_sql_sig(sql, tokens=None):
    ret = [];
    
    if sql is not None:
        formatted = sqlparse.format(sql, reindent=True, keyword_case='upper', strip_comments=True)
        parsed = sqlparse.parse(formatted)
        tokens = parsed[0].tokens
        
    for token in tokens:
        if token.is_whitespace():
            pass
        elif token.ttype in (sqlparse.tokens.Literal.String.Single, sqlparse.tokens.Literal.Number.Integer):
            pass
        elif token.is_group():
            ret.append(extract_sql_sig(None, token.flatten()))
        else:
            ret.append(token.value)
    return hash(tuple(ret))
''' example code
sig1 = extract_sql_sig(sql1)
sig2 = extract_sql_sig(sql2)
print(sig1)
print(sig2)
print(sig1 == sig2)
'''