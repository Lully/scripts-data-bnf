# coding: utf-8
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv as csv
import codecs

#Script Python qui rebondit sur les sujets associées aux publications d'un auteur.
#Permet de récupérer la liste des auteurs ayant publié sur le même sujet
#(avec limite : quand le sujet apparaît plus de X fois dans la base,
#on considère qu'il n'est pas pertinent : permet d'évacuer les sujet "Forme/Genre")
#L'objectif est d'importer le résultat du script dans Gephi pour générer un graphe d'auteurs associés à l'auteur en entrée.
#3 fichiers sont générés :
#  1. Liste des sujets (table de noeuds à importer dans Gephi)
#  2. Liste des auteurs (table de noeuds à importer dans Gephi)
#  3. Liste des associations Sujet-Auteur (table de liens à importer dans Gephi)
#Si on laisse les paramètres en entrée vides, le script les remplit avec des valeurs par défaut :
# a. Auteur analysé : René Girard
# b. Répertoire où déposer les fichiers en sortie : C:\Mes documents
# c. Date début de la période (ne prendre en compte que les publications inclues dans cette période) : date de naissance de l'auteur
# d. Date fin de la période : 9999
# e. Nombre max d'occurrences du sujet (si le nombre de manifs associées à un sujet excède ce nombre, ce sujet n'est pas exploité comme
# rebond pour trouver d'autres auteurs : 10000

person = input("URI de la personne dont il faut recuperer les dates des manifestations : ")
directory = input("Repertoire ou creer le fichier CSV en sortie : ")
datedebut = input("A partir de (Ne prendre en compte que les publications posterieures a cette date)")
datefin = input("Jusqu'a (Ne prendre en compte que les publications anterieures a cette date)")
limit = input("Nb max d'occurrences des mots-clés dans la base (si vide : 10000)")

urldata = "http://data.bnf.fr/sparql"


#Si l'identifiant "Person" n'a pas été renseigné en entrée (pour aller plus vite lors de tests)
# on affecte l'URI de René Girard
if (person == ""):
    person = "http://data.bnf.fr/ark:/12148/cb11905046c"
#Répertoire en écriture par défaut pour y déposer les fichiers
if (directory == ""):
    directory = "C:\Mes documents"
#La variable limit est convertie en nombre
if (limit == ""):
    limit = 10000
else:
    limit = int(limit)


#On vérifie que l'URI de la personne est bien son URI, et non l'URL de sa page dans data.bnf.fr
# Si l'URI contient "page", on fait une requête SPARQL pour convertir l'URL en URI de la personne

def page2ark(url):
    ark = url
    if (url.find("ark") > 0):
        if (url.find("foaf:Person") > 0):
            ark = url
        else:
            ark = url+"#foaf:Person"
    else:
        sparqlPage2ark = SPARQLWrapper(urldata)
        sparqlPage2ark.setQuery("""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        select ?person where {
          ?person foaf:page <""" + url + """>.
        }
        """)
        sparqlPage2ark.setReturnFormat(JSON)
        page2arkSet = sparqlPage2ark.query().convert()
        page2ark = page2arkSet["results"]["bindings"]
        if (page2ark[0].get("person")):
            ark = page2ark[0].get("person").get("value")
    return ark

personFOAF = "<" + page2ark(person) + ">"


personID = person.replace("http://data.bnf.fr/ark:/12148/","")

#Requête pour récupérer le nom de la personne, afin de nommer le fichier CSV en sortie
#On récupère au passage la date de naissance et de mort (si elles figurent dans data.bnf.fr)
# pour éventuellement générer des filtres par défaut lors de la requête
sparqlNom = SPARQLWrapperurldata

sparqlNom.setQuery("""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
select ?nom ?dateNaissance ?dateMort  where {
    """ + personFOAF + """ foaf:name ?nom.
       OPTIONAL {
       """ + personFOAF + """ <http://data.bnf.fr/ontology/bnf-onto/firstYear> ?dateNaissance.
       }
       OPTIONAL {
       """ + personFOAF + """ <http://data.bnf.fr/ontology/bnf-onto/lastYear> ?dateMort.
       }
}""")
sparqlNom.setReturnFormat(JSON)
NomSet = sparqlNom.query().convert()
nom = NomSet["results"]["bindings"]

nomListe = []
dateNaissanceListe = []
dateMortListe = []
dateNaissance = "0" 
dateMort = "0"


#Récupération
#1. du nom de la personne (utilisé pour nommer les fichiers en sortie)
#2. de la date de naissance (initialisée à 0, correctement renseignée ici)
#3. de la date de mort de la personne (initialisée à 0, correctement renseignée ici)
for el in nom:
    nomListe.append(el.get("nom").get("value"))
    nomStr = nomListe[0]
    if (el.get("dateNaissance")):
        dateNaissanceListe.append(el.get("dateNaissance").get("value"))
        dateNaissance = dateNaissanceListe[0]
    if (el.get("dateMort")):
        dateMortListe.append(el.get("dateMort").get("value"))
        dateMort = dateMortListe[0]



