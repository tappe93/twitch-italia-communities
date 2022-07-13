from DataCollection.twitch_api import *
import pandas as pd
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/Twitch_Analytics")
mydb = myclient["Twitch_Analytics"]
chat = mydb["chatters"]
viewers = mydb["viewers"]
errors = mydb["errors"]

df_dict = list(chat.find())

dict_def = {}
variables = [
    '_id',
    'month',
    'year',
    'date'
]

for timestamp in (df_dict):
    for streamer in timestamp:
        if streamer not in variables:
            if len(timestamp[streamer]) > 200:
                if streamer in dict_def.keys():
                    dict_def[streamer].extend((set(timestamp[streamer]) - set(dict_def[streamer])))
                else:
                    dict_def[streamer] = timestamp[streamer]

dict_community = {}
channel_completed = []

for channel_1 in (dict_def.keys()):
    dict_community[channel_1] = {}
    channel_completed.append(channel_1)
    for channel_2 in dict_def.keys():
        if channel_2 not in channel_completed:
            common = len(list(set(dict_def[channel_1]) & set(dict_def[channel_2])))
            if (common > 75) & ((common > len(dict_def[channel_1])/7.5)|(common > len(dict_def[channel_2])/7.5)):
                dict_community[channel_1][channel_2] = len(list(set(dict_def[channel_1]) & set(dict_def[channel_2])))

df_community_edge = pd.DataFrame()

for key,value in dict_community.items():
    for key_1,value_1 in dict_community[key].items():
        df_community_edge = df_community_edge.append({"Source":key, "Target":key_1, "Weight":value_1, "Type":"Undirected"},ignore_index = True)

df_community_label = pd.DataFrame()

for channel in dict_def.keys():
    df_community_label = df_community_label.append({"ID":channel, "Label":channel, "Count":len(dict_def[channel])},ignore_index=True)

df_community_edge.set_index('Source').to_csv('edge.csv')
df_community_label[(df_community_label.ID.isin(df_community_edge.Source)) | (df_community_label.ID.isin(df_community_edge.Target))].set_index('ID')[['Label','Count']].to_csv('label.csv')