# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 22:01:57 2020

@author: Yiming Wang
"""

import xlrd
import xlwt



def read():
    a=0
    flie_name='1.xlsx'
    wb=xlrd.open_workbook(filename=flie_name)
    table=wb.sheets()[0]
    rows_num=table.nrows
    for i in range(rows_num):
        value=table.cell_value(i,0)
        print(value)
        if int(value) > 213:
            a+=1
    print(a)
    
def creat():  #不可以向老的里边写入，但是可以创建新的进行覆盖
    open_file_initial=input("输入要打开excel表格: ")
    while True:
        try:
            file=open(open_file_initial,encoding="utf-8")#open file
        except FileNotFoundError:
            book = xlwt.Workbook(encoding='utf-8')     #cell_overwrite_ok=True)   
            sheet1 = book.add_sheet('1')
            sheet1.write(2,0,34) #行 列
            book.save("TT.xls")  #(r'D:\PycharmProjects\test.xlsx') 设定地址保存
            print('创建一个新的成功')
            break
        except Exception as e:
            print(str(e))
            break

 
def open_file():
    open_file_initial=input("输入要打开excel表格: ")
    while True:
        try:
            #file=open(open_file_initial+'.xlsx',encoding="utf-8")#open file #read 操作
            file=xlrd.open_workbook(open_file_initial+'.xls')
            print('打开表格')
            return file
        except Exception as e:
            print(str(e))
            break
                       
    
def write(airIDlist,pricelist,timelist):
    file=open_file()
    sheets=file.sheet_names() #获取所有sheet
    sheet1=file.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格

    for i in range(len(airIDlist)):
        sheet1.write(i,1,airIDlist[i])
        sheet1.write(i,2,pricelist[i])
        sheet1.write(i,3,timelist[i])
    file.save() #创建保存文件
    


if __name__ == "__main__":

    value_title = [["姓名", "性别", "年龄", "城市", "职业"],]

    value1 = [["张三", "男", "19", "杭州", "研发工程师"],
              ["李四", "男", "22", "北京", "医生"],
              ["王五", "女", "33", "珠海", "出租车司机"],]

    value2 = [["Tom", "男", "21", "西安", "测试工程师"],
              ["Jones", "女", "34", "上海", "产品经理"],
              ["Cat", "女", "56", "上海", "教师"],]

    creat()