"""
  Projet 2: Analyse de marché
"""
# -*- coding: utf-8 -*-
from urllib.parse import urlparse
import csv
import re
import os
import requests
from bs4 import BeautifulSoup

def info_book(product_page_url):
    """ Récupère les informations d'un livre depuis l'url du livre
        La fonction renvoie les informations sous forme de dictionnaire
        les 10 clefs qui composent ce dictionnaire :
            - product_page_url
            - universal_product_code
            - title
            - price_including_tax
            - price_excluding_tax
            - number_available
            - product_description
            - category
            - review_rating
            - image_url
        La fonction BeautifulSoup récupère les données avec les tags suivants:
            - td => ( il y a 7 td sur une page )
            - td N°1 => universal_ product_code (upc)
            - td N°3 et N°4 => price_including_tax et price_excluding_tax
            - td N°6 => number_available
            - td N°7 => review_rating
            - li et "class":"active" => title
            - meta + "name":"description" => product_description
            - a +regex de "../category/books/" => category
            - img + alt "Nom du livre" => image_url
    """
    infobook = {}
    infobook['product_page_url'] = product_page_url
    response = requests.get(product_page_url)
    url_site = geturlsite(product_page_url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        tds = soup.findAll('td')
        infobook['universal_product_code (upc)'] = tds[0].text
        title = soup.find('li', {"class": "active"}).text
        infobook['title'] = title
        infobook['price_including_tax'] = tds[2].text.replace('Â£', '')
        infobook['price_excluding_tax'] = tds[3].text.replace('Â£', '')
        infobook['number_available'] = tds[5].text.split('(')[1].split(' ')[0]
        infobook['product_description'] = soup.find(
            "meta", {"name": "description"})['content'].strip()
        infobook['category'] = soup.find(
            'a', {"href": re.compile("../category/books/")}).text
        infobook['review_rating'] = tds[6].text
        infobook['image_url'] = url_site + \
            soup.find('img', {"alt": title})['src'].replace('../', '')
    return infobook

def geturlsite(url):
    """ Renvoie l'adresse du site """
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

def writecsvcategory(datarray):
    """ La fonction créée le répertoire de destination si absent
        Ecrit les entêtes du csv puis les données
        Le fichier csv sera stocké dans le répertoire
        repdata+/<category>/+<category>.csv
    """
    repbase = '/tmp/data/csv/'
    repdata = repbase+datarray[0]['category']
    if not os.path.exists(repdata):
        os.makedirs(repdata)
    file_csv = repdata+'/'+datarray[0]['category']+'.csv'
    fieldnames = ['product_page_url', 'universal_product_code (upc)', 'title',
                  'price_including_tax', 'price_excluding_tax', 'number_available',
                  'product_description', 'category', 'review_rating', 'image_url']
    with open(file_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                quoting=csv.QUOTE_MINIMAL
                                )
        writer.writeheader()
        for data in datarray:
            writer.writerow(data)

def infobookbycategory(category_page_url):
    """ La fonction récupère les urls des livres d'une catégorie
        avec la fonction urlbookbycategory().
        Avec les "URLs Livre" la fonction info_book() obtient les informations demandées
        pour chaque livre puis on enregistre les données de la catégorie en
        format csv avec la fonction writecsvcategory """
    databook = []
    urlsbook = urlbookbycategory(category_page_url)
    for urlbook in urlsbook:
        databook.append(info_book(urlbook))
    writecsvcategory(databook)
    saveimagebook(databook)

def urlbookbycategory(category_page_url):
    """ Cette fonction renvoie les urls des livres pour une catégorie
        1) on récupère les pages liées à une catégorie avec la fonction pagebycategory()
        2) Pour chaque page on récupère les liens des articles présents
        3) On renvoie les liens de tous les livres liés à une catégorie sous forme de liste
    """
    urls = pagebycategory(category_page_url)
    urlsite = geturlsite(category_page_url)
    urlsbook = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for urlbook in soup.findAll('h3'):
            if urlbook.find('a'):
                urlbook = urlsite + \
                    urlbook.find('a')['href'].replace(
                        '../../../', 'catalogue/')
                urlsbook.append(urlbook)
    return urlsbook

def pagebycategory(category_page_url):
    """ Renvoie la liste des pages pour une catégorie
        1) La fonction request récupère le code html d'une page "catégorie"
        2) La fonction BeautifulSoup le nombre de pages liées à une catégorie les tags "li"
           et la class current  =>  soup.find('li',{'class':'current'}
        La page par défaut est index.html les pages suivantes si elles existent sont
        page-2.html page-3.html ....
        si aucune page détectée on renvoie la page par défaut
        sinon on renvoie la page par défaut +les pages  page-x.html
        pages = nbr de pages trouvées -1   (le -1 étant la page par défault)
        On commence avec un index à +2 pour les pages
    """
    response = requests.get(category_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pagin = soup.find('li', {'class': 'current'})
    listpagebycategory = []
    listpagebycategory.append(category_page_url)
    if pagin:
        pages = int(pagin.text.strip().split(' ')[3])-1
        category_url = category_page_url.replace('index.html', '')
        for i in range(pages):
            listpagebycategory.append(category_url+'page-'+str(i+2)+'.html')
        return listpagebycategory
    return listpagebycategory

def listcategory(url):
    """ Liste les catégories en utilisant les tags 'ul' et class=='nav nav-list'
        puis envoi les urls des catégories du site à la fonction infobookbycategory() pour
        un traitement sur les catégories.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    category_urls = soup.find('ul', {'class': 'nav nav-list'}).findAll('li')
    del category_urls[0]
    for category in category_urls:
        category_url = url+category.find('a')['href']
        infobookbycategory(category_url)

def saveimagebook(datarray):
    """ La fonction créée le répertoire de destination si absent
        Récupère et copie les images dans le réprtoire de destination
        repdata+/<category>/<image>
    """
    repbase = '/tmp/data/img/'
    repdata = repbase+datarray[0]['category']
    if not os.path.exists(repdata):
        os.makedirs(repdata)
    for data in datarray:
        if data['image_url'].find('/'):
            req = requests.get(data['image_url'], allow_redirects=True)
            open(repdata+'/'+data['image_url'].rsplit('/', 1)[1], 'wb').write(req.content)

if __name__ == '__main__':
    listcategory(url='http://books.toscrape.com/')
