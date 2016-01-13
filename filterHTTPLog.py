'''
Created on 2015. 7. 3.

@author: hoonja
'''
import sys

def filterHttpLog (logfile, outfile):
    inf = open(logfile)
    line = inf.readline()
    outf = open(outfile, "w")
    while line:
        result = line.lower()
        #if "HTTP/1.1\" 500" in result or "<script" in result:
        if "<script" in result:
            outf.writelines(line)
        line = inf.readline()
    outf.close()
    inf.close()
    
# Start Point
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("This program is for extracting query information and is for saving CSV type file.")
        print("Usage : log_file_name out_file_name")
        sys.exit()
    filterHttpLog(sys.argv[1], sys.argv[2])