from compileall import compile_dir
import time, os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB

from Bot.plugins.database.mongo_db import check_user_mdb,check_vcodec_settings,update_vcodec_settings,check_preset_settings,update_preset_settings,check_resolution_settings,check_audio_type_mdb, update_audio_type_mdb,update_resolution_settings
from Bot.utils.decorators import ffmpeg_settings
from Bot import encoder, OWNER_ID, LOG, FILES_CHANNEL
from Bot.utils.progress_pyro import progress_for_pyrogram
from Bot.utils.ffmpeg import ffmpeg_progress

data = []
flood = []
async def on_task_complete(id):
    ok = data_check(id)
    data.remove(ok)
    await add_task(ok)
    flood.remove(id)   
    return None       
        
def data_check(id):
    for i in data:
        if id == i.from_user.id: 
            return i
        
async def add_task(message):
    try:
        msg = await message.reply_text("<code>Downloading Files...</code>")
        c_time = time.time()
        FT = time.time()
        try:
            #FILE NAME
            '''if message.document.file_name in message:
                file_name = message.document.file_name
            elif message.video_file_name in message:
                file_name = message.video_file_name'''
            filepath = await message.download(progress=progress_for_pyrogram,progress_args=("**Downloading...**", msg, c_time))   
            cmd = ffmpeg_settings(message.from_user.id, filepath, FT)  
            await msg.edit_text('**Encoding...**')
            try:
                await ffmpeg_progress(cmd, filepath,f'progress-{FT}.txt',FT, msg, '**Encoding Started**\n\n')
            except Exception as e:
                LOG.info(f'ERror while ffmpeg progress\n' +e) 
            output = filepath.replace('.mkv', '')
            output = output+'IA.mkv'      
            try:
                await msg.edit(f'**Encoding Completed')   
                file =  await msg.reply_document(output)  
            except Exception as e: 
                LOG.info(f'Error while file sending\n'+e)  
            try:
                await file.copy(FILES_CHANNEL)
            except Exception as e: 
                LOG.info(f'Error while file copy\n'+e)  
        except Exception as e: 
            LOG.info(f'Error while line 56\n'+e)    
    except Exception as e: 
        LOG.info(f'Error while Line 58\n'+e)
    try:
        await on_task_complete(message.from_user.id)  
        await msg.delete()  
    except Exception as e: 
        LOG.info(f'Error while task complete\n'+e)  
    
    try:
        os.remove(filepath)
        os.remove(output)
        os.remove(f'progress-{FT}.txt')
    except Exception as e:
        LOG.info(f'Error while removing files\n'+e)    


video_mimetype = [
    "video/x-flv",
    "video/mp4",
    "application/x-mpegURL",
    'application/zip',
    "video/MP2T",
    "video/3gpp",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-ms-wmv",
    "video/x-matroska",
    "video/webm",
    "video/x-m4v",
    "video/quicktime",
    "video/mpeg"
]      
                  
@encoder.on_message(filters.document | filters.video & filters.private)
async def encoder_process(encoder, message):
    if message.document and message.video and message.document.mime_type and message.video.mime_type not in video_mimetype:
        return 
    check = check_user_mdb(message.from_user.id)
    if check is None:
        text= "You're not authorized to use this bot. Request Admins to approve you."
        await encoder.send_message(message.chat.id, text, reply_markup=IKM([[IKB('ʀᴇǫᴜᴇsᴛ', f'users_request-{message.from_user.id}')]]))
        return
    id = message.from_user.id
    flood.append(id)
    if flood.count(id) <=1:
        await add_task(message)
        flood.remove(id)
    else:
        data.append(message) 
        await message.reply('**Added To Queue**')             
                         
                   
        
        
        
                                
