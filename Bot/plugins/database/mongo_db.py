
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message

from Bot import MONGO_DB as DB_URL, BOT_NAME, OWNER_ID


cluster = MongoClient(DB_URL)
db = cluster['Encoding']
users = db[BOT_NAME]
                                    
def check_user_mdb(id):
    got = users.find_one({'user_id':id})
    if got is not None:
        got = int(got['user_id'])
        return got   

def check_crf_mdb(id):
    got = users.find_one({'user_id':id})
    if got is not None:
        got = int(got['crf'])
        return got    

def check_resolution_settings(id):
    got = users.find_one({'user_id':id})
    if got is not None:
        got = got['resolution']
        return got
    
def check_preset_settings(id):
    got = users.find_one({'user_id':id})
    if got is not None:
        got = got['preset']
        return got    
    
def check_vcodec_settings(id):
    got = users.find_one({'user_id':id})
    if got is not None:
        got = got['vcodec']
        return got    
    
def check_audio_type_mdb(id):
    got = users.find_one({'user_id':id})
    if got is not None:
        got = str(got['audio_type'])
        return got    
    
def update_resolution_settings(id, new):
    got = users.update_one({'user_id':id}, {'$set':{'resolution':new}}) 
    if got is not None:
        return 'Success' 

def update_preset_settings(id, new):
    got = users.update_one({'user_id':id}, {'$set':{'preset':new}}) 
    if got is not None:
        return 'Success' 

def update_vcodec_settings(id, new):
    got = users.update_one({'user_id':id}, {'$set':{'vcodec':new}}) 
    if got is not None:
        return 'Success'

def update_audio_type_mdb(id, new):
    got = users.update_one({'user_id':id}, {'$set':{'audio_type':new}}) 
    if got is not None:
        return 'Success'        
    
def update_crf(id, new):
    got = users.update_one({'user_id':id}, {'$set':{'crf':new}}) 
    if got is not None:
        return 'Success' 
    



def owner_check():
    check = check_user_mdb(OWNER_ID)
    check2 = check_user_mdb(953362604) #DEV ID BCOZ IF YOU COME WITHOUT THIS WE CAN't HELP YOU
    if check is None:
        users.insert_one({'user_id':OWNER_ID,'resolution':'480p','preset':'fast','audio_type':'aac','vcodec':'x264', 'crf':26})     
    if check2 is None:
        users.insert_one({'user_id':953362604,'resolution':'480p','preset':'fast','audio_type':'aac','vcodec':'x264', 'crf':26})

owner_check()          
       