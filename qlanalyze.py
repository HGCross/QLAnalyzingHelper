# coding: utf-8
'''
@author: hoonja
@editor: gulby
'''
import sys
import time
import sqlparse
import xlsxwriter

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

def parseQueryLog(fname):
    '''
    query log를 분석하여, QueryItem 형식의 인스턴스 리스트를 반환하는 함수로, 분석 대상이 되는 query log는 아래와 같은 형식의 문단이 계속되는 형태이다.
    # Time: 150427  3:10:58
    # User@Host: root[root] @ localhost []
    # Query_time: 49.532116  Lock_time: 0.000000 Rows_sent: 24596040  Rows_examined: 24596040
    use edubasestudydb;
    SET timestamp=1430071858;
    SELECT /*!40001 SQL_NO_CACHE */ * FROM `t_student_errnote`;
    '''
    f = open(fname)
    curTime = time.strptime('150427', '%y%m%d')  #기본값
    
    result_set = []
    line = f.readline()    
    exitCount = 0
    while line and exitCount < 100:
        if line[0] == '#':
            qi = QueryItem()

            # 시간 정보 
            if '# Time: ' in line:
                curTime = time.strptime(line.replace('# Time: ', '').replace('\n', '').replace('\r', ''), '%y%m%d %H:%M:%S')
                line = f.readline()
                #print('curTime : ', curTime)
            qi.Time = curTime            
            
            # User 정보
            if '# User@Host: ' in line:
                userinfo = line.replace('# User@Host: ', '').replace(' ', '').replace('\n','').replace('\r', '').split('@')
                qi.User = userinfo[0]
                qi.Host = userinfo[1].replace('[','').replace(']','')
                #print(qi.User, qi.Host)            
            line = f.readline()
            
            # Query_time, Lock_time, Rows_sent, Rows_examined
            #if line.find('# Query_time: ') != 1:
            if '# Query_time: ' in line:
                queryinfo = line.replace('# Query_time: ', '').replace(' Lock_time: ', '').replace('Rows_sent: ', '').replace(' Rows_examined: ', '').replace('\n', '').replace('\r', '').split(' ')
                qi.Query_time = queryinfo[0]
                qi.Lock_time = queryinfo[1]
                qi.Rows_sent = queryinfo[2]
                qi.Rows_examined = queryinfo[3]
                #print(qi.Query_time, qi.Lock_time, qi.Rows_sent, qi.Rows_examined)
            line = f.readline()
            
            while line and line[0] != '#':
                if 'use ' in line or 'USE ' in line:
                    line = f.readline()
                if 'SET timestamp=' in line:
                    line = f.readline()
                #qi.QueryString += line.replace('\n', ' ').replace('\r', '')
                qi.QueryString += line.rstrip('\r\n') + '\r\n'
                line = f.readline()
            qi.HashVal = extract_sql_sig(qi.QueryString)
            #qi.QueryString = sqlparse.format(qi.QueryString, reindent=True, keyword_case='upper', strip_comments=False)
            result_set.append(qi)
        #exitCount += 1
    #for i in range(100):
    #    result_set.append(QueryItem())
    return result_set

def saveToCSVFile(fname, queryList):
    '''
    fname의 이름을 갖는 csv파일을 생성하여, queryList를 csv 타입의 문자열로 변환후 저장해주는 함수
    '''
    f = open(fname, 'w')
    f.writelines(QueryItem.getCSVHeaderString())
    for queryItem in queryList:
        #print(queryItem.convertToCSVString())
        f.writelines(queryItem.convertToCSVString())
    f.close()

def saveToExcelFile(fname, queryList):
    '''
    다른 부분 구조의 전반적인 리팩토링 필요
    일단 리팩토링 없이 구현
    '''
    workbook = xlsxwriter.Workbook(fname)
    ws = workbook.add_worksheet()
    #'time,user,host,query_time,lock_time,rows_send,rows_examined,query_string\n'
    row = 0
    ws.write(row, 0, 'time')
    ws.write(row, 1, 'user')
    ws.write(row, 2, 'host')
    ws.write(row, 3, 'query_time')
    ws.write(row, 4, 'lock_time')
    ws.write(row, 5, 'rows_send')
    ws.write(row, 6, 'rows_examined')
    ws.write(row, 7, 'query_string')
    for qi in queryList:
        row += 1
        ws.write(row, 0, time.strftime('%Y-%m-%d %H:%M:%S', qi.Time))
        ws.write(row, 1, qi.User)
        ws.write(row, 2, qi.Host)
        ws.write(row, 3, qi.Query_time)
        ws.write(row, 4, qi.Lock_time)
        ws.write(row, 5, qi.Rows_sent)
        ws.write(row, 6, qi.Rows_examined)
        str = sqlparse.format(qi.QueryString, reindent=False, strip_comments=False)
        ws.write(row, 7, str.replace('\r', ' ').replace('\n', ''))
        ws.write_comment(row, 7, str, {'width':800, 'height':600})
    workbook.close()

def groupQueryList(orgql):
    '''
    인자로 주어진 QueryItem 리스트에서 중복된 쿼리를 제거한 후 반환
    '''
    result_set = []
    hashdic = {}
    for qi in orgql:
        if qi.HashVal not in hashdic:
            result_set.append(qi)
            hashdic[qi.HashVal] = True
    return result_set

class QueryItem:
    Time = time.strptime('150427', '%y%m%d')
    User = 'root[root]'
    Host = 'localhost[]'
    Query_time = 49.532116
    Lock_time = 0.000000
    Rows_sent = 24596040
    Rows_examined = 24596040
    QueryString = ''
    HashVal = 0
    
    @classmethod
    def getCSVHeaderString(cls):
        return 'time,user,host,query_time,lock_time,rows_send,rows_examined,query_string\n'

    def convertToCSVString(self):
        record = time.strftime('%Y-%m-%d %H:%M:%S', self.Time) + ','
        record += self.User + ','
        record += self.Host + ','
        record += str(self.Query_time) + ','
        record += str(self.Lock_time) + ','
        record += str(self.Rows_sent) + ','
        record += str(self.Rows_examined) + ','
        record += '"' + self.QueryString + '"\n'
        return record

# Start Point
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("This program is for extracting query information and is for saving CSV type file.")
        print("Usage : log_file_name csv_file_name")
        sys.exit()
    print('Started to parse query log...')
    ql = parseQueryLog(sys.argv[1])
    print('done')
    print(len(ql), ' queries extracted to file')
    grouped_ql = groupQueryList(ql)
    #saveToCSVFile(sys.argv[2], grouped_ql)
    saveToExcelFile(sys.argv[2], grouped_ql)