from DataCollection.twitch_api import *
import pandas as pd
import requests
import datetime
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/Twitch_Analytics")
mydb = myclient["Twitch_Analytics"]
chat = mydb["chatters"]
viewers = mydb["viewers"]
errors = mydb["errors"]

try:
    date_now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    streams = get_response(query="streams?language=it&first=100").json()['data']
    df = pd.json_normalize(streams)
    df["date"] = date_now
    df["month"] = datetime.datetime.now().month
    df["year"] = datetime.datetime.now().year
    

    chatters = {}
    for channel in (df.user_name.tolist()):
        url_chat = "http://tmi.twitch.tv/group/user/"+channel.lower()+"/chatters"
        chat_dict = requests.request("GET", url_chat).json()
        try:
            chatters[channel] = chat_dict['chatters']['viewers']
        except TypeError:
            print(channel)
            pass
    
    chatters["date"] = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    chatters["month"] = datetime.datetime.now().month
    chatters["year"] = datetime.datetime.now().year

    x = chat.insert_many([chatters])

    x = viewers.insert_many(df.to_dict(orient="records"))

except:
    x = errors.insert_many([{"Error at": datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}])
    