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

    @gulby : 나중에 pandas 를 써보자...
    '''
    f = open(fname)
    curTime = time.strptime('150427', '%y%m%d')  #기본값

    result_set = []
    line = f.readline()
    exitCount = 0
    while line and exitCount < 100:
        if line[0] == '#':
            qi = QueryItem()

            # 땜빵
            if '# administrator command: Prepare;' in line:
                line = f.readline()

            # 시간 정보
            if '# Time: ' in line:
                curTime = time.strptime(line.replace('# Time: ', '').replace('\n', '').replace('\r', ''), '%y%m%d %H:%M:%S')
                line = f.readline()
                #print('curTime : ', curTime)
            qi.Time = qi.MaxTime = qi.MinTime = curTime

            # User 정보
            if '# User@Host: ' in line:
                userinfo = line.replace('# User@Host: ', '').replace(' ', '').replace('\n','').replace('\r', '').split('@')
                qi.User = userinfo[0]
                qi.Host = userinfo[1].replace('[','').replace(']','')
                #print(qi.User, qi.Host)
                line = f.readline()

            # 땜빵
            if '# Thread_id: ' in line:
                line = f.readline()

            # Query_time, Lock_time, Rows_sent, Rows_examined
            if '# Query_time: ' in line:
                queryinfo = line.replace('# Query_time: ', '').replace(' Lock_time: ', '').replace('Rows_sent: ', '').replace(' Rows_examined: ', '').replace('\n', '').replace('\r', '').split(' ')
                #print(queryinfo)
                qi.Query_time = float(queryinfo[0])
                qi.Lock_time = float(queryinfo[1])
                qi.Rows_sent = int(queryinfo[2])
                qi.Rows_examined = int(queryinfo[3])
                #print(qi.Query_time, qi.Lock_time, qi.Rows_sent, qi.Rows_examined)
            line = f.readline()

            while line and line[0] != '#':
                if ('use ' in line or 'USE ' in line) and (';' in line): #땜빵 수정.. ';' 검색 부분이 없으면, 일반 코드에 use가 들어가는 경우도 걸러짐. 정규식을 쓰는 것이 정석
                    line = f.readline()
                if 'SET timestamp=' in line:
                    line = f.readline()
                if line and line[0] != '#':
                    #qi.QueryString += line.replace('\n', ' ').replace('\r', '')
                    a = line.rstrip('\r\n') + '\r\n'
                    qi.QueryString += line.rstrip('\r\n') + '\r\n'
                    line = f.readline()
            # print(qi.QueryString)
            if qi.QueryString != '':
                qi.HashVal = extract_sql_sig(qi.QueryString)
                print(qi.HashVal)
            #qi.QueryString = sqlparse.format(qi.QueryString, reindent=True, keyword_case='upper', strip_comments=False)
                result_set.append(qi)
        else:
            line = f.readline()
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
    col = 0
    ws.write(row, col, 'sig'); col += 1;
    ws.write(row, col, 'time'); col += 1;
    ws.write(row, col, 'max_time'); col += 1;
    ws.write(row, col, 'min_time'); col += 1;
    ws.write(row, col, 'user'); col += 1;
    ws.write(row, col, 'host'); col += 1;
    ws.write(row, col, 'query_time'); col += 1;
    ws.write(row, col, 'lock_time'); col += 1;
    ws.write(row, col, 'rows_send'); col += 1;
    ws.write(row, col, 'rows_examined'); col += 1;
    ws.write(row, col, 'count'); col += 1;
    ws.write(row, col, 'check'); col += 1;
    ws.write(row, col, 'org'); col += 1;
    ws.write(row, col, 'tuning'); col += 1;
    #ws.write(row, col, 'format'); col += 1;
    for qi in queryList:
        row += 1
        col = 0
        ws.write(row, col, unicode(qi.HashVal)); col += 1;
        ws.write(row, col, time.strftime('%Y-%m-%d %H:%M:%S', qi.Time)); col += 1;
        ws.write(row, col, time.strftime('%Y-%m-%d %H:%M:%S', qi.MaxTime)); col += 1;
        ws.write(row, col, time.strftime('%Y-%m-%d %H:%M:%S', qi.MinTime)); col += 1;
        ws.write(row, col, qi.User); col += 1;
        ws.write(row, col, qi.Host); col += 1;
        ws.write(row, col, qi.Query_time); col += 1;
        ws.write(row, col, qi.Lock_time); col += 1;
        ws.write(row, col, qi.Rows_sent); col += 1;
        ws.write(row, col, qi.Rows_examined); col += 1;
        ws.write(row, col, qi.count); col += 1;
        ws.write(row, col, ''); col += 1;
        str = sqlparse.format(qi.QueryString, reindent=False, strip_comments=False)
        ws.write(row, col, str.replace('\r', ' ').replace('\n', ' ').replace('    ', ' ').replace('  ', ' '))
        ws.write_comment(row, col, str, {'width':800, 'height':600}); col += 1;
        ws.write(row, col, '...');
        ws.write_comment(row, col, '', {'width':800, 'height':600}); col += 1;
        #str = sqlparse.format(str, reindent=True, keyword_case='upper', identifier_case='lower', strip_comments=True, indent_tabs=False, indent_width=4)
        #str = sqlparse.format(str, reindent=True, keyword_case='upper', identifier_case='lower', strip_comments=True, indent_tabs=True, indent_width=1)
        #ws.write(row, col, '...');
        #ws.write_comment(row, col, str, {'width':800, 'height':600}); col += 1;
    workbook.close()

def filterQueryList(orgql, ignore_sigs=None):
    '''
    인자로 주어진 QueryItem List에서 특정 조건에 부합하는 쿼리들은 제거하고 반환
    현재의 필터링 조건은 1) 새벽 2~8시 사이, 2) user가 root, 3) host IP가 211.117.172.107 인 경우 or localhost 일
    '''
    result_set = []
    for qi in orgql:
        if qi.Time.tm_hour >= 2 and qi.Time.tm_hour < 8:
            continue
        if qi.User == 'root[root]':
            continue
        if qi.Host == '220.117.172.107' or qi.Host == 'localhost':
            continue
        if ignore_sigs and ignore_sigs.get(qi.HashVal, 0) == 1:
            continue
        result_set.append(qi)
    return result_set;

def getIgnoreSigs(fname=None):
    if fname == None or fname == '':
        return None
    f = open(fname)
    result_dic = {}
    for line in f:
        result_dic[int(line)] = 1
    return result_dic;

def groupQueryList(orgql):
    '''
    인자로 주어진 QueryItem 리스트에서 중복된 쿼리를 제거한 후 반환
    '''
    orgql.sort(key=lambda x : x.HashVal)
    cur_hash = 0
    result_set = []
    for qi in orgql:
        if cur_hash == qi.HashVal:
            result_set[-1].count += 1
            if result_set[-1].MaxTime <= qi.Time:
                result_set[-1].MaxTime = qi.Time
            if result_set[-1].MinTime >= qi.Time:
                result_set[-1].MinTime = qi.Time
        else:
            result_set.append(qi)
            cur_hash = qi.HashVal
    result_set.sort(key=lambda x : (x.User, x.Host, -x.Rows_examined*x.count))
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
    count = 1
    MaxTime = time.strptime('150427', '%y%m%d')
    MinTime = time.strptime('150427', '%y%m%d')

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
    if len(sys.argv) < 3:
        print("This program is for extracting query information and is for saving CSV type file.")
        print("Usage : log_file_name xlsx_file_name")
        sys.exit()
    print('STEP 1 : Parsing query log...')
    ql = parseQueryLog(sys.argv[1])
    print(len(ql), ' queries extracted from log file')

    print('STEP 2 : Grouping query...')
    ignore_sigs = [];
    if len(sys.argv) == 4:
        #grouped_ql = groupQueryList(filterQueryList(ql, getIgnoreSigs(sys.argv[3])))
        grouped_ql = filterQueryList(groupQueryList(ql), getIgnoreSigs(sys.argv[3]))
    else:
        grouped_ql = groupQueryList(filterQueryList(ql))

    print('STEP 3 : Saving result...')
    #saveToCSVFile(sys.argv[2], grouped_ql)
    saveToExcelFile(sys.argv[2], grouped_ql)
    print('done')
