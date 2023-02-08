import re
import requests
import schedule
import csv
import pandas
import statistics
import os
import time 
import matplotlib.pyplot as plt
from datetime import datetime
HTTP_NOTIFICATION=True
EMAIL_NOTIFICATION=False
USE_API=True
API_FIELD="api_key"
API_KEY="FFDDF73E-C599-4E95-B70A-A2797B6FF344"
http_address="http://localhost:8081/exchange-rate-monitor/event"
DELTA_TH=5
VAR_TH=0.5
LONG_DATA=10
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def clean():
    exist=os.path.exists('data.csv')
    if exist==True:
        df = pandas.read_csv('data.csv')
        df_new=df.tail(LONG_DATA)
        df_new.to_csv("data.csv", index=False)
def send_mail(Message):
    #sender
    from_addr = 'username@email.domain.name'
    password = 'password'
    #Receiver
    to_addr = 'username@email.domain.name'
    #Send Server
    smtp_server = 'smtp.email.domain.name'
    text="<html><body><h1>Exchange Rate Monitor Notification</h1><p>"+Message+"</p></body></html>"

    msg = MIMEText(text, 'text/html', 'UTF-8')
    # 邮件头信息
    msg['From'] = Header('Exchange Rate Monitor')
    msg['To'] = Header('User')
    subject = '[NO REPLY]Exchange Rate Monitor Event'
    msg['Subject'] = Header(subject, 'UTF-8')

    try:
        smtpobj = smtplib.SMTP_SSL(smtp_server)
        smtpobj.connect(smtp_server, 465)
        smtpobj.login(from_addr, password)
        smtpobj.sendmail(from_addr, to_addr, msg.as_string())
        print("E-mail nofification sent.")
    except smtplib.SMTPException:
        print("E-mail notiiication failed.")
    finally:
        # 关闭服务器
        smtpobj.quit()

def notify(__type,__value):
    if HTTP_NOTIFICATION==True:
        try:
            appendix=""
            if USE_API:
                appendix="&"+API_FIELD+"="+API_KEY
            requests.get(http_address+"?type="+str(__type)+"&value="+str(__value)+appendix)
        except:
            print("Cannot notify via http.")
    if EMAIL_NOTIFICATION==True:
        try:
            send_mail(__type+" term change, value: "+str(__value))
        except:
            print("Cannot notify via e-mail.")
def plot():
    df = pandas.read_csv('data.csv')
    if len(df.index)>=2:
        A=df['BSP'].take([-1])
        B=df['BSP'].take([-2])
        delta=float(A)-float(B)
        print("Difference between last two concurrency:"+str(delta))
        variance=statistics.variance(df['BSP'].tail(LONG_DATA))
        print("Variance of last "+str(LONG_DATA)+" data is :"+str(variance))
        if delta>DELTA_TH:
            notify("short",delta)
        if variance>VAR_TH:
            notify("long",variance)
    plt.grid(True)
    plt.tight_layout()
    
    df.tail(LONG_DATA).plot()
    plt.savefig('Analysis.png')
def job():
    content = '澳门元'
    url = 'http://www.boc.cn/sourcedb/whpj/index.html'  #外汇数据地址
    html = requests.get(url).content.decode('utf-8')
    index = html.index('<td>' + content + '</td>')
    s = html[index:index+350]
    result = re.findall('<td>(.*?)</td>',s)
    date = re.findall('<td class="pjrq">(.*?)</td>',s)
    print("币种：" + result[0])
    print("现汇买入价：" + result[1])
    print("现钞买入价：" + result[2])
    print("现汇卖出价：" + result[3])
    print("现钞卖出价：" + result[4])
    print("中行结算价：" + result[5])
    print("发布时间：" + result[6])
    print("发布日期："+date[0])
    exist=os.path.exists('data.csv')
    if exist==False:
        _csv_obj = open('data.csv', 'w', encoding="utf-8", newline="")
        # 现汇买入价 Foreign Remittance Buying Rate - FRBR
        # 现钞买入价 Foreign Cash Buying Rate - FCBR
        # 现汇卖出价 Foreign Remittance Sellings Rate - FRSR
        # 现汇卖出价 Foreign Cash Sellings Rate - FCSR
        # 中行结算价 Bank Settlement Price - BSP
        # 发布日期 Date
        csv.writer(_csv_obj).writerow(["Date","Currency", "FRBR", "FCBR", "FRSR", "FCSR","BSP"])
        _csv_obj.close()
    if os.path.getsize('data.csv')==0:
        _csv_obj = open('data.csv', 'w', encoding="utf-8", newline="")
        csv.writer(_csv_obj).writerow(["Date","Currency", "FRBR", "FCBR", "FRSR", "FCSR","BSP" ])
        _csv_obj.close()
    csv_obj = open('data.csv', 'a', encoding="utf-8", newline="")
    a0=result[0]
    a1=result[1]
    a2=result[2]
    a3=result[3]
    a4=result[4]
    a5=result[5]
    # a6=date[0]
    a6=datetime.now()
    csv.writer(csv_obj).writerow([a6,a0,a1,a2,a3,a4,a5])
    csv_obj.close()
    print("Data Gathered")
    print("Plotting Data")
    plot()
    clean()
#every() accepts seconds.
schedule.every(15).seconds.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
