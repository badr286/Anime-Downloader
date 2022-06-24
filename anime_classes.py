from requests import get
from bs4 import BeautifulSoup as soup

class Witanime:

    def get_servers_from_multi_servers(multi_servers_url):
        url = multi_servers_url.replace('embed', 'd')
        res = get(url)
        soup_res = soup(res.text, 'html.parser')

        servers_LIs = [li for li in soup_res.findAll('li')]
        servers = []

        for server_LI in servers_LIs:
            name = server_LI.find('small').text
            url = server_LI.find('a')['href']
            if url[0:4] != 'http':
                url = 'https:' + url

            servers.append({'name': name, 'url': url})

        return servers

    def get_ep_sources_by_ep_url(ep_url):
        res = get(ep_url)
        soup_res = soup(res.text, 'html.parser')

        servers_a_tags = soup_res.find(id='episode-servers').findAll('a')

        # IN CASE MULTISERVERS DOESN'T EXIST
        servers = []
        
        # FINDING THE MULTI SERVER
        for server in servers_a_tags:
            if 'multi server' in server.text:
                url = server['data-ep-url']
                servers = Witanime.get_servers_from_multi_servers(url)
                servers_a_tags.remove(server)


        for server in servers_a_tags:
            server_name = server.text
            server_url = server['data-ep-url']

            servers.append({'name': server_name, 'url': server_url})

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
