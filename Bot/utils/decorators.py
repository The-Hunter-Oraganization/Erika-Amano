
from Bot.plugins.database.mongo_db import check_crf_mdb,check_user_mdb,check_vcodec_settings,update_vcodec_settings,check_preset_settings,update_preset_settings,check_resolution_settings,check_audio_type_mdb, update_audio_type_mdb,update_resolution_settings

def ffmpeg_settings(id, input, FT):
    resolutio = check_resolution_settings(id)
    audio_type = check_audio_type_mdb(id)
    preset = check_preset_settings(id)
    vcodec = check_vcodec_settings(id)
    crf = check_crf_mdb(id)
    if crf is None:
        crf = 28
    output = input.rsplit('.',1)[0]
    if '.mkv' in input:
        output = output+'_IA.mkv'    
    else:
        output = output+'_IA.mp4'    
    
    if vcodec == 'x264':
        vcodecs = 'libx264'
    elif vcodec == 'x265':
        vcodecs = 'libx265'     
    
    if resolutio == '480p':
        resolution = '640x480'
    elif resolutio == '720p':
        resolution = '1280x720'   
    else:
        resolution = '1920x1080'  
    
    if audio_type == 'opus':
        if resolutio == '480p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 64k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}""" -y'
        elif resolutio == '720p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 128k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}""" -y'
        else:
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 256k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}""" -y'
    
    elif audio_type == 'aac':
        if resolutio == '480p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        elif resolutio == '720p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        else:
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
    
    elif audio_type == 'libopus':
        if resolutio == '480p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        elif resolutio == '720p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        else:
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf {crf} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}""" -y'        
    return cmd      

# def ffmpeg_auto_settings(id, input, FT):
#     resolutio = check_resolution_settings(id)
#     audio_type = check_audio_type_mdb(id)
#     preset = check_preset_settings(id)
#     vcodec = check_vcodec_settings(id)
    
#     if '.mkv' in input:
#         output = output+'_IA.mkv'    
#     else:
#         output = output+'_IA.mp4'
    
#     if vcodec == 'x264':
#         vcodecs = 'libx264'
#     elif vcodec == 'x265':
#         vcodecs = 'libx265'        
    
#     if audio_type == 'opus':
#         if resolutio == 'auto':
#             if vcodecs == 'libx265':
#                 lq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 26 -s 640x480 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 480p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 64k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}480p.mkv""" -y'
#                 mq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 23 -s 1280x720 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 720p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 128k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}720p.mkv""" -y'
#                 hq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 24 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 1080p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 256k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}1080p.mkv""" -y'
#             elif vcodecs == 'libx264':
#                 lq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 28 -s 640x480 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 480p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 64k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}480p.mkv""" -y'
#                 mq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 27 -s 1280x720 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 720p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 128k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}720p.mkv""" -y'
#                 hq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 26 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 1080p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 256k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}1080p.mkv""" -y'
                
#     elif audio_type == 'aac':
#         if resolutio == 'auto':
#             if vcodecs == 'libx265':
#                 lq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 26 -s 640x480 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 480p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}480p.mkv""" -y'
#                 mq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 23 -s 1280x720 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 720p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}720p.mkv""" -y'
#                 hq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 24 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 1080p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}1080p.mkv""" -y'
#             elif vcodecs == 'libx264':
#                 lq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 28 -s 640x480 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 480p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}480p.mkv""" -y'
#                 mq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 27 -s 1280x720 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 720p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}720p.mkv""" -y'
#                 hq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 26 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 1080p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}1080p.mkv""" -y'

    
#     elif audio_type == 'libopus':
#         if resolutio == 'auto':
#             if vcodecs == 'libx265':
#                 lq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 26 -s 640x480 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 480p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}480p.mkv""" -y'
#                 mq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 23 -s 1280x720 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 720p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}720p.mkv""" -y'
#                 hq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx265 -crf 24 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 1080p - libx265"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}1080p.mkv""" -y'
#             elif vcodecs == 'libx264':
#                 lq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 28 -s 640x480 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 480p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}480p.mkv""" -y'
#                 mq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 27 -s 1280x720 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 720p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}720p.mkv""" -y'
#                 hq = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec libx264 -crf 26 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - 1080p - libx264"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}1080p.mkv""" -y'
#     return lq,mq,hq      