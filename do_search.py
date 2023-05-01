from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

url = 'https://www.google.com/search'

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
}


def do_search(search: str):
    parameters = {'q': search}

    content = requests.get(url, headers=headers, params=parameters).content
    soup = BeautifulSoup(content, 'html.parser')

    search = soup.find(id='search')
    first_link = search.find('a')
    html = urlopen(first_link['href'])
    wikipedia_soup = BeautifulSoup(html, 'html.parser')
    # content = wikipedia_soup.find(id="mw-content-text")
    text = ""
    cnt = 0
    for paragraph in wikipedia_soup.find_all('p'):
        text += paragraph.text
        cnt += 1
        if cnt == 2:
            break
    text = text.split('\n')[1]
    return text
