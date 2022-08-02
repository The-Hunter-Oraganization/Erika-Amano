
from Bot.plugins.database.mongo_db import check_user_mdb,check_vcodec_settings,update_vcodec_settings,check_preset_settings,update_preset_settings,check_resolution_settings,check_audio_type_mdb, update_audio_type_mdb,update_resolution_settings

def ffmpeg_settings(id, input, FT):
    resolutio = check_resolution_settings(id)
    audio_type = check_audio_type_mdb(id)
    preset = check_preset_settings(id)
    vcodec = check_vcodec_settings(id)
    output = input.replace('.mkv', '')
    output = output+'IA.mkv'
    
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
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 28 -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 64k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}""" -y'
        elif resolutio == '720p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 27 -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 128k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}""" -y'
        else:
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 25 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a opus -b:a 256k -map 0:a -c:s copy -map 0:s? -strict -2 """{output}""" -y'
    
    elif audio_type == 'aac':
        if resolutio == '480p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 28 -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        elif resolutio == '720p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 27 -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        else:
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 25 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a aac -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
    
    elif audio_type == 'libopus':
        if resolutio == '480p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 28 -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 64k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        elif resolutio == '720p':
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 27 -s {resolution} -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 128k -map 0:a -c:s copy -map 0:s? """{output}""" -y'
        else:
            cmd = f'ffmpeg -hide_banner -loglevel quiet -progress progress-{FT}.txt -i """{input}""" -preset {preset} -vcodec {vcodecs} -crf 25 -metadata title="Encoded By IndiAnime" -metadata:s:v title="IndiAnime - {resolutio} - {vcodec}"  -metadata:s:a title="IndiAnime" -map 0:v -c:a libopus -b:a 256k -map 0:a -c:s copy -map 0:s? """{output}""" -y'        
    return cmd      