from bs4 import BeautifulSoup
import requests
import os
import csv


liste_urls_livres = []
liste_urls_categories = []
fin_url_a_remplacer = "index.html"
nom_fichier_csv = ""
liste_titre = ["product_page_url",
               "universal_ product_code (upc)",
               "title",
               "price_including_tax",
               "price_excluding_tax",
               "number_available",
               "product_description",
               "category",
               "review_rating",
               "image_url"
               ]

if not os.path.exists("books_to_scrape_csv"):
    os.mkdir("books_to_scrape_csv")


def copie_urls_livre(url_a_parcourir):
    
    global fin_url_a_remplacer
    req = requests.get(url_a_parcourir)
    soup = BeautifulSoup(req.content, features="html.parser")
    url_boucle = soup.find_all("h3")
    url_raccourci = url_a_parcourir.replace(fin_url_a_remplacer, "")

    for i in url_boucle:
        lien = i.find("a")
        lien = lien["href"]
        lien = lien.replace("../../..", "http://books.toscrape.com/catalogue")
        liste_urls_livres.append((lien))

    if soup.find("li", class_="next"):
        bouton_next = soup.find("li", class_="next")
        url_next_page = bouton_next.find("a")
        url_next_page = url_next_page["href"]
        fin_url_a_remplacer = url_next_page
        url_next_page = url_raccourci + url_next_page
        copie_urls_livre(url_next_page)


def scrap_page_livre(url_page_livre):
   
    req = requests.get(url_page_livre)

    if req.ok:
        soup = BeautifulSoup(req.content, features="html.parser")

        titre = soup.title.text
        titre = soup.find("ul", class_="breadcrumb")
        titre = soup.find("li", class_="active").text

        tableau = soup.find("table", class_="table table-striped")
        tableau = tableau.find_all("td")

        upc = tableau[0].text

        prix_ht = tableau[2].text
        prix_ht = prix_ht.replace("£", "")
        prix_ht = float(prix_ht)

        prix_ttc = tableau[3].text
        prix_ttc = prix_ttc.replace("£", "")
        prix_ttc = float(prix_ttc)

        stock = tableau[5].text
        stock = stock.replace("In stock (", "").replace(" available)", "")
        stock = int(stock)

        nb_etoiles = soup.find("p", class_="star-rating")["class"]
        nb_etoiles = nb_etoiles[1]
        if nb_etoiles == "One":
            nb_etoiles = 1
        elif nb_etoiles == "Two":
            nb_etoiles = 2
        elif nb_etoiles == "Three":
            nb_etoiles = 3
        elif nb_etoiles == "Four":
            nb_etoiles = 4
        elif nb_etoiles == "Five":
            nb_etoiles = 5

        description = soup.find_all("p")
        description = description[3].text

        img_url = soup.find("img").get("src")
        img_url = img_url.replace("../..", "http://books.toscrape.com")

        categorie = soup.find("ul", class_="breadcrumb").find_all("li")
        categorie = categorie[2].text.strip()

        liste_donnees = [url_page_livre,
                         upc,
                         titre,
                         prix_ht,
                         prix_ttc,
                         stock,
                         description,
                         categorie,
                         nb_etoiles,
                         img_url
                         ]

        return (liste_donnees)


def copie_urls_cat():
   
    global liste_urls_categories
    url_de_base = "http://books.toscrape.com/"
    req = requests.get(url_de_base)
    soup = BeautifulSoup(req.text, features="html.parser")
    cats = soup.find("ul", class_="nav").find_all("a")

    for i in cats:
        i = i["href"]
        i = url_de_base + i
        i = i.replace("'", '"')
        liste_urls_categories.append(i)
    del (liste_urls_categories[0])  


copie_urls_cat()


for i in liste_urls_categories: 
    print(i)
    req = requests.get(i)

    if req.ok:
        soup = BeautifulSoup(req.content, features="html.parser")
        nom_fichier_csv = soup.find("h1").text.lower().replace(" ", "_")
        nom_fichier_csv = nom_fichier_csv + ".csv"

        copie_urls_livre(i) 

    with open("books_to_scrape_csv/" + nom_fichier_csv, "w", encoding="utf-8-sig", newline="") as cat_csv:
        csv_file_writer = csv.writer(cat_csv)
        csv_file_writer.writerow(liste_titre) 

        for url in liste_urls_livres:
            csv_file_writer.writerow(scrap_page_livre(url)) 

    liste_urls_livres = []
    fin_url_a_remplacer = "index.html"