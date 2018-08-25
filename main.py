import requests
from bs4 import BeautifulSoup
import os, json
import threading
import random

base_url = 'https://www.amazon.com'
ips = []
book_url = None
asins = []
books = []
isbns = []
user_agents = []

def makeRequest(url):
    agent = random.choice(user_agents[1])

    if len(ips)!=0:
        proxy = random.choice(ips)
        #print(proxy, agent)
        request = requests.get(url, headers={'User-agent' : agent}, proxies={'http' : proxy})
    else:
        request = requests.get(url, headers={'User-agent' : agent})

    content = request.text
    soup = BeautifulSoup(content, 'lxml')
    return soup

def getAsin(isbn):
    search_soup = makeRequest(base_url+'/gp/search/field-isbn='+isbn.strip())
    try:
        #print(search_soup.title)
        data_asin = search_soup.select_one("li[id=result_0]")['data-asin']
        print("Asin : " + data_asin)
        asins.append(data_asin)
    except:
        print(base_url+'/gp/search/field-isbn='+isbn.strip() + " Not found!")

def createHeadersList():
    useragent_files = os.listdir('useragents')
    useragents_path = os.path.abspath('useragents')
    h = []
    for x in useragent_files:
        with open(os.path.join(useragents_path,x), 'r') as f:
            user_agents.append(f.read().split('\n'))

    return user_agents

def getProxies():
    #https://www.us-proxy.org/
    soup = makeRequest('https://www.us-proxy.org/')
    t = soup.find('table',{'id':'proxylisttable'})
    rows = t.findAll('tr')[1:]

    for r in rows:
        cols = r.findAll('td')
        try:
            ip = cols[0].get_text()
        except Exception as e:
            pass

        ips.append(ip)

def doSomething():
    # Read the file to get urls
    with open('input.txt', 'r') as f:
        isbns = f.read().split("\n")

    for isbn in isbns:
        getAsin(isbn)

    for asin in asins:
        book_url = base_url + "/dp/" + asin

        print("Processing : " + book_url)
        soup = makeRequest(book_url)
        #print(soup.title.get_text())

        try:
            prod_title = soup.select_one('span[id=productTitle]').get_text()
        except Exception as e:
            hardcover_url = soup.find('span',{'text':'Hardcover'}).get_parent()['href']
            print("Title not found : trying ..." + hardcover_url)
            soup = makeRequest(hardcover_url)
            prod_title = soup.select_one('span[id=productTitle]').get_text()

        prod_details = soup.find_all('div', id='detail-bullets')
        prod_attributes = prod_details[0].find_all('ul')[0].find_all('li')

        print(asin, prod_title)
        d = {}
        d['Title'] = prod_title
        for attribute in prod_attributes:
            props = attribute.get_text().rstrip().replace('\n','').replace('\t','').replace('  ','')
            p = props.split(':')

            # skip amazon best seller rank
            if 'Amazon Best Sellers Rank' in props or 'Average Customer Review' in props:
                pass
            else:
                try:
                    d[p[0]] = p[1].strip()
                    #print(p[0], p[1])
                except:
                    pass
        books.append(d)


    # Write attributes to a file
    with open('output.json', 'w') as target:
        target.truncate()
        target.write(json.dumps(books))

createHeadersList()
getProxies()
doSomething()
