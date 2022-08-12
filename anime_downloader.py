from anime_classes import Witanime
from downloader import get_file

classes_and_identifiers = {
	'witanime': Witanime
}

identifiers = list( classes_and_identifiers.keys() )

def get_site_class(url):
        for identifier in identifiers:
                
                if identifier in url:
                        site_class = classes_and_identifiers[identifier]
                        return site_class


class Episode:
	def __init__(self, num, url, site_class):
		self.num = num
		self.servers = site_class.get_ep_sources_by_ep_url(url)

	def display_all_servers_with_indexes(self):
		for i in range( len(self.servers) ):
			server = self.servers[i]
			print( f'{i}. {server["name"]}\n        URL: {server["url"]}' )



url = input("URL: ")
site_class = get_site_class(url)
anime_episodes = site_class.get_eps_by_anime_url(url)


print( f'{len(anime_episodes)} Episodes Found' )



f,t = input('From,To: ').split(',')
f,t = int(f)-1, int(t)
anime_episodes = anime_episodes[f:t]


# Getting The Server For The Choosen Episodes
print('\n\nGetting The Server For The Choosen Episodes', end='\n\n')


ready_episodes = []
for episode in anime_episodes:
	ready_episode = Episode(
			episode['num'],
			episode['url'],
			site_class
		)
	ready_episodes.append(ready_episode)
	print(episode['num'] + ' READY')



# Choosing The Wanted Servers
print('\n\nChoosing The Wanted Servers', end='\n\n')


download_list = []
for episode in ready_episodes:
        print(episode.num)
        episode.display_all_servers_with_indexes()
        server_index = int(input("Server Number: "))

        download_list.append( episode.servers[server_index]['url'] )

# Downloading Wanted Servers
print('\n\nDownloading Wanted Servers', end='\n\n')


for url in download_list:
        file = get_file(url)
        if not file:
        	print("ERROR IN DOWNLOADING "+url)
        	continue

        print('Downloading..')
        print(file.info)

        file.download_and_save()

        print('Downloaded')
        print('=============')







        
