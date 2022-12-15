# -*- coding: utf-8 -*-
"""
Created on Sun May 29 14:24:13 2022

@author: MY
txt 写入 读取的操作
"""

class Txt():

    def __init__(self, filePath=None):
        '''
        Parameters
        ----------
        filePath : txt文件位置
           确定文件位置进行以下操作 ex： r'C:\XXX.txt'
        Returns
        -------
        None.

        '''
        self.FP= filePath

    def readall(self):
        # 第一种方法  不读取换行符号 不会太吃内存
        lst = []
        with open(self.FP, 'r', encoding='UTF-8') as file:
            while True:
                line = file.readline()
                if not line: break
                lst.append(line.rstrip('\r\n'))
        return lst

    def readlist(self):  # 太大吃内存
        with open(self.FP, 'r', encoding='UTF-8') as file:
            data = file.readlines()  # 直接将文件中按行读到list里，效果与方法2一样
        return data
        
    def readlist(self):
        with open(self.FP, 'r', encoding='UTF-8') as file:
            data = file.readlines()  #直接将文件中按行读到list里，效果与方法2一样
        return data

    def writeall(self,string):
        with open(self.FP,'w', encoding='UTF-8') as f:    #设置文件对象
            f.write(string)                 #将字符串写入文件中

    
    def writelist(self,l=None):
        '''
        l：需要传输lsit 文字
        '''
        with open(self.FP, 'w', encoding='UTF-8') as f:
            for i in l:
                if i.find('\n')!=-1:f.write(i)
                else:f.write(i + '\n')
    def test(self):
        print('导入成功')
        
# li = ['aaa','bbb','ccc']  
# l = 'sdsds'
# Txt(r'F:\代码\飞桨语言处理\UIE_Extraction\Scrapy\test.txt').writeall(l)
