"""
  Projet 2: Analyse de marché Programe Principal
"""
import utils.projet2 as scrape

URL_SITE='http://books.toscrape.com/'

def main(url):
    """ 1) On utilise la méthode list_category()
           qui retourn les urls des catégories dans une liste
        2) On utilise la méthode url_book_by_category()
           pour récupérer les urls de tous les livres de la catégorie
        3) Pour chaque livre on utilise la methode info_book()
           pour récupérer les informations utile pour analyse de marché
        4) On sauvegarde les données d'une catégorie
           avec la méthode write_csv_category()
        5) On récupère les images des livres avec la méthode save_image_book()
    """
    category_urls=scrape.list_category(url)
    if category_urls:
        for category_url in category_urls:
            databook=[]
            page_category=scrape.page_by_category(category_url)
            urlsbook = scrape.url_book_by_category(page_category)
            for urlbook in urlsbook:
                databook.append(scrape.info_book(urlbook))
            scrape.write_csv_category(databook)
            scrape.save_image_book(databook)

main(URL_SITE)
