from Bot import encoder as app, LOG

async def get_users(id):
    try:
        get_users = await app.get_users(id)
        if get_users.username:
            USERNAME = get_users.username
        else:
            USERNAME = "None"
        if get_users.id:
            ID = get_users.id    
        if get_users.first_name:
            F_NAME = get_users.first_name
        else:
            F_NAME = "None"
        if get_users.last_name:
            L_NAME = get_users.last_name
        else:
              L_NAME = "None"
        if get_users.dc_id:
            DC_ID = get_users.dc_id
        else:
            DC_ID = "None"
        if get_users.status:
            STATUS = get_users.status
        else:
            STATUS = "None" 
        if get_users.photo.big_file_id:
            PBFI =  get_users.photo.big_file_id
        else:
            PBFI = "AQADBQADqrIxG_iZqFQAEAMAA2SnX3gABMVq60tkSk5LAAQeBA"      
    except:
        LOG.info("Error No User Found")
        return  
    return USERNAME, F_NAME, L_NAME, DC_ID, STATUS,PBFI, ID   

async def user_check_template(USERNAME, F_NAME, L_NAME, DC_ID, STATUS, ID=None):
    TEXTS = f"**ᴜsᴇʀ's ғɪʀsᴛ ɴᴀᴍᴇ**: `{F_NAME}`\n" 
    TEXTS += f"**ᴜsᴇʀ's ʟᴀsᴛ ɴᴀᴍᴇ**: `{L_NAME}`\n" 
    TEXTS += f"**ᴜsᴇʀ's ᴜsᴇʀɴᴀᴍᴇ**: @{USERNAME}\n" 
    TEXTS += f"**ᴜsᴇʀs's ɪᴅ:**: `{ID}`\n" 
    TEXTS += f"**ᴜsᴇʀ's ᴅᴀᴛᴀᴄᴇɴᴛᴇʀ**: `{DC_ID}`\n" 
    TEXTS += f"**ᴜsᴇʀ's ʟᴀsᴛ sᴛᴀᴛᴜs**: `{STATUS}`\n"  
    return TEXTS  