#Si dans le formulaire en entrée la date de début n'a pas été renseignée :
    #1. on prend la date de naissance
    #2. si la date de naissance n'est pas connue : on met "2000"
#Cette valeur sert ensuite à limiter la requête SPARQL à une fourchette de dates (début-fin)
#pour éviter de récupérer un trop grand nombre de noms
if (datedebut == ""):
    if (dateNaissance == "0"):
        datedebut = "2000"
    else:
        datedebut = dateNaissance
#Même chose que pour la date de mort : utilisé ensuite pour limiter la requête SPARQL
#(trouver autres auteurs ayant publié sur le même sujet)
#1. si l'utilisateur a mis une valeur en entrée, on la garde
#2. sinon, in récupère la date de mort de l'auteur
#3. si la date de mort de l'auteur est inconnue : on met "9999"
if (datefin == ""):
    if (dateMort == "0"):
        datefin = "9999"
    else:
        datefin = dateMort

#Correction sur la valeur du directory : ajout d'un antislash à la fin s'il n'y en a pas deja un
if (directory[len(directory)-1] == "\\" or directory[len(directory)-1] == "/"):
    directory = directory
else:
    if (directory.find("\\") == -1):
        directory = directory + "/"
    else:
        directory = directory + "\\"





#On récupère la liste des sujets traités par un auteur.
sparqlSujets = SPARQLWrapperurldata

sparqlSujets.setQuery("""DEFINE input:same-as "yes"
PREFIX dcterms: <http://purl.org/dc/terms/>
select distinct ?sujet where {
  ?manif dcterms:contributor """ + personFOAF + """.
  ?manif dcterms:subject ?sujet.
}""")
sparqlSujets.setReturnFormat(JSON)
SujetsSet = sparqlSujets.query().convert()
Sujets = SujetsSet ["results"]["bindings"]

ListeSujetsAuteur = []
ListeNbSujetsAuteur = []

for el in Sujets:
    ListeSujetsAuteur.append(el.get("sujet").get("value"))

sparqlNbSujets = SPARQLWrapperurldata

#Pour chaque sujet traité par cet auteur, on récupère le nombre de manifs indexées à ce sujet
for sujet in ListeSujetsAuteur:
    sparqlNbSujets.setQuery("""PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX frbr-rda: <http://rdvocab.info/uri/schema/FRBRentitiesRDA/>
    select (count(?manif) as ?nbIndexations) where {
      ?manif dcterms:subject <""" + sujet + """>.
      ?manif a frbr-rda:Manifestation.
    }""")
    sparqlNbSujets.setReturnFormat(JSON)
    NbSujetsSet = sparqlNbSujets.query().convert()
    NbSujets = NbSujetsSet ["results"]["bindings"]
    for el in NbSujets:
        ListeNbSujetsAuteur.append([sujet, el.get("nbIndexations").get("value")])

#1. Liste des auteurs
#2. Liste des sujets
#3. Liste des liens Auteur-Sujet
#4. Tableau complet pour visualiser sous Excel
AutresAuteursURI = []
AutresAuteursNom = []
AuteursD=[]
SujetsURI = []
SujetsLabels = []
SujetsD=[]
AuteursSujets = ["Source;Target"]

# Suppression dans ListeNbSujetsAuteur des mots-clés contenant un nombre d'occurrences supérieur à la variable limit
ListeNbSujetsAuteurFiltree = []
for el in ListeNbSujetsAuteur:
    if (int(el[1]) < limit):
        ListeNbSujetsAuteurFiltree.append(el[0])


#POUR CHAQUE SUJET de ListeNbSujetsAuteurFiltree :
#Requête SPARQL qui va récupérer :
        #1. la liste des sujets sur lesquels l'auteur a écrit
        #2. la liste des autres auteurs ayant publié sur le même sujet
#puis filtre sur une fourchette de publications :
        #Soit les dates mises en entrée par l'utilisateur
        #Soit les dates de naissance/mort de l'auteur
        #soit les dates 2000-9999 par défaut

