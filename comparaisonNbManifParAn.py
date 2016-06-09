# coding: utf-8

#Script pour décompter le nombre de manifs par décennies, pour plusieurs auteurs comparativement
#2 paramètres en entrée :
# 1. Liste des ARK (ou URL des pages). Si rien, le script met les ARK de 4 poètes du XIXe siècle
# 2. Périodes à prendre en compte (permet de lisser les courbes). Si rien : 1 année

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv as csv
import codecs
from lxml import etree
from collections import Counter

urldata = "http://data.bnf.fr/sparql"

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



#Param en entrée
listeARK1 = input("Liste des ARK des auteurs (séparés par une virgule)")
arrondi = input("Années regroupées par périodes de ... ans")
if (listeARK1 == ""):
    listeARK1 = "http://data.bnf.fr/ark:/12148/cb118905823,http://data.bnf.fr/ark:/12148/cb119219976,http://data.bnf.fr/ark:/12148/cb119279849,http://data.bnf.fr/ark:/12148/cb11914131k"

if (arrondi == ""):
    arrondi = 1
else:
    arrondi = int(arrondi)

ListeARK1 = listeARK1.split(",")
ListeARKs = []

for ark in ListeARK1:
    ListeARKs.append(page2ark(ark))

ListeARKnoms = []
#Récupérer le nom de famille des auteurs
for ARK in ListeARKs:
    sparqlName = SPARQLWrapper(urldata)
    sparqlName.setQuery("""
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    select ?name where{
      <""" + ARK + """> foaf:familyName ?name.
    }
    """)
    sparqlName.setReturnFormat(JSON)
    NameSet = sparqlName.query().convert()
    Names = NameSet["results"]["bindings"]
    if (Names[0].get("name")):
        Nom = Names[0].get("name").get("value").replace("é","e")
    else:
        Nom = ARK.replace("http://data.bnf.fr/ark:/12148/","")
    ListeARKnoms.append([ARK,Nom])

queryManifsEntete = []
queryManifsUNION = []

for auteur in ListeARKnoms:
    queryManifsEntete.append("(count(?manif" + auteur[1] + ") as ?" + auteur[1] + ")")
queryManifsEntete = " ".join(queryManifsEntete)

for auteur in ListeARKnoms:
    queryManifsUNION.append("""{?expr""" + auteur[1] + """ marcrel:aut <""" + auteur[0] + """>.
  ?manif""" + auteur[1] + """ rdarelationships:expressionManifested ?expr""" + auteur[1] + """; bnf-onto:firstYear ?datepub.
}""")

queryManifsUNION = "\nUNION ".join(queryManifsUNION)

queryManifs = """
DEFINE input:same-as "yes"

PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdarelationships: <http://rdvocab.info/RDARelationshipsWEMI/>
PREFIX bnf-onto: <http://data.bnf.fr/ontology/bnf-onto/>
PREFIX marcrel: <http://id.loc.gov/vocabulary/relators/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

select ?date """ + queryManifsEntete + """ where {
""" + queryManifsUNION + """
BIND ((round(?datepub/""" + str(arrondi) + """)*""" + str(arrondi) + """) as ?date).
}

GROUP BY ?date
ORDER BY ?date
"""

sparqlDecompteManifs = SPARQLWrapper(urldata)
sparqlDecompteManifs.setQuery(queryManifs)
sparqlDecompteManifs.setReturnFormat(JSON)
DecompteManifsSet = sparqlDecompteManifs.query().convert()
DecompteManifs = DecompteManifsSet["results"]["bindings"]

ListeResultatsManifs = []

#Constitution d'une liste de résultats par auteur
ListeNomsAuteurs= []
ListeAnnees = []
DicNomsAuteurs = {}

for auteur in ListeARKnoms:
    ListeNomsAuteurs.append(auteur[1])


for nom in ListeNomsAuteurs:
    listenom = []
    for el in DecompteManifs:
        listenom.append(el.get(nom).get("value"))
    ListeResultatsManifs.append(listenom)

i = 0
for nom in ListeNomsAuteurs:
	DicNomsAuteurs[nom] = ListeResultatsManifs[i]
	i = i+1

print(DicNomsAuteurs)

for el in DecompteManifs:
    ListeAnnees.append(el.get("date").get("value"))

tableau = pd.DataFrame(DicNomsAuteurs,index=ListeAnnees)



"""for auteur in ListeNomsAuteurs:
    serie = pd.DataFrame({auteur:ListeResultatsManifs[i],"annee":ListeAnnees[i]})
    #print(serie)
    tableau = tableau.merge(serie,left_on="annee")
    i = i + 1"""

#tableau.set_index(ListeAnnees)
#print(ListeNomsAuteurs)
print(tableau)



#print(ListeResultatsManifs)

#print(DecompteManifs)
plt.plot(tableau)
plt.xlabel("Annees")
LegendeY = "Nb d'éditions par an"
if (arrondi != 1):
    LegendeY = 'Nb editions par periodes de ' + str(arrondi) + ' ans'
plt.ylabel(LegendeY)
plt.legend(ListeNomsAuteurs, fontsize=9)

plt.show()

#print(queryManifs)
