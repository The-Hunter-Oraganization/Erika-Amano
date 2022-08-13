import time, os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB

from Bot.plugins.database.mongo_db import check_user_mdb,check_vcodec_settings,update_vcodec_settings,check_preset_settings,update_preset_settings,check_resolution_settings,check_audio_type_mdb, update_audio_type_mdb,update_resolution_settings
from Bot.utils.decorators import ffmpeg_auto_settings, ffmpeg_settings
from Bot import encoder, OWNER_ID, LOG, FILES_CHANNEL
from Bot.utils.progress_pyro import progress_for_pyrogram
from Bot.utils.ffmpeg import ffmpeg_progress

encoder_is_on = []
flood = []

async def on_task_complete():
    del encoder_is_on[0]
    if len(encoder_is_on) > 0:
        if encoder_is_on[0]:
            await add_task(encoder_is_on[0])   
        
async def add_task(message):
    try:
        msg = await message.reply_text("<code>Downloading Files...</code>")
        c_time = time.time()
        FT = time.time()
        try:
            filepath = await message.download(progress=progress_for_pyrogram,progress_args=("**Downloading...**", msg, c_time))   
            check_resolution = check_resolution_settings(message.from_user.id)
            
            if check_resolution == 'auto':
                cmd = ffmpeg_auto_settings(message.from_user.id, filepath, FT)
                await msg.edit_text('**Encoding...**')
                try:
                    lq = await ffmpeg_progress(cmd[0], filepath,f'progress-{FT}.txt',FT, msg, '**Encoding Started 480p**\n\n')
                except Exception as e:
                    LOG.info(f'ERror while ffmpeg progress\n' +e) 
                try:
                    mq = await ffmpeg_progress(cmd[1], filepath,f'progress-{FT}.txt',FT, msg, '**Encoding Started 720p**\n\n')
                except Exception as e:
                    LOG.info(f'ERror while ffmpeg progress\n' +e)     
                try:
                    hq = await ffmpeg_progress(cmd[2], filepath,f'progress-{FT}.txt',FT, msg, '**Encoding Started 1080p**\n\n')
                except Exception as e:
                    LOG.info(f'Error while ffmpeg progress\n' +e)     
                output = input.rsplit('.',1)[0]
                try: #MSG EDIT AND EDIT
                    await msg.edit(f'**Encoding Completed')   
                    lq =  await msg.reply_document(output+'480p.mkv', caption='480p')  
                    mq =  await msg.reply_document(output+'720p.mkv', caption='720p')  
                    hq =  await msg.reply_document(output+'1080p.mkv',caption='1080p')  
                except Exception as e: 
                    LOG.info(f'Error while file sending\n'+e)  
                try:
                    await lq.copy(FILES_CHANNEL)
                    await mq.copy(FILES_CHANNEL)
                    await hq.copy(FILES_CHANNEL)
                except Exception as e: 
                    LOG.info(f'Error while file copy\n'+e)
            else:
                cmd = ffmpeg_settings(message.from_user.id, filepath, FT)  
                await msg.edit_text('**Encoding...**')
                try:
                    await ffmpeg_progress(cmd, filepath,f'progress-{FT}.txt',FT, msg, '**Encoding Started**\n\n')
                except Exception as e:
                    LOG.info(f'ERror while ffmpeg progress\n' +e) 
                
                output = input.rsplit('.',1)[0]
                output = output+'_IA.mkv'     
            
                try: #MSG EDIT AND EDIT
                    await msg.edit(f'**Encoding Completed')   
                    file =  await msg.reply_document(output)  
                except Exception as e: 
                    LOG.info(f'Error while file sending\n'+e)  
                try:
                    await file.copy(FILES_CHANNEL)
                except Exception as e: 
                    LOG.info(f'Error while file copy\n'+e)
            
            try: #FILE DELETE
                os.remove('downloads')
                os.remove(f'progress-{FT}.txt')
            except Exception as e: 
                    LOG.info(f'Error while removing files\n'+e)  
           
            try: #MSG DELETE
                await msg.delete() 
            except:
                pass       
                       
        except Exception as e: 
            LOG.info(f'Error while line 56\n'+e)    
    except Exception as e: 
        LOG.info(f'Error while Line 58\n'+e)
        
    try:
        await on_task_complete()   
    except Exception as e: 
        LOG.info(f'Error while task complete\n'+e) 
       


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
    encoder_is_on.append(message)
    if len(encoder_is_on) == 1:
        await add_task(message)           
                         
                   
        
        
        
                                
