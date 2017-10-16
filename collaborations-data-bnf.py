# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 13:56:34 2017

@author: Lully
Ce programme prend en entrée un identifiant d'auteur BnF, récupère la liste des auteurs liés 
et de là les relations entre ces auteurs (et leur poids)
En sortie, un tableau à deux colonnes qu'on peut injecter dans Gephi comme table de liens, 
afin d'obtenir un graphe de collaborations
Sachant qu'il s'y trouve nécessairement des relations posthumes : quand un interprète
enregistre des morceaux d'un compositeur des siècles passés
"""


from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
from unidecode import unidecode

entree = input("Identifiant ARK de l'auteur dont il faut chercher les collaborations : ")
if (entree == ""):
    entree = "ark:/12148/cb13896861p"

dicCollaborations = defaultdict(int)
dicArk2Nom = defaultdict(str)

listeCollaborations_file = open("collaborations-" + entree[11:22] + ".csv","w")
listeCollaborations = []

def auteur2collabSPARQL(ark):
    req = """DEFINE input:same-as "yes"
        PREFIX rdarelationships: <http://rdvocab.info/RDARelationshipsWEMI/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX bnf-onto: <http://data.bnf.fr/ontology/bnf-onto/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        select distinct ?nomAuteur ?prenomAuteur ?ressource ?collaborateur ?nomCollaborateur ?prenomCollaborateur where {
        ?ressource ?URIrole1 <http://data.bnf.fr/""" + ark + """#about>.
        <http://data.bnf.fr/""" + ark + """#about> foaf:familyName ?nomAuteur.
        OPTIONAL {<http://data.bnf.fr/""" + ark + """#about> foaf:givenName ?prenomAuteur.}
        ?ressource ?URIrole2 ?collaborateur.
        ?collaborateur foaf:familyName ?nomCollaborateur.
        OPTIONAL {?collaborateur foaf:givenName ?prenomCollaborateur.}
        ?URIrole1 skos:inScheme <http://data.bnf.fr/vocabulary/roles>.
        ?URIrole2 skos:inScheme <http://data.bnf.fr/vocabulary/roles>.}"""
    sparql = SPARQLWrapper("http://data.bnf.fr/sparql")
    sparql.setQuery(req)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert() 
    return results

def collaboration(nomAuteur1,nomAuteur2):
    nomAuteur1 = nomAuteur1.replace('"',"'").replace(';',",")
    nomAuteur2  = nomAuteur2.replace('"',"'").replace(';',",")
    collab = [nomAuteur1,nomAuteur2]
    collab = "\"" + collab[0] + "\";\"" + collab[1] + "\""
    listeCollaborations.append(collab)
    listeCollaborations_file.write(collab + "\n")

def auteur2collab(ark):
    req_sparql = auteur2collabSPARQL(ark)
    for result in req_sparql["results"]["bindings"]:
        #éviter les cas où l'auteur est collaborateur de lui-même (c'est-à-dire intervient à plusieurs titres sur un même document)
        if (result["nomAuteur"]["value"] != result["nomCollaborateur"]["value"]):
            nomAuteur1 = result["nomAuteur"]["value"]
            if (result["prenomAuteur"]["value"] != ""):
                nomAuteur1 += " " + result["prenomAuteur"]["value"]
            nomAuteur1 = unidecode(nomAuteur1)
            nomAuteur2 = result["nomCollaborateur"]["value"]
            if (result["prenomCollaborateur"]["value"] != ""):
                nomAuteur2 += " " + result["prenomCollaborateur"]["value"]
            nomAuteur2 = unidecode(nomAuteur2)
            collaboration(nomAuteur1,nomAuteur2)
            arkCollaborateur = result["collaborateur"]["value"].replace("http://data.bnf.fr/","").replace("#foaf:Person","").replace("#about","").replace("#foaf:Organization","")
            dicArk2Nom[arkCollaborateur] = unidecode(result["nomCollaborateur"]["value"])
    
    #Pour chaque collaborateur trouvé à l'auteur principal, on 
    #relance la requête pour récupérer ses co-auteurs. On ne garde ceux-ci que s'ils sont dans la premièr eliste
    i = 1
    nbKeysdicArk2Nom = len(dicArk2Nom)
    FichierCollaborateurs = open("collaborateurs.txt","w")
    FichierCollaborateurs.write(str(dicArk2Nom))
    for ark in dicArk2Nom:
        print(str(i) + "/" + str(nbKeysdicArk2Nom) + ". " + ark + " : " + dicArk2Nom[ark])
        i = i+1
        lienscollaborateurs = auteur2collabSPARQL(ark)
        for result in lienscollaborateurs["results"]["bindings"]:
            if (result["nomAuteur"]["value"] != result["nomCollaborateur"]["value"]):
                arkCollaborateur = result["collaborateur"]["value"].replace("http://data.bnf.fr/","").replace("#foaf:Person","")
                if (arkCollaborateur in dicArk2Nom):
                    collaboration(unidecode(result["nomAuteur"]["value"]),unidecode(result["nomCollaborateur"]["value"]))
        
        
auteur2collab(entree)
