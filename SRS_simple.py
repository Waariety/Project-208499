#Import module
from flask import Flask, request, abort
import requests
import random
import json
import csv
from collections import defaultdict

from linebot import LineBotApi
from linebot.models import *

#Token
ACCESS_TOKEN = 'LJGPQjnwwpFjt4CYp+vpnLblxljPZYSGkzvVTrc4QbgXuTrkXpLYL19Dt9ZhCSFWxFwDllSFHQFEgGv8z0MBE2IH255fFu0ks6ycNaXCDQ+xEwwlmNqY2Xlpbn0JirF0f1E4DnTs4KB+TxCBwMypDwdB04t89/1O/w1cDnyilFU='

word = []
word_other = []
count = 0

#Collect data
class DataStore():
    count_false = 0
    count_true = 0
    a = None
    b = None

data = DataStore()

f = open('/home/AceProject/data/sample.json')
read_data = json.load(f)

#Import data
v = []
f_full = open('/home/AceProject/data/100-vocab.csv')
csv_reader = csv.reader(f_full)
for line in csv_reader:
  #print(line)
  v.append(line[0])
  v.append(line[1])
  v.append(line[2])

res_dct = {v[i]:v[i + 2] for i in range(0, len(v), 3)}

user_history = defaultdict(dict)

#Data personal
for uid in read_data.keys():
    collect_word = []
    data_personal_key = []
    data_personal_value = []
    collect_word_key = []
    collect_word_value = []
    new_data = {}

    for key, value in read_data[uid].items():
        data_personal_key = read_data[uid]["words"]
        data_personal_value = read_data[uid]["meaning"]

    for key, value in data_personal_key.items():
        #print(key, ',')
        collect_word_key.append(key)

    for key, value in data_personal_value.items():
        #print(key, ',')
        collect_word_value.append(key)

    for key in collect_word_key:
        for value in collect_word_value:
            new_data[key] = value
            collect_word_value.remove(value)
            break
    user_history[uid] = list(new_data.items())

#Create array
def array_and_dict():
    return { 'words' : defaultdict(lambda: defaultdict(int)), 'correct' : 0, 'wrong' : 0}

#Update
def update(dictionary_add):
    filename = '/home/AceProject/data/test.json'
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
            if not bool(user_history[userid]):
                Reply_messasge = 'You have answered all questions!!!'
                send_message(Reply_token,Reply_messasge)
                return request.json, 200

            data.a = [user_history[userid][0]]
            user_history[userid].remove(data.a[0])
            data.b = [random.choice([n for n in res_dct.items() if n != data.a[0]])]

            word.clear()
            word.append(data.a)

            word_other.clear()
            word_other.append(data.b[0][1])
            word_other.append(word[0][0][1])
            word_other.sort()

            buttons_template = ButtonsTemplate(
            title=None, text='Do you know the meaning of\n"'+ word[0][0][0] + '"?', actions=[
                MessageAction(label= word_other[0], text= word_other[0], weight = "bold" , color = "#aaaaaa"),
                MessageAction(label= word_other[1] , text= word_other[1], weight = "bold" , color = "#aaaaaa")
            ])
            template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
            line_bot_api.reply_message(Reply_token, template_message)

        elif data.a[0][1][1] in message :
            Reply_messasge = 'That is great!\nIt means ' + data.a[0][1]
            send_message(Reply_token,Reply_messasge)
            text_message = TextSendMessage(text='Do you want to go next?',
                               quick_reply=QuickReply(items=[
                                   QuickReplyButton(action=MessageAction(label="Of course!", text="Of course!")),
                                   QuickReplyButton(action=MessageAction(label="Take a break", text="See you next time!"))
                               ]))
            line_bot_api.push_message(userid, text_message)
            dictionary_add[userid]['words'][data.a[0][0]]["True"] += 1
            dictionary_add[userid]['correct'] += 1
            update(dictionary_add)
            word.clear()

        elif data.b[0][1]in message :
            Reply_messasge = 'Do not mention it.\nIt means ' + data.a[0][1]
            send_message(Reply_token,Reply_messasge)
            text_message = TextSendMessage(text='Do you want to go next?',
                               quick_reply=QuickReply(items=[
                                   QuickReplyButton(action=MessageAction(label="Of course!", text="Of course!")),
                                   QuickReplyButton(action=MessageAction(label="Take a break", text="See you next time!"))#,
                                   #QuickReplyButton(action=MessageAction(label="How many have you done?", text="It is almost complete!"))
                               ]))
            line_bot_api.push_message(userid, text_message)
            dictionary_add[userid]['words'][data.a[0][0]]["False"] += 1
            dictionary_add[userid]['wrong'] += 1
            update(dictionary_add)
            word.clear()

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
                Reply_messasge = 'You have done ' + str(data.count_true + data.count_false) + ', \nIt is almost complete!!!'
            else:
                Reply_messasge = 'You have done ' + str(data.count_true + data.count_false) + ', \nThank you for your participation!!!'
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
