# 输入位于的城市
import io
import sys
import csv
import requests
import pandas as pd
import numpy as np


class city_search_form():

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')

    #查询首字母
    def label(name):
        try:
            file1 = pd.read_csv(r'地区.csv',encoding='gb18030')
            #print(file1)
            file1 = np.array(file1)
            #print(file1)
            data = []
            for item in file1:
                sh = item[0]
                #print(sh)
                if name == sh:
                    #print(item)
                    data.append(item)
            print(data)
        except csv.Error as e:
          print("程序异常，请检查输入")

    #查询城市名称
    def city(name):
        try:
            file1 = pd.read_csv(r'地区.csv', encoding='gb18030')
            # print(file1)
            file1 = np.array(file1)
            # print(file1)
            data = []
            for item in file1:
                sh = item[1]
                # print(sh)
                if name == sh:
                    print(item)
                    data.append(item)
            # print(data)
        except csv.Error as e:
            print("程序异常，请检查输入")


    #检索
    def search(self):
        global href
        global content
        href = input("请输入你所查询的地区的链接：")
        content = input("请输入你要搜索的内容：")
        url = f"https:{href}/s/{content}/"
        response = requests.get(url=url)
        res = response.text
        print(res)




if __name__ == "__main__":
    print("————————城市查询————————")
    print("1、首字母查询")
    print("2、全称查询")
    #tp为要查询的类型
    tp = input("请输入你要查询的类型：")
    if tp == "1":
        name = input("请输入要查询的首字母（大写）：")
        city_search_form.label(name)
        city_search_form.search()
    elif tp == "2":
        name = input("请输入要查询的城市名称：")
        city_search_form.city(name)
        city_search_form.search()