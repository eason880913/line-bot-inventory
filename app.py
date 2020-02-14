from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import psycopg2
import re
import time
#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *
#======這裡是呼叫的檔案內容=====

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('621GPo280uX4vTgf/+NyT3Mc+aQONQWzINlN5A84IcA2uSrxdlIrWDILl/A7Rd7BKWyH6iaKG47/UB7DO3kJwyA/ZJzKFvWfbYMbs4STIc7dW5k44WEq0k8/50pZ2Z0qGU42zqCQ3LWT+kC5XRvXbgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('35952d9441a70ce3f68ac9b7d14072df')

def db():
    connection = psycopg2.connect(user="slbztsvvycydaq",
                                        password="f1666cafab9d2467fa444158bf8c2f7a99aaef2a71dd126590a42508f5981bdc",
                                        host="ec2-3-234-169-147.compute-1.amazonaws.com",
                                        port="5432",
                                        database="db2lsctsu2ueqh")
    cursor = connection.cursor()
    return cursor
cursor = db()

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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #try:

    #info
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    all_data =''
    sum_num = 0
    group_id = event.source.group_id
    table_name = 'inventroy'+str(group_id)
    record_table_name = 'record'+str(group_id)
    #print(table_name)
    msg = event.message.text
    msg_num = re.findall(r'\w+',msg)

    if '新增商品' in msg:
        #info
        inventory_name = msg_num[1]
        inventory_dollars = msg_num[2]
        inventory_dollars = re.sub(r'\D','',inventory_dollars)
        inventory_num = msg_num[3]
        inventory_num = re.sub(r'\D','',inventory_num)

        if len(msg_num)>4:
            User_ID = TextSendMessage(text='錯誤格式')
            line_bot_api.reply_message(event.reply_token, User_ID)
        if len(msg_num)<4:
            User_ID = TextSendMessage(text='錯誤格式')
            line_bot_api.reply_message(event.reply_token, User_ID)
        elif len(msg_num)==4:
            try:
                cursor.execute(f'CREATE TABLE "public"."{table_name}" ("id" serial,"inventory" varchar UNIQUE,"dollars" varchar,"number_" varchar, PRIMARY KEY ("id"));')
                cursor.execute("COMMIT")
            except:
                print('table already exist')
                cursor.execute("ROLLBACK")
            try:
                cursor.execute(f'INSERT INTO "public"."{table_name}" ("inventory","dollars","number_")'+f"VALUES ('{inventory_name}', '{inventory_dollars}', '{inventory_num}');")
                cursor.execute("COMMIT")
            except:
                insert = TextSendMessage(text='商品已經存在')
                line_bot_api.reply_message(event.reply_token, insert)
                cursor.execute("ROLLBACK")
            insert_ = TextSendMessage(text='新增完成')
            line_bot_api.reply_message(event.reply_token, insert_)
            
    if '查詢剩餘存貨' == msg:
        try:
            cursor.execute(f'SELECT * FROM "public"."{table_name}";')
            data = cursor.fetchall()
            for i in data:
                all_data=all_data+i[1]+' '+i[2]+'元 '+i[3]+'個 '+'\n'
            User_ID = TextSendMessage(text=all_data)
            line_bot_api.reply_message(event.reply_token, User_ID)
        except:
            User_ID = TextSendMessage(text='沒有任何商品')
            line_bot_api.reply_message(event.reply_token, User_ID)  

    if '刪除商品' in msg:
        #info
        inventory_name = msg_num[1]
        if len(msg_num)>2:
            User_ID = TextSendMessage(text='錯誤格式')
            line_bot_api.reply_message(event.reply_token, User_ID)
        if len(msg_num)<2:
            User_ID = TextSendMessage(text='錯誤格式')
            line_bot_api.reply_message(event.reply_token, User_ID)
        elif len(msg_num)==2:
            try:
                cursor.execute(f'DELETE FROM "public"."{table_name}" WHERE "inventory"'+f"= '{inventory_name}';" )
                cursor.execute("COMMIT")
                ddd = TextSendMessage(text='刪除完成')
                line_bot_api.reply_message(event.reply_token, ddd)
            except:
                ddd = TextSendMessage(text='沒有此商品')
                line_bot_api.reply_message(event.reply_token, ddd)
                cursor.execute("ROLLBACK")
    
    if '刪除全部商品' == msg:
        cursor.execute(f'TRUNCATE "public"."{table_name}";')
        cursor.execute("COMMIT")
        delete_all = TextSendMessage(text='全部刪除完成')
        line_bot_api.reply_message(event.reply_token, delete_all)

    if '賣出商品' in msg:
        inventory_name = msg_num[1]
        inventory_num = msg_num[2]
        inventory_num = re.sub(r'\D','',inventory_num)
        if len(msg_num)>3:
            User_ID = TextSendMessage(text='錯誤格式')
            line_bot_api.reply_message(event.reply_token, User_ID)
        if len(msg_num)<3:
            User_ID = TextSendMessage(text='錯誤格式')
            line_bot_api.reply_message(event.reply_token, User_ID)
        elif len(msg_num)==3:
            try:
                cursor.execute(f'CREATE TABLE "public"."{record_table_name}" ("id" serial,"inventory" varchar ,"number_" int4,"time_" varchar, PRIMARY KEY ("id"));')
                cursor.execute("COMMIT")
            except:
                print('table already exist')
                cursor.execute("ROLLBACK")

            try:
                cursor.execute(f'SELECT number_ FROM "public"."{table_name}"'+f"WHERE inventory = '{inventory_name}';")
                data = cursor.fetchall()
                num_inventory = int(data[0][0])-int(inventory_num)
                cursor.execute(f'UPDATE "public"."{table_name}" SET "number_"'+f"= '{num_inventory}'"+'WHERE "inventory"'+f" = '{inventory_name}';")
                cursor.execute("COMMIT")
                User_ID = TextSendMessage(text='紀錄完畢')
                line_bot_api.reply_message(event.reply_token, User_ID)
            except:
                User_ID = TextSendMessage(text='無此商品')
                line_bot_api.reply_message(event.reply_token, User_ID)

            cursor.execute(f'INSERT INTO "public"."{record_table_name}" ("inventory","number_","time_")'+f"VALUES ('{inventory_name}', '{inventory_num}', '{time_now}');")
            cursor.execute("COMMIT")
            
    if '營收' in msg:
        cursor.execute(f'SELECT "inventory", SUM("number_") FROM "{record_table_name}" GROUP BY "inventory";')
        data_record_all= cursor.fetchall()
        for l in data_record_all:
            try:
                print(l[0])
                cursor.execute(f'SELECT dollars FROM "public"."{table_name}"'+f"WHERE inventory = '{l[0]}';")
                data_record = cursor.fetchall()
                print(data_record[0][0])
                print(l[1])
            except:
                User_ID = TextSendMessage(text=f'{l[0]}沒有在產品清單裡')
                line_bot_api.reply_message(event.reply_token, User_ID)
            sum_num += int(data_record[0][0])*l[1]
        User_ID = TextSendMessage(text=sum_num)
        line_bot_api.reply_message(event.reply_token, User_ID)
    '''
    if '滾' == msg:
        User_ID = TextSendMessage(text = "滾去你旁邊～可以嗎\udbc0\udc8a")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '我愛你' == msg:
        User_ID = TextSendMessage(text = "我也愛你\udbc0\udc96")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '閉嘴' == msg:
        User_ID = TextSendMessage(text = "泂泂是妳嗎？\udbc0\udc85")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '莊旻達是誰' == msg:
        User_ID = TextSendMessage(text = "是帥氣又大方的老師，會買飲料給學生，對學生最好了\udbc0\udc78")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '誰最挑食' == msg:
        User_ID = TextSendMessage(text = "我不敢說，她會瞪我\udbc0\udc9f")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '好想要喝酒' == msg:
        User_ID = TextSendMessage(text = "沛青是妳嗎？\udbc0\udc85")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '姐夫～～' == msg:
        User_ID = TextSendMessage(text = "你在叫哪一個？\udbc0\udc8c")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '要拍照囉'== msg:
        User_ID = TextSendMessage(text = "戳右邊的臉")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '我最美' == msg:
        User_ID = TextSendMessage(text = "天母說謊怪\udbc0\udc0d")
        line_bot_api.reply_message(event.reply_token, User_ID)
    if '我最美' == msg:
        User_ID = TextSendMessage(text = "天母說謊怪\udbc0\udc0d")
        line_bot_api.reply_message(event.reply_token, User_ID)
    '''    




    #except:
    user_id = event.source.user_id
    print('Reply User ID =>' + user_id)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
