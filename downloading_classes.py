from requests import get, head, post, packages, session
from bs4 import BeautifulSoup as soup
from urllib.parse import unquote
packages.urllib3.disable_warnings()


def get_size(size_in_bytes):
    size_in_bytes = int(size_in_bytes)
    size_in_mb = round(size_in_bytes / 1024 / 1024, 2)
    return f'{size_in_mb} MB'


def get_name_from_headers(header):
    return header.split(';')[1].replace('filename=', '').replace('"', '')


class File:
    def __init__(self, file):
        self.name = file['name']
        self.size = file['size']
        self.main_url = file['main_url']
        self.get_content_func = file['get_content_func']
        self.info = self.info()

    def info(self):
        info_str = ''

        if '.mp4' not in self.name:
            self.name += '.mp4'

        info_str += 'Name: ' + self.name
        info_str += '\nURL: ' + self.main_url
        info_str += '\nSize: ' + self.size

        return info_str

    def download_and_save(self):
        content = self.get_content_func()
        open(self.name, 'wb').write(content)


# ------------------------------------------------------


class GoogleDrive:
    def get_id(url):
        url = url.replace('https://drive.google.com/file/d/', '')
        url = url.replace('/view', '')
        vid_id = url.replace('/preview', '')
        return vid_id

    def ok(vid_id):
        url = f'https://drive.google.com/uc?export=download&id={vid_id}&confirm=AYE'

        if post(url, stream=True).headers.get('content-disposition'):
            return True
        else:
            return False


    def get_file_by_id(vid_id):
        url = f'https://drive.google.com/uc?export=download&id={vid_id}&confirm=AYE'
        res = post(url, stream=True)

        file = {

            'get_content_func': lambda: post(url).content,
            'size': get_size(res.headers['content-length']),
            'name': get_name_from_headers(res.headers['content-disposition']),
            'main_url': url

        }

        return File(file)

    def get_file_by_url(url):
        vid_id = GoogleDrive.get_id(url)
        print(vid_id)
        return GoogleDrive.get_file_by_id(vid_id)


class Mp4upload:

    def get_id(url):
        url = url.replace('https://', '')
        url = url.replace('www.', '')
        url = url.replace('mp4upload.com/', '')
        url = url.replace('embed-', '')
        url = url.replace('.html', '')

        vid_id = url

        return vid_id

    def ok(vid_id):
        url = f'https://www.mp4upload.com/embed-{vid_id}.html'
        res = get(url).text

        if res == 'File was deleted':
            return False
        else:
            return True

    def get_name_from_url(url):
        return url.split('/')[-1].replace('%20', ' ')

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

        res = post(url, data=data, headers=headers, stream=True,
                   allow_redirects=False, verify=False)
        src = res.headers['location']
        src_headers = head(src, headers=headers, verify=False).headers

        file['get_content_func'] = lambda: get(
            src, headers=headers, verify=False).content
        file['name'] = Mp4upload.get_name_from_url(src)
        file['size'] = get_size(src_headers['content-length'])
        file['main_url'] = url

        return File(file)

    def get_file_by_url(url):
        vid_id = Mp4upload.get_id(url)
        return Mp4upload.get_file_by_id(vid_id)
    

class Userscloud:
    def get_file_by_url(url):
        vid_id = url.split('/')[-1]
        
        data = {
	'op': 'download2',
	'id': vid_id,
        }

        res = post(url, data=data, stream=True)

        file = {}
        file['get_content_func'] = lambda: post(url, data=data)
        file['name'] = unquote(res.url).split('/')[-1]
        file['size'] = get_size(res.headers['content-length'])
        file['main_url'] = url

        return File(file)



class Tusfiles:
    def get_file_by_url(url):
        return Userscloud.get_file_by_url(url)


class Bayfiles:
    def get_file_by_url(url):
        res = get(url)
        res_soup = soup(res.text, 'html.parser')

        file_url = res_soup.find( id='download-url' )['href']
        return Animeiat.get_file_by_url(file_url)




class Animeiat:
    def get_file_by_url(url):
        file = {}
        res = head(url)

        file['get_content_func'] = lambda: get(url).content
        file['size'] = get_size(res.headers['content-length'])
        file['name'] = unquote(url.split('/')[-1])
        file['main_url'] = url

        return File(file)


class Skyanime_player:
    def get_file_by_url(url, file_name):
        vid_id = url.split('?id=')[-1]


        # Get ApiKey
        res = get(url).text.split('"')

        for i in range(len(res)):
            if 'apikey' in res[i]:
                apikey = res[i+1]

                break

        # Get File Url
        url = "https://www.googleapis.com/drive/v3/files/"+vid_id+"?alt=media&key="+apikey

        # Prepare File
        # return Animeiat.get_file_by_url(url) works ig
        file = {}
        res = head(url)

        file['get_content_func'] = lambda: get(url).content
        file['size'] = get_size(res.headers['content-length'])
        file['name'] = file_name
        file['main_url'] = url

        return File(file)

    



class Egybest:
    def get_file_by_url(url):
        res = head(url)
        file = {}

        file['get_content_func'] = lambda: get(url).content
        file['name'] = get_name_from_headers(res.headers['content-disposition'])
        file['size'] = get_size(res.headers['content-length'])
        file['main_url'] = url

        return File(file)