for sujet in ListeNbSujetsAuteurFiltree:
    sparql = SPARQLWrapperurldata
    
    sparqlQuery = """PREFIX marcrel: <http://id.loc.gov/vocabulary/relators/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX bnf-onto: <http://data.bnf.fr/ontology/bnf-onto/>
    PREFIX bio: <http://vocab.org/bio/0.1/>
    PREFIX rdarelationships: <http://rdvocab.info/RDARelationshipsWEMI/>
    PREFIX frbr-rda: <http://rdvocab.info/uri/schema/FRBRentitiesRDA/>
    select ?autreAuteur ?nom ?labelSujet where {
      ?expr1  dcterms:subject <""" + sujet + """>.
      ?expr1 a frbr-rda:Expression.

      ?expr1 owl:sameAs ?expr2.
      ?expr2 dcterms:contributor """ + personFOAF + """.
      
      ?exprAutre1 dcterms:subject <""" + sujet + """>.
      <""" + sujet + """> skos:prefLabel ?labelSujet.

      ?exprAutre1 owl:sameAs ?exprAutre2.
      ?exprAutre2 dcterms:contributor ?autreAuteur.  
      
      ?manifAutre rdarelationships:expressionManifested ?exprAutre1.
      ?manifAutre  bnf-onto:firstYear ?datePublicationManif.
      
      ?autreAuteur foaf:name ?nom.
      ?autreAuteur a foaf:Person.
      
      MINUS {
        <""" + sujet + """> skos:scopeNote ?descriptionSujet.
        FILTER regex(?descriptionSujet, "en subdiv").
       }

      FILTER (
        ?datePublicationManif > """ + datedebut + """ 
        && 
        ?datePublicationManif < """ + datefin + """
      ).
      FILTER (langMatches(lang(?labelSujet), "fr")).
    }
    """

    sparql.setQuery(sparqlQuery)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    dataset = results["results"]["bindings"]

#    print (sparqlQuery)

#On va ensuite récupérer les résultats dans des tableaux


    index = []
    i=1

    for el in dataset:
        AutresAuteursURI.append(el.get("autreAuteur").get("value"))
        AutresAuteursNom.append(el.get("nom").get("value"))
        AuteursD.append(el.get("autreAuteur").get("value") + ";" + el.get("nom").get("value"))
        SujetsURI.append(sujet)
        SujetsLabels.append(el.get("labelSujet").get("value"))
        SujetsD.append(sujet + ";" + el.get("labelSujet").get("value"))
        AuteursSujets.append(el.get("autreAuteur").get("value") + ";" + sujet)
        index.append(i)
        i = i + 1

columns = ["Auteur","URI Auteur", "Sujet", "URI Sujet"]

Auteurs = ["ID;Label"]
for auteur in AuteursD:
    if not(auteur in Auteurs):
        Auteurs.append(auteur)
Sujets = ["ID;Label"]
for sujet in SujetsD:
    if not(sujet in Sujets):
        Sujets.append(sujet)


"""s1 = pd.Series(AutresAuteursURI, index=index, name='Auteur')
s2 = pd.Series(AutresAuteursNom, index=index, name='URI uteur')
s3 = pd.Series(SujetsURI, index=index, name='Sujet')
s4 = pd.Series(SujetsLabels, index=index, name='URI Sujet')"""

sA = pd.Series(Auteurs)
sB = pd.Series(Sujets)
sAB = pd.Series(AuteursSujets)

"""tableau = pd.concat([s1, s2, s3, s4], axis=1)"""
tableauAuteurs = pd.concat([sA], axis=1)
tableauSujets = pd.concat([sB], axis=1)
tableauAuteursSujets = pd.concat([sAB], axis=1)

#print(tableau)




#Ecriture des fichiers CSV en sortie
#filename : le tableau complet URI Auteur + nom Auteur + URI Sujet + Label Sujet
#filename  = directory + "resultats-" + nomStr + ".csv"
"""with open(filename, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(s3)"""
#tableau.to_csv(path_or_buf=filename,sep=";", header="True",mode="w",encoding="utf-8")

#filenameA : nom et URI des auteurs (pour import comme table de noeuds dans Gephi)
filenameA  = directory + "1-resultats-" + nomStr + "-Auteurs (table de noeuds).csv"
outfileA = codecs.open(filenameA, "w", "utf-8")
outfileA.writelines( list( "%s\n" % auteur for auteur in Auteurs ) )
outfileA.close()

#filenameB : nom et URI des sujets (pour import comme table de noeuds dans Gephi)
filenameB  = directory + "2-resultats-" + nomStr + "-Sujets (table de noeuds).csv"
outfileB = codecs.open(filenameB, "w", "utf-8")
outfileB.writelines( list( "%s\n" % sujet for sujet in Sujets) )
outfileB.close()

#filenameAB : URI des auteurs -> URI des sujets (pour import comme table de liens dans Gephi)
filenameAB  = directory + "3-resultats-" + nomStr + "-Auteur-Sujets (table de liens).csv"
outfileAB = codecs.open(filenameAB, "w", "utf-8")
outfileAB.writelines( list( "%s\n" % auteursujet for auteursujet in AuteursSujets) )
outfileAB.close()
