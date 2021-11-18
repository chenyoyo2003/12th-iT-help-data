# -*- coding: utf-8 -*-
"""
"""
#載入LineBot所需要的套件
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import os
import time
import re
import random
import json
import requests

app = Flask(__name__)

#======測試==========
# Channel Access Token
line_bot_api = LineBotApi('QLdQ49iminM9vWWNHBX/lEXE5Y6Nufzu1YLPsQnRMXwy22aDO/XUeCzFOKsw5Y+REgpPVSZYdjTIdBkkb6YEoT63p4zfFehfRpwN7lbVD/Z6rCt3v/29KXxQkGfeER6NNfCcTamC5YSQiP2ZRehbngdB04t89/1O/w1cDnyilFU=')
# Channel Secret 
handler = WebhookHandler('e21b7c4fcde587a113145986d76bd68d')
line_bot_api.push_message('U41640217301124092e0eb4b6fd6bd49e', TextSendMessage(text='你可以開始了'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

cities = ['基隆市','嘉義市','臺北市','嘉義縣','新北市','臺南市','桃園縣','高雄市','新竹市','屏東縣','新竹縣','臺東縣','苗栗縣','花蓮縣','臺中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']   

def get(city):
    token = 'CWB-CE79A203-7B52-4458-B396-210934B251BA'
    urs = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(urs)
    print(Data)
    print(Data.json())
    Data = (Data.json())['records']['location'][0]['weatherElement']
    res = [[] , [] , []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    return res

# Message event
@handler.add(MessageEvent)
def handle_message(event):
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text
    if(message[:2] == '天氣'): #要前面2個
         city = message[3:] #前面3個省略
         city = city.replace('台','臺')
         if(not (city in cities)):
                 line_bot_api.reply_message(reply_token,TextSendMessage(text="查詢格式為: 天氣 縣市"))
         else:
             res = get(city)
             for data in res:
                 message = TemplateSendMessage(
                    alt_text = city + '未來 36 小時天氣預測',
                    template = CarouselTemplate(
                        columns = [
                            CarouselColumn(
                               thumbnail_image_url = 'https://i.imgur.com/Ex3Opfo.png',
                               title = '{} ~ {}'.format(res[0][0]['startTime'][5:-3],res[0][0]['endTime'][5:-3]),
                               text = '天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(data[0]['parameter']['parameterName'],data[2]['parameter']['parameterName'],data[4]['parameter']['parameterName'],data[1]['parameter']['parameterName']),
                               actions = [
                                   URIAction(
                                       label = '詳細內容',
                                       uri = 'https://www.cwb.gov.tw/V8/C/W/County/index.html'
                                    )
                                ]
                            )
                        ]
                    )
                 )
         line_bot_api.reply_message(reply_token, TextSendMessage(message))
                                   
#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
