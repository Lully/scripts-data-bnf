# coding: utf-8
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import numpy as np
import matplotlib
import csv as csv


person = input("URI de la personne dont il faut recuperer les dates des manifestations : ")
directory = input("Repertoire ou creer le fichier CSV en sortie : ")

#Correction sur la valeur du directory : ajout d'un antislash à la fin s'il n'y en a pas deja un
if (directory[len(directory)-1] == "\\" or directory[len(directory)-1] == "/"):
    directory = directory
else:
    if (directory.find("\\") == -1):
        directory = directory + "/"
    else:
        directory = directory + "\\"

personFOAF = "<" + person + "#foaf:Person>"
personID = person.replace("http://data.bnf.fr/ark:/12148/","")

sparql = SPARQLWrapper("http://data.bnf.fr/sparql")

sparql.setQuery("""
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdarelationships: <http://rdvocab.info/RDARelationshipsWEMI/>
PREFIX bnf-onto: <http://data.bnf.fr/ontology/bnf-onto/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
select ?date (count(?date) as ?NbManifParDate) where {
  ?manif rdarelationships:expressionManifested ?expression.
  ?manif bnf-onto:firstYear ?date.
  ?expression owl:sameAs ?expression2.
  ?expression2 dcterms:contributor """ + personFOAF + """.
}
ORDER BY ASC(?date)
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
dataset = results["results"]["bindings"]

listeDesAnnees = []
listedesNbManif = []

for el in dataset:
    listeDesAnnees.append(el.get("date").get("value"))
    listedesNbManif.append(el.get("NbManifParDate").get("value"))

columns = ["Date","Nb manif"]
min = listeDesAnnees[0]
max = listeDesAnnees[-1]

#print (min, "-", max, "/", columns)

listeAnnees = [int(min)]
listeNbManif = [int(listedesNbManif[0])]

index=[1]
i = 1

while int(min) < int(max):
    nouvMin = int(min) + 1
    listeAnnees.append(nouvMin)
    if (str(nouvMin) in listeDesAnnees):
        pos = listeDesAnnees.index(str(nouvMin))
        listeNbManif.append(int(listedesNbManif[pos]))
    else:
        listeNbManif.append(0)
    min = nouvMin
    i = i+1
    index.append(i)
    


s1 = pd.Series(listeAnnees, index=index, name='dates')
s2 = pd.Series(listeNbManif, index=index, name='manifs')
s3 = pd.Series(listeNbManif, index=listeAnnees, name='manifs')

tableau = pd.concat([s1, s2], axis=1)

print(tableau)
s3=s3.cumsum()
s3.plot()

#Requête pour récupérer le nom de la personne, afin de nommer le fichier CSV en sortie
sparqlNom = SPARQLWrapper("http://data.bnf.fr/sparql")

sparqlNom.setQuery("""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
select ?nom  where {""" + personFOAF + """foaf:name ?nom
}""")
sparqlNom.setReturnFormat(JSON)
NomSet = sparqlNom.query().convert()
nom = NomSet["results"]["bindings"]

nomListe = []
for el in nom:
    nomListe.append(el.get("nom").get("value"))

nomStr = nomListe[0]

#Ecriture du fichier CSV en sortie
filename  = directory + "resultats-" + nomStr + ".csv"
"""with open(filename, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(s3)"""
tableau.to_csv()
tableau.to_csv(path_or_buf=filename,sep=";", header="True",mode="w",encoding="utf-8")
