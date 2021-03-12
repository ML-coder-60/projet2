"""
  Projet 2
"""
# -*- coding: utf-8 -*-
from urllib.parse import urlparse
import csv
import re
import os
import requests
from bs4 import BeautifulSoup

def getinfobook(product_page_url):
    """ Récupere les informations d'un livre depuis l'url du livre
        la fonction renvoie les informations sous forme de dictionaire
        les 10 clefs qui compose ce dictionnaire:
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
       La fonction BeautifulSoup récupère les donnéés avec les tags suivants:
          - td  => ( il y a 7 td sur une page )
            - td N°1                           => universal_ product_code (upc)
            - td N°3 et N°4                    => price_including_tax et price_excluding_tax
            - td N°6                           => number_available
            - td N°7                           => review_rating
          - li et "class":"active"             => title
          - meta + "name":"description"        => product_description
          - a +regex de  "../category/books/"  => category
          - img + alt "Nom du livre"           => image_url
    """
    infobook = {}
    # On ajoute la ref url
    infobook['product_page_url'] = product_page_url
    response = requests.get(product_page_url)
    parsed_uri = urlparse(product_page_url)
    url_site = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
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
        writecsvcategory(infobook)

def writecsvcategory(data):
    """ Créé le reprtoire de destination si absent
        Ecrit les entêtes du csv puis puis écrit les données
        Le fichier csv sera stocké dans le répertoire
        repdata+/<category>/+<category>.csv
    """
    repbase = '/tmp/data/csv/'
    repdata = repbase+data['category']
    if not os.path.exists(repdata):
        os.makedirs(repdata)
    file_csv=repdata+'/'+data['category']+'.csv'
    fieldnames = ['product_page_url', 'universal_product_code (upc)', 'title',
                  'price_including_tax', 'price_excluding_tax', 'number_available',
                  'product_description', 'category', 'review_rating', 'image_url']
    with open(file_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                quoting=csv.QUOTE_MINIMAL
                                )
        writer.writeheader()
        writer.writerow(data)

if __name__ == '__main__':
    URL = 'http://books.toscrape.com/catalogue/sharp-objects_997/index.html'
    getinfobook(URL)
