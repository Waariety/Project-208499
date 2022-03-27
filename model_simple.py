#Import module
from flask import Flask, request, abort
import requests
import random
import json
import csv
import numpy as np
from collections import defaultdict

from linebot import LineBotApi
from linebot.models import *

#Token
ACCESS_TOKEN = 'LJGPQjnwwpFjt4CYp+vpnLblxljPZYSGkzvVTrc4QbgXuTrkXpLYL19Dt9ZhCSFWxFwDllSFHQFEgGv8z0MBE2IH255fFu0ks6ycNaXCDQ+xEwwlmNqY2Xlpbn0JirF0f1E4DnTs4KB+TxCBwMypDwdB04t89/1O/w1cDnyilFU='

#Collect data
word = []
word_other = []
count = 0

class DataStore():
    count_false = 0
    count_true = 0
    a = None
    b = None

data = DataStore()

#Import data
v = []
f = open('/home/AceProject/data/100-vocab.csv')
csv_reader = csv.reader(f)
for line in csv_reader:
  #print(line)
  v.append(line[0])
  v.append(line[1])
  v.append(line[2])

#Create dictionary
res_dct = {v[i]: [v[i + 1],v[i + 2], i//3] for i in range(0, len(v), 3)}
num_words = len(res_dct) # number of words
random_dict = [0]*num_words
for word_, list_ in res_dct.items():
    random_dict[list_[2]] = (word_, list_)

#Create array
def array_and_dict():
    return { 'words' : defaultdict(lambda: defaultdict(int)),
    'meaning' : defaultdict(lambda: defaultdict(int)), 'correct' : 0 , 'wrong' : 0}

#Update
def update(dictionary_add):
    filename = '/home/AceProject/data/sample.json'
    with open(filename, "w") as json_file:
        json.dump(dictionary_add, json_file)

dictionary_add = defaultdict(array_and_dict)

#Flask
app = Flask(__name__)
line_bot_api = LineBotApi(ACCESS_TOKEN)

@app.route('/', methods=['POST','GET'])

#webhook
def webhook():

    if request.method == 'POST':
        payload = request.json
        Reply_token = payload['events'][0]['replyToken']
        print(Reply_token)
        message = payload['events'][0]['message']['text']
        userid = payload['events'][0]['source']['userId']
        print(message)

        if 'Start' in message or 'Of course!' in message :
            data.a = random.sample(res_dct.items(), 2)
            word.clear()
            word.append(data.a)

            word_other.clear()
            word_other.append(data.a[1][1][1])
            word_other.append(data.a[0][1][1])
            word_other.sort()

            buttons_template = ButtonsTemplate(
            title=None, text='Do you know the meaning of\n"'+ data.a[0][0] + '"?', actions=[
                MessageAction(label= word_other[0], text= word_other[0], weight = "bold" , color = "#aaaaaa"),
                MessageAction(label= word_other[1] , text= word_other[1], weight = "bold" , color = "#aaaaaa")
            ])
            template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
            line_bot_api.reply_message(Reply_token, template_message)

        elif data.a[0][1][1] in message :
            #word_other
            #word
            Reply_messasge = 'That is great!\nIt means ' + data.a[0][1][1]
            send_message(Reply_token,Reply_messasge)
            text_message = TextSendMessage(text='Do you want to go next?',
                               quick_reply=QuickReply(items=[
                                   QuickReplyButton(action=MessageAction(label="Of course!", text="Of course!")),
                                   QuickReplyButton(action=MessageAction(label="Take a break", text="See you next time!"))
                               ]))
            line_bot_api.push_message(userid, text_message)
            dictionary_add[userid]['words'][data.a[0][0]]["True"] += 1
            dictionary_add[userid]['meaning'][data.a[0][1][1]]["True"] += 1
            dictionary_add[userid]['correct'] += 1
            update(dictionary_add)
            word.clear()
            #count_true+=1

        elif data.a[1][1][1] in message :
            #word_other
            #word
            Reply_messasge = 'Do not mention it.\nIt means ' + data.a[0][1][1]
            send_message(Reply_token,Reply_messasge)
            text_message = TextSendMessage(text='Do you want to go next?',
                               quick_reply=QuickReply(items=[
                                   QuickReplyButton(action=MessageAction(label="Of course!", text="Of course!")),
                                   QuickReplyButton(action=MessageAction(label="Take a break", text="See you next time!"))
                               ]))
            line_bot_api.push_message(userid, text_message)
            dictionary_add[userid]['words'][data.a[0][0]]["False"] += 1
            dictionary_add[userid]['meaning'][data.a[0][1][1]]["False"] += 1
            dictionary_add[userid]['wrong'] += 1
            update(dictionary_add)
            word.clear()
            #count_false+=1

        elif 'How to use' in message :
            line_bot_api.push_message(userid, ImageSendMessage(
                                        original_content_url='https://aceproject.pythonanywhere.com/stat/pic.png',
                                        preview_image_url='https://aceproject.pythonanywhere.com/stat/pic.png'
                                        ))

        elif 'Point' in message :
            total = dictionary_add[userid]['correct']
            Reply_messasge = 'You got ' + str(total) + ' point'
            send_message(Reply_token,Reply_messasge)
            sticker_message = StickerSendMessage(package_id='1',sticker_id='2')
            line_bot_api.push_message(userid, sticker_message)

        elif 'See you next time!' in message :
            total = dictionary_add[userid]['correct'] + dictionary_add[userid]['wrong']
            if total < 60:
                Reply_messasge = 'You have done ' + str(total) + ', \nIt is almost complete!!!'
            else:
                Reply_messasge = 'You have done ' + str(total) + ', \nYou have completed the learning phase!'
            send_message(Reply_token,Reply_messasge)

        return request.json, 200
    else:
        abort(400)

#Send message
def send_message(token, message):
    line_bot_api.reply_message(token,
        TextSendMessage(text=message))

if __name__ == '__main__':
    pass