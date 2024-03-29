from requests import get, head, post, packages, session
from bs4 import BeautifulSoup as soup
from urllib.parse import unquote
from m3u8 import parse as m3u8_parse
packages.urllib3.disable_warnings()


def get_size(size_in_bytes):
    size_in_bytes = int(size_in_bytes)
    size_in_mb = round(size_in_bytes / 1024 / 1024, 2)
    return f'{size_in_mb} MB'


def get_name_from_headers(header):
    return header.split(';')[1].replace('filename=', '').replace('"', '')


class FileHelper:
    def get_name_from_response(response):
        content_disposition = response.headers.get("content-disposition")
        if not content_disposition:
            return False

        if 'filename=' in content_disposition:
            name_start = content_disposition.index('filename=') + 9 # 9 is len('filename='), because index() returns the index of the first letter
            name_start+= 1 # to avoid the (") in the start
            temp = content_disposition[name_start:]
            name = temp.split('"')[0]

        else:
            name = unquote( response.url.split('/')[-1] )

        return name

    def size_to_mb(size_in_bytes):
        size_in_bytes = int(size_in_bytes)
        size_in_mb = round(size_in_bytes / 1024 / 1024, 2)
        return f'{size_in_mb} MB'

    def get_info_str(FileObj):
        info_str = ''

        if '.mp4' not in FileObj.name:
            FileObj.name += '.mp4'

        info_str += 'Name: ' + FileObj.name
        info_str += '\nURL: ' + FileObj.main_url
        info_str += '\nSize: ' + FileHelper.size_to_mb( FileObj.size )

        return info_str





class File:
    def __init__(self, response):
        self.response = response
        self.name = FileHelper.get_name_from_response(response)
        self.size = int(response.headers['content-length'])
        self.main_url = response.url
        self.info = FileHelper.get_info_str(self)


    def download_and_save(self):
        file = open(self.name, 'ab')
        downloaded = 0
        
        for chunk in self.response.iter_content(1024*1024*10):
            file.write(chunk)
            downloaded += len(chunk)
            perc = ( downloaded / self.size ) * 100
            perc = round(perc, 2)
            print(f'{perc}%')
            
        file.close()

class M3u8_file:
    def __init__(self, name, indexM3u8, main_url):
        self.name = name
        self.indexM3u8 = indexM3u8
        self.parts = M3u8_file.get_parts(indexM3u8)

        self.info = 'Name: ' + name
        self.info+= '\nURL: ' + main_url
        self.info+= '\nIndexUrl: ' + indexM3u8

    def get_parts(indexM3u8):
        res = get(indexM3u8, headers={}).text
        indexM3u8_dict = m3u8_parse(res)

        parts = [seg['uri'] for seg in indexM3u8_dict['segments']]
        return parts
        

    def download_and_save(self):
        file = open(self.name, 'ab')
        downloadedParts = 0
        totalParts = len(self.parts)

        for part in self.parts:
            part_content = get(part).content
            file.write(part_content)

            downloadedParts += 1
            perc = ( downloadedParts / totalParts ) * 100
            perc = round(perc, 2)
            print(f'{perc}%')

        file.close()
        
# ------------------------------------------------------

def stringToHex(string):
    return string.encode('utf-8').hex()

class Streamsb:
    def get_file_by_url(url):
        vid_id = url.split('/')[-1].replace('.html', '')

        data = f"AAA||{vid_id}||streamsb"
        hexData = stringToHex(data)
        
        url = 'https://sbthe.com/sources48/' + hexData
        headers = {'watchsb': 'sbstream'}
        
        res = get(url, headers=headers).json()
        
        m3u8_file_url = res['stream_data']['file']
        m3u8_file = get(m3u8_file_url).text
        m3u8_file_dict = m3u8_parse(m3u8_file)

        best_quality_index = m3u8_file_dict['playlists'][-1]['uri']


        m3u8_file_name = res['stream_data']['title']
        if not m3u8_file_name.endswith('.mp4'):
            m3u8_file_name+= '.mp4'
    

        
        
        return M3u8_file(m3u8_file_name, best_quality_index, url)

    
class GoogleDrive:
    def get_id(url):
        url = url.split('id=')[1]
        vid_id = url.split('&')[0]
        return vid_id

    def ok(vid_id):
        url = f'https://drive.google.com/uc?export=download&id={vid_id}&confirm=AYE'

        if post(url, stream=True).headers.get('content-disposition'):
            return True
        else:
            return False

    # old downloading function, doesn't work anymore, ig
    '''
    def get_file_by_id(vid_id):
        url = f'https://drive.google.com/uc?export=download&id={vid_id}&confirm=AYE'
        res = post(url, stream=True)

        return File(res)
    '''
    
    def get_file_by_id(vid_id):
        url = f'https://drive.google.com/uc?id={vid_id}&export=download'
        res = get(url, stream=True)
	
        if res.headers.get('content-disposition'):# file doesn't need confirmation
                return File(res)

        res_soup = soup(res.text, 'html.parser')
        downloadAnyWay_url = res_soup.find(id='download-form')['action']

        res = post(downloadAnyWay_url, stream=True)
        return File(res)
    

    def get_file_by_url(url):
        vid_id = GoogleDrive.get_id(url)
        return GoogleDrive.get_file_by_id(vid_id)

    
class Mp4upload:

    def get_id(url):
        vid_id = url.split('/')[-1]
        return vid_id

    def ok(vid_id):
        url = f'https://www.mp4upload.com/embed-{vid_id}.html'
        res = get(url).text

        if res == 'File was deleted':
            return False
        else:
            return True

    def get_file_by_id(vid_id):
        url = f'https://www.mp4upload.com/{vid_id}'
        file = {}

        headers = {'referer': 'https://mp4upload.com'}
        data = {
            'op': 'download2',
            'id': vid_id,
            'rand': '',
            'referer': 'https://www.mp4upload.com/',
            'method_free':  '',
            'method_premium': ''
        }

        res = post(url, data=data, headers=headers, stream=True, verify=False)

        return File(res)

    def get_file_by_url(url):
        vid_id = Mp4upload.get_id(url)
        return Mp4upload.get_file_by_id(vid_id)

class Userscloud:

    def get_id_from_url(url):
        return url.split('/')[-1]

    def get_file_by_url(url):

        data = {
            'op': 'download2',
            'id': Userscloud.get_id_from_url( url )
        }

        res = post(url, data=data, stream=True)

        return File(res)

class Tusfiles:
    def get_file_by_url(url):
        return Userscloud.get_file_by_url(url)

class Bayfiles:
    def get_file_by_url(url):
        res = get(url)
        res_soup = soup(res.text, 'html.parser')

        file_url = res_soup.find( id='download-url' )['href']
        res = get(file_url, stream=True)

        return File(res)

class Workupload:
    def get_id_from_url(url):
        return url.split('/')[-1]

    def get_file_by_url(url):
        i = session()
        i.get(url)

        vid_id = Workupload.get_id_from_url(url)
        api_url = f'https://workupload.com/api/file/getDownloadServer/{vid_id}'
        file_url = i.get(api_url).json()['data']['url']

        res = i.get(file_url, stream=True)

        return File(res)

class Mediafire:
    def get_file_by_url(url):
        res = get(url)
        res_soup = soup(res.text, 'html.parser')

        file_url = res_soup.find(id = 'downloadButton')['href']
        res = get(file_url, stream=True)

        return File(res)
