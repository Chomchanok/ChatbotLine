import os
from flask import Flask, request
from linebot.models import *
from linebot import *
import json
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


######################################################################
line_bot_api = LineBotApi('') ## Line Channel access token
handler = WebhookHandler('') ## Line Channel secret
######################################################################


########################
# Json from dialogflow #
########################

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    # print(body)
    req = request.get_json(silent=True, force=True)
    intent = req["queryResult"]["intent"]["displayName"] # Intent NLP from dialogflow
    text = req['originalDetectIntentRequest']['payload']['data']['message']['text']
    reply_token = req['originalDetectIntentRequest']['payload']['data']['replyToken']
    id = req['originalDetectIntentRequest']['payload']['data']['source']['userId']
    disname = line_bot_api.get_profile(id).display_name

    # Show logs #
    print('id = ' + id)
    print('name = ' + disname)
    print('text = ' + text)
    print('intent = ' + intent)
    print('reply_token = ' + reply_token)

    reply(intent, text, reply_token, id, disname)

    return 'OK'


# def reply1(intent, text, reply_token, id, disname):


def reply(intent, text, reply_token, id, disname):

    if intent == 'intent 5':
        text_message = TextSendMessage(text='ทดสอบสำเร็จ')
        line_bot_api.reply_message(reply_token, text_message)



    ######################
    #### Feq Flood API ###
    ######################

    elif intent == "feq_flood":
        str = text.split()
        feq = str[0]

        ## show logs 
        #print("Input word ::", str)

        data = requests.get('https://d6e1a899623f.ngrok.io/damage_freq/{}'.format(feq))
        
        ## show logs 
        #print("Logs return all data :",data)

        json_data = json.loads(data.text)
        num = len(json_data)

        message = ""

        for i in range(num):
            blk_id = json_data[i]['blk_id']
            damage_frequency = json_data[i]['damage_frequency']
            blk_length = json_data[i]['blk_length']
            past_convert = json.loads(json_data[i]['past'])

            # show logs 
            print("JSON PAST logs :", past_convert)
 

            widht_past = past_convert['width']
            depth_past = past_convert['depth']
            slop_past = past_convert['slop']
            #print("Depart JSON logs =", widht_past +" " + depth_past + " " +slop_past)
            
            
            mess = '{}. รหัสสิ่งขีดขวาง: {} \n ความถี่น้ำท่วม: {} \n หน้ากว้างสิ่งขีดขวาง: {} \n ความกว้าง: {} \n ความลึก: {} \n สโลป: {}'.format(i + 1, blk_id, damage_frequency, blk_length, widht_past, depth_past, slop_past)

            message = message + mess + "\n \n"
        
        print(message)
        text_message=TextSendMessage(text=message)
        line_bot_api.reply_message(reply_token, text_message)


    
    ######################
    #### Blk_id API ######
    ######################
    
    elif intent == "blk_id":
        str=text.split()
        id_blk=str[0]
        data = requests.get(
            'https://d6e1a899623f.ngrok.io/solution_project/{}'.format(id_blk))
        print(data)
        print(data.content)
        json_data = json.loads(data.text)
        num=len(json_data)
 

        print("json data", json_data)

        # Debug
        print("json data 0", json_data[0]['blk_id'])
        print("json data 0", json_data[0]['prob_level'])
        message = ""

        for i in range(num):
            blk_code = json_data[i]['blk_id']
            prob_level = json_data[i]['prob_level']
            exp_solreport = json_data[i]['exp_solreport']
            mess = '{}. รหัสสิ่งขีดขวาง: {} \n ระดับความเสี่ยง: {} \n เเนวทางเเก้ไขเบื้องต้น: {}'.format(i+1, blk_code, prob_level, exp_solreport)
            message = message + mess + "\n"

        print(message)
        text_message=TextSendMessage(text=message)
        line_bot_api.reply_message(reply_token, text_message)

    ######################
    #### location_blk API 
    ######################
    
    elif intent == "location_blk":
        str=text.split()

        province = str[0]
        ampol = str[1]
        tumbol = str[2]

        data = requests.get(
            'https://d6e1a899623f.ngrok.io/find_location_blk/{}/{}/{}'.format(province, ampol, tumbol))

        print("Data show ::",data)
        print("Content Show ::",data.content)
        json_data = json.loads(data.text)
        num=len(json_data)
 
        # Check Json 
        print("json data", json_data, '\n')
        print("check json in json :", json_data[0]['damage_level'])
        debug_json_damagelevel = json.loads(json_data[0]['damage_level'])
        print("damage_level Flood :: ",debug_json_damagelevel['flood'])
        

        message = ""

        for i in range(num):

            blk_id = json_data[i]['blk_id']
            blk_location_id = json_data[i]['blk_location_id'] 

            json_damage_level = json.loads(json_data[i]['damage_level'])
            flood_level = json_damage_level['flood']
            # debug 
            print("Debug flood_level:: ",flood_level)

            damage_frequency = json_data[i]['damage_frequency']

            mess = '{}. รหัสสิ่งขีดขวาง: {} \n รหัสสถานที่: {} \n สถานะสิ่งขีดขวาง: {} \n ความถี่ความเสียหาย {}' .format(i+1, blk_id, blk_location_id, flood_level, damage_frequency)
            message = message + mess + "\n \n"

        print(message)
        text_message=TextSendMessage(text=message)
        line_bot_api.reply_message(reply_token, text_message)



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()
