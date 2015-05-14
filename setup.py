# coding: utf-8
'''
Created on 2015. 5. 13.

@author: hoonja
'''
# -*- coding: utf-8 -*-
from setuptools import setup

# name, description, version등의 정보는 일반적인 setup.py와 같습니다.
setup(name="ql2xlsx",
      description="convert a query log file to a excel formatted file.",
      version="0.0.1",
      # 설치시 의존성 추가
      setup_requires=["py2app"],
      app=["qlanalyze.py"],
      options={
          "py2app": {
              # PySide 구동에 필요한 모듈들은 포함시켜줍니다.
              "includes": ["sys",
                           "time",
                           "sqlparse",
                           "xlsxwriter"]
          }
      })