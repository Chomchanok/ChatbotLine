import os
from flask import Flask, request
from linebot.models import *
from linebot import *
import json
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

line_bot_api = LineBotApi('b5jEOAKs0FHY3MkC1fBn/ghTXv0uJBNYDF4ae7FVoGA0OkMhXa3fRSMVEqGiCjArgHXvcUh0KN5P2u+eOn+6dBVt4gwGYRsx6+kwxg2qhjO0GXG8x+9xvNRNt475r91YmgJQCU4aEB1bHrLf2LeMigdB04t89/1O/w1cDnyilFU=') ## Line Channel access token
handler = WebhookHandler('7d2e8f552de39ddd3f60099aa1e0f297') ## Line Channel secret

########################
# Json from dialogflow #
########################

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    # print(body)
    req = request.get_json(silent=True, force=True)
    print(req)

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
    #### province API ####
    ######################

    elif intent == 'province':
        str=text.split()
        amp=str[0]
        tambol=str[1]
        data = requests.get(
            'https://blockage.crflood.com/api/blockage/{}/{}'.format(amp,tambol))
        print(data)
        print(data.content)
        json_data = json.loads(data.text)
        num=len(json_data)
        blk_tumbol = json_data[0]['blockage_location']['blk_tumbol']
        message='สิ่งกีดขวางของตำบล{}\n'.format(blk_tumbol)
        for i in range(num):
            blk_code= json_data[i]['blk_code']
            blk_village = json_data[i]['blockage_location']['blk_village']
            river=json_data[i]['river']['river_name']+"/"+json_data[i]['river']['river_main']
            mess='{}. รหัสสิ่งกีดขวาง: {} \n ลำน้ำ: {} \nที่อยู่ : {} \n' .format(i+1,blk_code,river,blk_village)
            message=message+"\n"+mess
            # text_message = TextSendMessage(text='{}. รหัสสิ่งกีดขวาง: {} \n ที่อยู่ : {} ต.{}\n' .format(i+1,blk_code,blk_village,blk_tumbol))
            # message.append(text_message)
        print(message)
        text_message=TextSendMessage(text=message)
        line_bot_api.reply_message(reply_token, text_message)

    ######################
    #### Feq Flood API ###
    ######################

    elif intent == "feq_flood":
        str = text.split()
        feq = str[0]

        ## show logs 
        #print("Input word ::", str)

        data = requests.get('https://4871f4a67312.ngrok.io/damage_freq/{}'.format(feq))
        
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
            # print("Depart JSON logs =", widht_past +" " + depth_past + " " +slop_past)
            
            
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
            'https://4871f4a67312.ngrok.io/solution_project/{}'.format(id_blk))
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
    
    elif intent == "blockages_location":
        str=text.split()

        province = str[0]
        ampol = str[1]
        tumbol = str[2]

        data = requests.get(
            'https://4871f4a67312.ngrok.io/find_location_blk/{}/{}/{}'.format(province, ampol, tumbol))

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

    ########################
    # API Location long la #
    ########################

    elif intent == "share_location":
        str=text.split()
        longitude = str[0]
        latitude = str[1]

        data = requests.get('https://4871f4a67312.ngrok.io/find_distance/{}/{}'.format(longitude, latitude))
        print('Show data = ', data)
        json_data = json.loads(data.text)
        num=len(json_data)

        print("json data", json_data, '\n')
        message = "ลำดับที่ใกล้ที่สุดไปไกลที่สุด \n"

        for i in range(num):
            id_location = json_data[i]['id_location']
            longitude = json_data[i]['longitude']
            latitude = json_data[i]['latitude']
            location = json_data[i]['location']

            mess = "{}. รหัสสถานที่ {} \n ลองจิจูต {} \n ละจิจูต {} \n สถานที่ {} ".format(i + 1, id_location, longitude, latitude, location)
            message = message + mess + '\n \n'
        
        print(message)
        text_message=TextSendMessage(text=message)
        line_bot_api.reply_message(reply_token, text_message)

    ########################
    ## API Water IDF Value #
    ########################

    elif intent == "water_idf":
        str=text.split()
        idf_value = str[0]
        longitude = str[1]
        latitude = str[2]

        data = requests.get('https://4871f4a67312.ngrok.io/water_idf/{}/{}'.format(longitude, latitude))
        print('Show data = ', data)
        json_data = json.loads(data.text)
        num=len(json_data)

        print("json data", json_data, '\n')
        message = "ค่าน้ำฝนที่ใกล้พื้นที่ของคุณมากที่สุด \n"

        for i in range(num):
            id_idf = json_data[i]['id_idf']
            value_water = json_data[i]['value_water']

            mess = "ค่าน้ำฝน = {} ".format(value_water)
            message = message + mess + '\n \n'
        
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
