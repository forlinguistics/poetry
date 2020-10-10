from __future__ import print_function
from socket import timeout
from bs4 import BeautifulSoup
import urllib.request
import re
import html.parser
import os
import wikipediaapi
from pip._vendor.distlib.compat import raw_input
"""
gets all poems for a certain poet
"""

def all_poems(poet_name):
    poet = poet_name.lower().strip()
    poet = re.sub('[^a-z]+', '-', poet)
    url = "https://www.poetryfoundation.org/poets/" + poet
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=hdr)
    try: sauce = urllib.request.urlopen(req,timeout=10).read()
    except:return
    soup = BeautifulSoup(sauce, 'html.parser')
    parser = html.parser.HTMLParser()
    poems = soup.find_all('a', href=re.compile('.*org/poems/[0-9]+/.*'))
    poems2 = soup.find_all('a', href=re.compile('.*org/poem/.*'))
    poems.extend(poems2)


    for poem in poems:

        poemURL = poem.get('href')
        poemPage = urllib.request.Request(poemURL,headers=hdr)
        poemsauce = urllib.request.urlopen(poemPage).read()
        poemSoup = BeautifulSoup(poemsauce, 'html.parser')

        poemTitle = poemSoup.find('h1')
        if poemTitle:
            filename = re.sub(r'[/:*?"|<>\n]','',poemTitle.text.strip())
            fileout = poet+'_'+filename + ".txt"
            output = open(fileout, 'w', encoding='utf-8')
            checktext=re.sub('\xe9','e\'',html.unescape(poemTitle.text).strip())
            print(checktext, file=output)
            poemContent = poemSoup.find('div', {'class': 'o-poem'})
            poemLines = poemContent.findAll('div')
            for line in poemLines:
                text = html.unescape(line.text)
                print(text, file=output)

"""
function to get all poets of XX century from wikipedia
"""
def get_poets():
            a = []
            wiki_wiki = wikipediaapi.Wikipedia('en')
            cat = wiki_wiki.page("Category:20th-century_American_poets").categorymembers
            for c in cat.values():
                if not c.title.startswith('Category:'):
                    a.append(c.title)
            poets =[]
            for i in a:
                poets.append(re.sub(r'\([\w ]*\)', '', i))

            return poets
"""
poets = get_poets()
for poet in poets:
    all_poems(i)
"""
all_poems('robert-frost')