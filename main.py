import urllib.request
from bs4 import BeautifulSoup
import os, json, re

base_url = 'https://www.amazon.com'
headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
book_url = None
asins = []
books = []

# Read the file to get urls
with open('input.txt', 'r') as f:
    isbns = f.readlines()
    for isbn in isbns:
        isbn_search = urllib.request.Request(base_url+'/gp/search/field-isbn='+isbn, headers=headers)
        isbn_search_page = urllib.request.urlopen(isbn_search)
        search_content = isbn_search_page.read()
        search_soup = BeautifulSoup(search_content, 'lxml')
        try:
            data_asin = search_soup.select_one("li[id=result_0]")['data-asin']
            asins.append(data_asin)
        except:
            print(str(isbn) + " Not found!")
            #pass

print(asins)
for asin in asins:
    book_url = base_url + "/dp/" + asin

    print("Processing : " + book_url)
    request = urllib.request.Request(book_url, headers=headers)
    page = urllib.request.urlopen(request)
    content = page.read()
    soup = BeautifulSoup(content, 'lxml')

    prod_details = soup.find_all('div', id='detail-bullets')
    prod_attributes = prod_details[0].find_all('ul')[0].find_all('li')
    prod_title = soup.find_all('span',id='productTitle')[0].get_text()
    print(prod_title)
    
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
    target.writelines(json.dumps(books) + '\n')
