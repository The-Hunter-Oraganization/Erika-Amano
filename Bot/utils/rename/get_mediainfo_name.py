from pymediainfo import MediaInfo
            
def get_filename(query):
    mediainfo = MediaInfo.parse(query)
    for trackobj in mediainfo.tracks:
        track = trackobj.to_data()
    if track["track_type"] == "General": 
        try:
            title = (track['title'])
        except:
            title = None  
    return title          
                