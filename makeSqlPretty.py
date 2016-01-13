# coding: utf-8
'''
Created on 2015. 5. 12.

@author: hoonja
'''
import sqlparse

def makeSqlPretty(sql):
    formatted = sqlparse.format(sql, reindent=True, keyword_case='upper', strip_comments=True)
    return formatted

print (makeSqlPretty("INSERT INTO ishomedb.SDK_SMS_SEND (USER_ID, SCHEDULE_TYPE, SUBJECT, SMS_MSG, NOW_DATE, SEND_DATE, CALLBACK, DEST_COUNT, DEST_INFO)         (SELECT 'sigong3439'         , 1         , '학습 시작 30분전 SMS'                 , CONCAT('[홈런]', c.nm_kor, '님의 홈런 학습 시작 30분 전 입니다. 준비해주세요~')         , DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')         , DATE_FORMAT(DATE_ADD(STR_TO_DATE(CONCAT(DATE_FORMAT(a.plan_de, '%Y%m%d'), TIME_FORMAT(MIN(a.plan_time), '%H%i%s')), '%Y%m%d%H%i%s'), INTERVAL -30 MINUTE), '%Y%m%d%H%i%s')         , '15440910'         , 1           /* 학부모 */                 , CONCAT('batch4^', CONCAT(d.mobile1, d.mobile2, d.mobile3))                       FROM    ishomedb.tz_lms_plan_module a         INNER   JOIN ishomedb.tz_student b         ON      a.student_no = b.student_no         /* 학생 정보 */         LEFT    OUTER JOIN ishomedb.tz_member c         ON      b.student_id = c.user_id         /* 부모 정보 */         INNER   JOIN ishomedb.tz_member d         ON      c.parent_id = d.user_id                   WHERE   b.teacher_id IS NOT NULL         AND     DATE_FORMAT(a.plan_de, '%Y%m%d') = DATE_FORMAT(NOW(), '%Y%m%d')         AND     DATE_FORMAT(a.plan_time, '%H%i%s') >= DATE_FORMAT( DATE_ADD(NOW(), INTERVAL -30 MINUTE), '%H%i%s')                   AND     DATE_FORMAT(NOW(), '%Y%m%d') >= DATE_FORMAT(b.start_de, '%Y%m%d')          AND     DATE_FORMAT(NOW(), '%Y%m%d') <= DATE_FORMAT(b.end_de, '%Y%m%d')                     /* 학부모 */                 AND c.start_sms_yn IN ('Y', 'B')                                 AND CONCAT(d.mobile1, d.mobile2, d.mobile3) IS NOT NULL                       GROUP   BY a.student_no         ORDER   BY a.plan_time); "))
