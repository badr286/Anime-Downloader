from downloading_classes import GoogleDrive, Mp4upload, Userscloud, Tusfiles, Bayfiles, Workupload, Mediafire, Streamsb

classes_and_identifiers = {
    'drive': GoogleDrive,
    'mp4upload': Mp4upload,
    'userscloud': Userscloud,
    'tusfiles': Tusfiles,
    'bayfiles': Bayfiles,
    'workupload': Workupload,
    'mediafire': Mediafire,
    'sbfull': Streamsb,
    'sbthe': Streamsb
}

identifiers = list( classes_and_identifiers.keys() )

def get_file(url):
    for identifier in identifiers:
        if identifier in url:
            the_class = classes_and_identifiers[identifier]
            return the_class.get_file_by_url(url)
        if 'gateanime' in url:
            return get_file(  get(url, headers={}).url  ) # Get The Actual URL and Run It Through get_file Again
        
    return False
    
        
