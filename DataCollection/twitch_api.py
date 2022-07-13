import os,sys
sys.path.append(os.getcwd())
import requests
from config import api_key as headers
import json
import pandas as pd
from datetime import datetime

url_chat = "http://tmi.twitch.tv/group/user/"
base_url = 'https://api.twitch.tv/helix/'
indent = 2

def get_response(query):
    """
    Get response from Twitch API.

    Parameter
    ---------
    query: str
    """
    url = base_url + query
    response = requests.get(url = url, headers = headers)
    return response

def print_response(response):
    """
    Used for debugging purposes.

    Parameter
    ---------
    response
    """
    response_json = response.json()
    print_response = json.dumps(response_json, indent=indent)
    print(print_response)

def top_streams(language = None,number = 100):
    """
    Get the first n stream with most concurrent viewers in a language.

    Parameters
    ----------
    language: str, default 'it'
        Language chosen.
    number: int, default = 100
        Number of streams.
    """
    calls = number//100 + 1
    last_call_number = number%100

    if language is None:
        query = 'streams?first='+str(number)
    else:
        query =  'streams?language='+language+'&first='+str(number)
    df = pd.DataFrame()

    if calls == 1:
        resp_0 = get_response(query=query)
        df = df.append(pd.json_normalize(resp_0.json()['data']))
    else:
        resp_0 = get_response(query="streams?language="+language+"&first=100")
        df = df.append(pd.json_normalize(resp_0.json()['data']))
        for call in range(1,calls):
            if call != calls - 1:
                resp_1 = get_response(query="streams?language="+language+"&first=100&after="+resp_0.json()['pagination']['cursor'])
                resp_0 = resp_1
            else:
                if last_call_number != 0:
                    resp_1 = get_response(query="streams?language="+language+"&first="+str(last_call_number)+"&after="+resp_0.json()['pagination']['cursor'])
            df = df.append(pd.json_normalize(resp_1.json()['data']))
    df = df.head(number)
    df['timestamp'] = datetime.now().strftime("%Y/%m/%d %H:%M")
    return df 

def get_chatters(user_name):
    return requests.get(url_chat + user_name.lower() + "/chatters").json()
