import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import urllib
import json
from time import sleep
import os


url = "https://cn.investing.com/equities/apple-computer-inc-historical-data"
filePath = os.path.abspath(__file__)

class get_info:
    def __init__(self, From, Start, End) :
        self.From = From
        self.Start = Start
        self.End = End

    def serch(self):

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url)

        select_From = Select(driver.find_element(By.ID,"data_interval"))
        select_From.select_by_value(self.From)

        jss='document.getElementById("picker").value="' + self.Start + ' - ' + self.End + '";'
        driver.execute_script(jss)

        jss = 'document.getElementById("widgetFieldDateRange").click();'
        driver.execute_script(jss)
        jss = 'document.getElementById("applyBtn").click();'
        driver.execute_script(jss)
        sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", {"id": "curr_table"})

        columns = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]
        columns[1:]
        
        trs = table.find_all('tr')[1:]
        rows = list()
        for tr in trs:
            rows.append([td.text.replace('\n', '').replace('\xa0', '') for td in tr.find_all('td')])
        data = {}

        for row in rows:
            buffer = {}
            for i in range(6):
                buffer[columns[i+1]] = row[i+1]
            data[row[0]] = buffer
        print(data)
        return data
        



print("====================================")
print("\n")
print("蘋果股價搜索")
print("\n")
print("====================================")
print("\n")
print("\n")

print("請輸入搜索單位 (Daily/Weekly/Monthly)")
dateFrom = input()
print("請輸入搜索起始日期 (format : yyyy/mm/dd)")
startDate = input()
print("請輸入搜索結束日期 (format : yyyy/mm/dd)")
endDate = input()

a = get_info(dateFrom,startDate,endDate)
data = a.serch()

with open (os.path.join(__file__,'out_put.json'),'w', encoding='UTF-8') as f:
    json.dump(data, f, ensure_ascii=False)