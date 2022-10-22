from requests import get
from bs4 import BeautifulSoup as soup


def merge_lists(From,To):
    for i in From:
        To.append(i)
    return True

AVAILABLE_SERVERS = [
    'drive',
    'mp4upload',
    'userscloud',
    'tusfiles',
    'bayfiles',
    'workupload',
    'mediafire',
    'sbfull',
    'sbthe'
]
def getAvailableServers(servers: list):
    availabeServers = []
    for server in servers:
        for keyword in AVAILABLE_SERVERS:
            if keyword in server['url']:
                availabeServers.append(server)

    return availabeServers


class Witanime:

    def get_servers_from_multi_servers(multi_servers_url):
        url = multi_servers_url.replace('embed', 'd')
        res = get(url)
        soup_res = soup(res.text, 'html.parser')

        servers_LIs = soup_res.findAll('li')
        servers = []

        for server_LI in servers_LIs:
            name = server_LI.find('small').text
            url = server_LI.find('a')['href']
            if url[0:4] != 'http':
                url = 'https:' + url

            servers.append({'name': name, 'url': url})

        return servers

    def get_servers_from_yonaplay(yonaplayer_url):
        res = get(yonaplayer_url, headers = {'referer':'https://witanime.com'})
        soup_res = soup( res.text, 'html.parser' )

        container_div = soup_res.find('div', {'class': 'ODDIV'})
        servers_LIs = container_div.findAll('li')

        servers = []
        for server_LI in servers_LIs:
            name = server_LI.find('span').text + ' ' + server_LI.find('p').text
            url = server_LI['onclick'].replace('go_to_player', '').replace('(', '').replace(')', '').replace("'", '')
            
            servers.append({'name': name, 'url': url})

        return servers
    

    def get_ep_sources_by_ep_url_NOTUSED(ep_url):#From Video Player
        res = get(ep_url)
        soup_res = soup(res.text, 'html.parser')

        servers_a_tags = soup_res.find(id='episode-servers').findAll('a')
        servers = []
        
        # FINDING THE MULTI SERVERS
        for server in servers_a_tags:
            if 'multi server' in server.text:
                url = server['data-ep-url']
                multiservers = Witanime.get_servers_from_multi_servers(url)
                merge_lists(multiservers, servers)
                servers_a_tags.remove(server)
                
            elif 'yonaplay' in server.text:
                url = server['data-ep-url']
                yonaservers = Witanime.get_servers_from_yonaplay(url)
                merge_lists(yonaservers, servers)
                servers_a_tags.remove(server)


        for server in servers_a_tags:
            server_name = server.text
            server_url = server['data-ep-url']

            servers.append({'name': server_name, 'url': server_url})

        return servers


    def get_ep_sources_by_ep_url(ep_url):#From Downloading Servers
        res = get(ep_url)
        soup_res = soup(res.text, 'html.parser')
        
        episode_download_container = soup_res.find('div', {'class':'episode-download-container'})
        quality_lists = episode_download_container.findAll('ul', {'class':'quality-list'})

        servers = []
        for group in quality_lists:
            LIs = group.findAll('li')
            quality_name = LIs[0].text
            group_servers = LIs[1:]
            for server in group_servers:
                server_name = server.text + ' - ' + quality_name
                server_url = server.find('a')['href']
                if 'multi server' in server.text:
                    url = server_url
                    multiservers = Witanime.get_servers_from_multi_servers(url)
                    merge_lists(multiservers, servers)
                    continue

                servers.append( {'name':server_name, 'url':server_url} )

        return servers
            

    def get_eps_by_anime_url(anime_url):
        res = get(anime_url).text
        soup_res = soup(res, 'html.parser')

        episodes_divs = soup_res.findAll('div',
                {'class': 'episodes-card-title'})

        episodes = []
        for episode in episodes_divs:
            url = episode.find('a')['href']
            num = episode.find('h3').text

            episodes.append({'num': num, 'url': url})

        return episodes
    
   

class Gateanime:

    def get_ep_sources_by_ep_url(ep_url):
        res = get(ep_url)
        res_soup = soup(res.text, 'html.parser')

        servers_tr_tags = res_soup.find('tbody').findAll('tr')

        servers = []
        for server_tr_tag in servers_tr_tags:
            server_span_tags = server_tr_tag.findAll('span')

            server_name = server_span_tags[1].text
            quality = server_span_tags[3].text
            server_url = server_tr_tag.find('a')['href']

            servers.append( {'name':server_name + ' - ' + quality, 'url': server_url } )

        return servers

            
            
        

    def get_eps_by_anime_url(anime_url):
        
        parts = anime_url.split(' ')
        
        if parts == 2:
            anime_url, season_number = anime_url.split(' ')
        else:
            anime_url, season_number = parts[0], '1' # Default Season Value Is 1
            
            
        
        res = get(anime_url)
        res_soup = soup(res.text, 'html.parser')

        seasons = res_soup.findAll('div', {'class':'AABox'})
        wanted_season = seasons[ int(season_number) - 1 ]

        eps_tr_tags = wanted_season.findAll('tr')

        episodes = []
        for tr_tag in eps_tr_tags:
            ep_td_tags = tr_tag.findAll('td')

            num = ep_td_tags[0].text
            url = tr_tag.find('a')['href']
            
            episodes.append({'num': num, 'url':url})

        return episodes
