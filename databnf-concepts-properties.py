# coding: utf-8
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv as csv
from lxml import etree
import io

sparqlEndpoint = "http://data.bnf.fr/sparql"

# Requête SPARQL qui récupère la liste des classes dans data.bnf.fr
# et compte le nombre d'instances pour ces classes.
# la sortie est un fichier XML qui, associé à un fichier XSL (https://github.com/Lully/scripts-data-bnf/blob/master/databnf-concepts-properties2gexf.xsl)
# permet de générer du GEXF (importable dans Gephi)

directory = input("Repertoire de destination : ")
nomStr = input("Nom du fichier")



#Correction sur la valeur du directory : ajout d'un antislash à la fin s'il n'y en a pas deja un
if (directory[len(directory)-1] == "\\" or directory[len(directory)-1] == "/"):
    directory = directory
else:
    if (directory.find("\\") == -1):
        directory = directory + "/"
    else:
        directory = directory + "\\"


sparql = SPARQLWrapper(sparqlEndpoint)

sparql.setQuery("""
select distinct ?Concept where {[] a ?Concept.}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
datasetConcepts = results["results"]["bindings"]

ListeConcepts = []

for element in datasetConcepts:
    ListeConcepts.append(element.get("Concept").get("value"))

#print (ListeConcepts)

#3 listes (ensuites mises en dataFrame :
#Col 1 = liste concepts
#Col 2 = liste des propriétés associées aux ressources ayant pour type ces concepts
#Col 3 = Classe du sous-domaine pour cette propriété
#Col 4 = Nb de fois où une ressource se voit affecter la propriété
ListesConceptsProprietes1 = []
ListesConceptsProprietes2 = []
ListesConceptsProprietes3 = []
ListesConceptsProprietes4 = []

for Concept in ListeConcepts:
    sparql = SPARQLWrapper(sparqlEndpoint)
    sparql.setQuery("""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    select distinct ?prop (count(?prop) as ?NbProp) ?typeRange where {
    ?item a <""" + Concept + """>.
    ?item ?prop ?val.
    OPTIONAL  {?val a ?typeRange.}
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    datasetProprietes = results["results"]["bindings"]
    for el in datasetProprietes:
        ListesConceptsProprietes1.append(Concept)
        ListesConceptsProprietes2.append(el.get("prop").get("value"))
        range = Concept + "litteral"
        if el.get("typeRange"):
            range = el.get("typeRange").get("value")
        ListesConceptsProprietes3.append(range)
        ListesConceptsProprietes4.append(el.get("NbProp").get("value"))

#2e requête, spécifique à data.bnf.fr : les mentions de responsabilités sont assumées
# par des URI#Expression, URI#Work, qui n'ont pas forcément de classe définie
#Mais comme la liste est trop longue, il découper en autant de requêtes qu'il y a de propriétés possibles. Donc
# 1. Une requête pour récupérer les propriétés
# 2. Pour chaque propriété, un ensemble de requêtes...


"""PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
select distinct ?prop where {
  {?Expression ?prop ?person.
  ?person a foaf:Person.
  ?person a ?typeRange} 
  UNION 
  {?Expression ?prop ?org.
  ?org a foaf:Organization.
  ?org  a ?typeRange}.
  MINUS{?Expression a ?typeExpression}
    }
"""
listeProp = ['http://purl.org/dc/terms/contributor','http://data.bnf.fr/vocabulary/roles/r360','http://data.bnf.fr/vocabulary/roles/r3060','http://data.bnf.fr/vocabulary/roles/r70','http://data.bnf.fr/vocabulary/roles/r680','http://data.bnf.fr/vocabulary/roles/r330','http://data.bnf.fr/vocabulary/roles/r440','http://id.loc.gov/vocabulary/relators/bsl','http://data.bnf.fr/vocabulary/roles/r100','http://data.bnf.fr/vocabulary/roles/r1010','http://purl.org/dc/terms/subject','http://data.bnf.fr/vocabulary/roles/r1110','http://id.loc.gov/vocabulary/relators/nrt','http://data.bnf.fr/vocabulary/roles/r170','http://data.bnf.fr/vocabulary/roles/r620','http://id.loc.gov/vocabulary/relators/red','http://data.bnf.fr/vocabulary/roles/r990','http://data.bnf.fr/vocabulary/roles/r110','http://data.bnf.fr/vocabulary/roles/r10','http://data.bnf.fr/vocabulary/roles/r1130','http://id.loc.gov/vocabulary/relators/rsg','http://data.bnf.fr/vocabulary/roles/r610','http://data.bnf.fr/vocabulary/roles/r1040','http://id.loc.gov/vocabulary/relators/cnd','http://id.loc.gov/vocabulary/relators/edt','http://id.loc.gov/vocabulary/relators/prt','http://data.bnf.fr/vocabulary/roles/r630','http://id.loc.gov/vocabulary/relators/aus','http://id.loc.gov/vocabulary/relators/aut','http://id.loc.gov/vocabulary/relators/trl','http://id.loc.gov/vocabulary/relators/pbd','http://id.loc.gov/vocabulary/relators/ill','http://data.bnf.fr/vocabulary/roles/r3260','http://id.loc.gov/vocabulary/relators/ccp','http://id.loc.gov/vocabulary/relators/act','http://data.bnf.fr/vocabulary/roles/r550','http://id.loc.gov/vocabulary/relators/aui','http://data.bnf.fr/vocabulary/roles/r1030','http://id.loc.gov/vocabulary/relators/sng','http://id.loc.gov/vocabulary/relators/clb','http://data.bnf.fr/vocabulary/roles/r460','http://id.loc.gov/vocabulary/relators/rpt','http://data.bnf.fr/vocabulary/roles/r220','http://id.loc.gov/vocabulary/relators/cmp','http://id.loc.gov/vocabulary/relators/adp','http://data.bnf.fr/vocabulary/roles/r1160','http://data.bnf.fr/vocabulary/roles/r450','http://id.loc.gov/vocabulary/relators/ivr','http://data.bnf.fr/vocabulary/roles/r1120','http://id.loc.gov/vocabulary/relators/voc','http://data.bnf.fr/vocabulary/roles/r210','http://id.loc.gov/vocabulary/relators/com','http://id.loc.gov/vocabulary/relators/pht','http://data.bnf.fr/vocabulary/roles/r500','http://data.bnf.fr/vocabulary/roles/r980','http://id.loc.gov/vocabulary/relators/cwt','http://data.bnf.fr/vocabulary/roles/r120','http://data.bnf.fr/vocabulary/roles/r9990','http://id.loc.gov/vocabulary/relators/prf','http://data.bnf.fr/vocabulary/roles/r530','http://data.bnf.fr/vocabulary/roles/r1850','http://data.bnf.fr/vocabulary/roles/r1860','http://data.bnf.fr/vocabulary/roles/r200','http://id.loc.gov/vocabulary/relators/cur','http://data.bnf.fr/vocabulary/roles/r310','http://id.loc.gov/vocabulary/relators/drm','http://data.bnf.fr/vocabulary/roles/r1310','http://data.bnf.fr/vocabulary/roles/r230','http://id.loc.gov/vocabulary/relators/itr','http://data.bnf.fr/vocabulary/roles/r1210','http://data.bnf.fr/vocabulary/roles/r1570','http://data.bnf.fr/vocabulary/roles/r380','http://id.loc.gov/vocabulary/relators/art','http://data.bnf.fr/vocabulary/roles/r2080','http://id.loc.gov/vocabulary/relators/cst','http://data.bnf.fr/vocabulary/roles/r40','http://id.loc.gov/vocabulary/relators/ann','http://data.bnf.fr/vocabulary/roles/r1080','http://data.bnf.fr/vocabulary/roles/r160','http://id.loc.gov/vocabulary/relators/chr','http://data.bnf.fr/vocabulary/roles/r4010','http://data.bnf.fr/vocabulary/roles/r290','http://data.bnf.fr/vocabulary/roles/r1060','http://id.loc.gov/vocabulary/relators/dnc','http://id.loc.gov/vocabulary/relators/fmo','http://id.loc.gov/vocabulary/relators/dte','http://data.bnf.fr/vocabulary/roles/r560','http://id.loc.gov/vocabulary/relators/ins','http://data.bnf.fr/vocabulary/roles/r1280','http://data.bnf.fr/vocabulary/roles/r520','http://data.bnf.fr/vocabulary/roles/r1990','http://id.loc.gov/vocabulary/relators/lyr','http://data.bnf.fr/vocabulary/roles/r510','http://data.bnf.fr/vocabulary/roles/r1150','http://data.bnf.fr/vocabulary/roles/r1650','http://data.bnf.fr/vocabulary/roles/r1667','http://data.bnf.fr/vocabulary/roles/r1180','http://data.bnf.fr/vocabulary/roles/r410','http://id.loc.gov/vocabulary/relators/egr','http://data.bnf.fr/vocabulary/roles/r311','http://data.bnf.fr/vocabulary/roles/r3250','http://data.bnf.fr/vocabulary/roles/r280','http://id.loc.gov/vocabulary/relators/crr','http://id.loc.gov/vocabulary/relators/pbl','http://data.bnf.fr/vocabulary/roles/r312','http://data.bnf.fr/vocabulary/roles/r50','http://id.loc.gov/vocabulary/relators/arr','http://data.bnf.fr/vocabulary/roles/r320','http://id.loc.gov/vocabulary/relators/rcp','http://data.bnf.fr/vocabulary/roles/r90','http://id.loc.gov/vocabulary/relators/anm','http://data.bnf.fr/vocabulary/roles/r1560','http://data.bnf.fr/vocabulary/roles/r72','http://id.loc.gov/vocabulary/relators/ant','http://data.bnf.fr/vocabulary/roles/r1580','http://data.bnf.fr/vocabulary/roles/r1450','http://data.bnf.fr/vocabulary/roles/r540','http://id.loc.gov/vocabulary/relators/aft','http://data.bnf.fr/vocabulary/roles/r340','http://id.loc.gov/vocabulary/relators/aud','http://data.bnf.fr/vocabulary/roles/r223','http://data.bnf.fr/vocabulary/roles/r1287','http://data.bnf.fr/vocabulary/roles/r1320','http://data.bnf.fr/vocabulary/roles/r1567','http://data.bnf.fr/vocabulary/roles/r1938','http://data.bnf.fr/vocabulary/roles/r1380','http://data.bnf.fr/vocabulary/roles/r1230','http://data.bnf.fr/vocabulary/roles/r71','http://id.loc.gov/vocabulary/relators/att','http://data.bnf.fr/vocabulary/roles/r1460','http://data.bnf.fr/vocabulary/roles/r430','http://data.bnf.fr/vocabulary/roles/r1930','http://data.bnf.fr/vocabulary/roles/r1428','http://data.bnf.fr/vocabulary/roles/r1590','http://data.bnf.fr/vocabulary/roles/r150','http://id.loc.gov/vocabulary/relators/ctg','http://data.bnf.fr/vocabulary/roles/r3290','http://data.bnf.fr/vocabulary/roles/r250','http://id.loc.gov/vocabulary/relators/sad','http://data.bnf.fr/vocabulary/roles/r1318','http://data.bnf.fr/vocabulary/roles/r1368','http://data.bnf.fr/vocabulary/roles/r1388','http://data.bnf.fr/vocabulary/roles/r1218','http://data.bnf.fr/vocabulary/roles/r1358','http://data.bnf.fr/vocabulary/roles/r1240','http://data.bnf.fr/vocabulary/roles/r1270','http://data.bnf.fr/vocabulary/roles/r1290','http://data.bnf.fr/vocabulary/roles/r2090','http://id.loc.gov/vocabulary/relators/std','http://data.bnf.fr/vocabulary/roles/r590','http://data.bnf.fr/vocabulary/roles/r1510','http://id.loc.gov/vocabulary/relators/prg','http://data.bnf.fr/vocabulary/roles/r644','http://data.bnf.fr/vocabulary/roles/r640','http://id.loc.gov/vocabulary/relators/scl','http://data.bnf.fr/vocabulary/roles/r531','http://data.bnf.fr/vocabulary/roles/r485','http://id.loc.gov/vocabulary/relators/pop','http://data.bnf.fr/vocabulary/roles/r190','http://id.loc.gov/vocabulary/relators/spn','http://data.bnf.fr/vocabulary/roles/r1190','http://data.bnf.fr/vocabulary/roles/r180','http://data.bnf.fr/vocabulary/roles/r1170','http://data.bnf.fr/vocabulary/roles/r1410','http://id.loc.gov/vocabulary/relators/col','http://data.bnf.fr/vocabulary/roles/r300','http://id.loc.gov/vocabulary/relators/dto','http://data.bnf.fr/vocabulary/roles/r4040','http://id.loc.gov/vocabulary/relators/dnr','http://data.bnf.fr/vocabulary/roles/r314','http://data.bnf.fr/vocabulary/roles/r1017','http://data.bnf.fr/vocabulary/roles/r365','http://data.bnf.fr/vocabulary/roles/r1420','http://data.bnf.fr/vocabulary/roles/r1100','http://data.bnf.fr/vocabulary/roles/r1760','http://data.bnf.fr/vocabulary/roles/r1299','http://data.bnf.fr/vocabulary/roles/r1767','http://data.bnf.fr/vocabulary/roles/r700','http://id.loc.gov/vocabulary/relators/scr','http://data.bnf.fr/vocabulary/roles/r4120','http://id.loc.gov/vocabulary/relators/dub','http://data.bnf.fr/vocabulary/roles/r73','http://id.loc.gov/vocabulary/relators/asn','http://data.bnf.fr/vocabulary/roles/r1220','http://data.bnf.fr/vocabulary/roles/r1668','http://data.bnf.fr/vocabulary/roles/r480','http://id.loc.gov/vocabulary/relators/ltg','http://data.bnf.fr/vocabulary/roles/r1630','http://data.bnf.fr/vocabulary/roles/r1550','http://data.bnf.fr/vocabulary/roles/r1217','http://data.bnf.fr/vocabulary/roles/r1830','http://data.bnf.fr/vocabulary/roles/r1520','http://data.bnf.fr/vocabulary/roles/r1108','http://data.bnf.fr/vocabulary/roles/r1400','http://data.bnf.fr/vocabulary/roles/r4140','http://id.loc.gov/vocabulary/relators/bnd','http://data.bnf.fr/vocabulary/roles/r1569','http://id.loc.gov/vocabulary/relators/cll','http://data.bnf.fr/vocabulary/roles/r144','http://data.bnf.fr/vocabulary/roles/r1119','http://data.bnf.fr/vocabulary/roles/r484','http://data.bnf.fr/vocabulary/roles/r2280','http://data.bnf.fr/vocabulary/roles/r1140','http://data.bnf.fr/vocabulary/roles/r1288','http://data.bnf.fr/vocabulary/roles/r1350','http://data.bnf.fr/vocabulary/roles/r270','http://data.bnf.fr/vocabulary/roles/r522','http://data.bnf.fr/vocabulary/roles/r660','http://data.bnf.fr/vocabulary/roles/r790','http://data.bnf.fr/vocabulary/roles/r1980','http://data.bnf.fr/vocabulary/roles/r1278','http://data.bnf.fr/vocabulary/roles/r534','http://data.bnf.fr/vocabulary/roles/r321','http://data.bnf.fr/vocabulary/roles/r1360','http://data.bnf.fr/vocabulary/roles/r1317','http://data.bnf.fr/vocabulary/roles/r126','http://data.bnf.fr/vocabulary/roles/r910','http://id.loc.gov/vocabulary/relators/rth','http://data.bnf.fr/vocabulary/roles/r1470','http://data.bnf.fr/vocabulary/roles/r222','http://data.bnf.fr/vocabulary/roles/r1707','http://data.bnf.fr/vocabulary/roles/r1840','http://data.bnf.fr/vocabulary/roles/r780','http://id.loc.gov/vocabulary/relators/lbt','http://data.bnf.fr/vocabulary/roles/r470','http://data.bnf.fr/vocabulary/roles/r1658','http://data.bnf.fr/vocabulary/roles/r260','http://id.loc.gov/vocabulary/relators/ctb','http://data.bnf.fr/vocabulary/roles/r3150','http://data.bnf.fr/vocabulary/roles/r4020','http://data.bnf.fr/vocabulary/roles/r690','http://id.loc.gov/vocabulary/relators/pro','http://data.bnf.fr/vocabulary/roles/r80','http://data.bnf.fr/vocabulary/roles/r350','http://id.loc.gov/vocabulary/relators/prd','http://data.bnf.fr/vocabulary/roles/r580','http://data.bnf.fr/vocabulary/roles/r3200','http://data.bnf.fr/vocabulary/roles/r3170','http://data.bnf.fr/vocabulary/roles/r2140','http://id.loc.gov/vocabulary/relators/lgd','http://data.bnf.fr/vocabulary/roles/r1440','http://data.bnf.fr/vocabulary/roles/r1430','http://id.loc.gov/vocabulary/relators/drt','http://data.bnf.fr/vocabulary/roles/r2100','http://data.bnf.fr/vocabulary/roles/r2990','http://id.loc.gov/vocabulary/relators/dst','http://data.bnf.fr/vocabulary/roles/r2095','http://data.bnf.fr/vocabulary/roles/r2216','http://data.bnf.fr/vocabulary/roles/r524','http://data.bnf.fr/vocabulary/roles/r570','http://data.bnf.fr/vocabulary/roles/r41','http://data.bnf.fr/vocabulary/roles/r130','http://id.loc.gov/vocabulary/relators/wam','http://data.bnf.fr/vocabulary/roles/r4080','http://data.bnf.fr/vocabulary/roles/r1700','http://data.bnf.fr/vocabulary/roles/r1717','http://data.bnf.fr/vocabulary/roles/r770','http://data.bnf.fr/vocabulary/roles/r1770','http://id.loc.gov/vocabulary/relators/rce','http://data.bnf.fr/vocabulary/roles/r2300','http://data.bnf.fr/vocabulary/roles/r2085','http://data.bnf.fr/vocabulary/roles/r2260','http://data.bnf.fr/vocabulary/roles/r4170','http://data.bnf.fr/vocabulary/roles/r473','http://data.bnf.fr/vocabulary/roles/r3160','http://data.bnf.fr/vocabulary/roles/r2050','http://data.bnf.fr/vocabulary/roles/r2010','http://data.bnf.fr/vocabulary/roles/r1427','http://data.bnf.fr/vocabulary/roles/r2145','http://data.bnf.fr/vocabulary/roles/r1637','http://data.bnf.fr/vocabulary/roles/r221','http://data.bnf.fr/vocabulary/roles/r600','http://id.loc.gov/vocabulary/relators/trc','http://data.bnf.fr/vocabulary/roles/r730','http://data.bnf.fr/vocabulary/roles/r1289','http://data.bnf.fr/vocabulary/roles/r1638','http://data.bnf.fr/vocabulary/roles/r3210','http://data.bnf.fr/vocabulary/roles/r1780','http://data.bnf.fr/vocabulary/roles/r1480','http://id.loc.gov/vocabulary/relators/org','http://data.bnf.fr/vocabulary/roles/r1777','http://data.bnf.fr/vocabulary/roles/r370','http://data.bnf.fr/vocabulary/roles/r20','http://data.bnf.fr/vocabulary/roles/r1599','http://data.bnf.fr/vocabulary/roles/r1490','http://data.bnf.fr/vocabulary/roles/r414','http://data.bnf.fr/vocabulary/roles/r2220','http://data.bnf.fr/vocabulary/roles/r2255','http://data.bnf.fr/vocabulary/roles/r650','http://id.loc.gov/vocabulary/relators/sgn','http://data.bnf.fr/vocabulary/roles/r2210','http://id.loc.gov/vocabulary/relators/ppt','http://data.bnf.fr/vocabulary/roles/r111','http://data.bnf.fr/vocabulary/roles/r411','http://data.bnf.fr/vocabulary/roles/r2305','http://data.bnf.fr/vocabulary/roles/r2215','http://data.bnf.fr/vocabulary/roles/r1090','http://data.bnf.fr/vocabulary/roles/r2086','http://data.bnf.fr/vocabulary/roles/r4030','http://data.bnf.fr/vocabulary/roles/r2980','http://data.bnf.fr/vocabulary/roles/r3280','http://data.bnf.fr/vocabulary/roles/r505','http://data.bnf.fr/vocabulary/roles/r441','http://data.bnf.fr/vocabulary/roles/r1050','http://data.bnf.fr/vocabulary/roles/r1197','http://data.bnf.fr/vocabulary/roles/r1257','http://data.bnf.fr/vocabulary/roles/r1020','http://data.bnf.fr/vocabulary/roles/r161','http://data.bnf.fr/vocabulary/roles/r1718','http://data.bnf.fr/vocabulary/roles/r1250','http://data.bnf.fr/vocabulary/roles/r1260','http://data.bnf.fr/vocabulary/roles/r1387','http://data.bnf.fr/vocabulary/roles/r4180','http://data.bnf.fr/vocabulary/roles/r2200','http://id.loc.gov/vocabulary/relators/flm','http://data.bnf.fr/vocabulary/roles/r2230','http://data.bnf.fr/vocabulary/roles/r2290','http://data.bnf.fr/vocabulary/roles/r2120','http://data.bnf.fr/vocabulary/roles/r1277','http://data.bnf.fr/vocabulary/roles/r412','http://data.bnf.fr/vocabulary/roles/r152','http://data.bnf.fr/vocabulary/roles/r13','http://data.bnf.fr/vocabulary/roles/r4150','http://data.bnf.fr/vocabulary/roles/r710','http://id.loc.gov/vocabulary/relators/ilu','http://data.bnf.fr/vocabulary/roles/r4190','http://data.bnf.fr/vocabulary/roles/r101','http://data.bnf.fr/vocabulary/roles/r642','http://data.bnf.fr/vocabulary/roles/r1330','http://data.bnf.fr/vocabulary/roles/r4090','http://data.bnf.fr/vocabulary/roles/r471','http://data.bnf.fr/vocabulary/roles/r140','http://data.bnf.fr/vocabulary/roles/r3120','http://data.bnf.fr/vocabulary/roles/r60','http://data.bnf.fr/vocabulary/roles/r4070','http://data.bnf.fr/vocabulary/roles/r720','http://id.loc.gov/vocabulary/relators/rev','http://data.bnf.fr/vocabulary/roles/r171','http://data.bnf.fr/vocabulary/roles/r240','http://data.bnf.fr/vocabulary/roles/r154','http://data.bnf.fr/vocabulary/roles/r1597','http://data.bnf.fr/vocabulary/roles/r400','http://id.loc.gov/vocabulary/relators/srv','http://data.bnf.fr/vocabulary/roles/r1018','http://data.bnf.fr/vocabulary/roles/r1587','http://data.bnf.fr/vocabulary/roles/r1620','http://data.bnf.fr/vocabulary/roles/r1179','http://data.bnf.fr/vocabulary/roles/r173','http://data.bnf.fr/vocabulary/roles/r2146','http://data.bnf.fr/vocabulary/roles/r1730','http://data.bnf.fr/vocabulary/roles/r1738','http://data.bnf.fr/vocabulary/roles/r2340','http://data.bnf.fr/vocabulary/roles/r2110','http://data.bnf.fr/vocabulary/roles/r1827','http://data.bnf.fr/vocabulary/roles/r1657','http://data.bnf.fr/vocabulary/roles/r1660','http://data.bnf.fr/vocabulary/roles/r1239','http://data.bnf.fr/vocabulary/roles/r1690','http://data.bnf.fr/vocabulary/roles/r1558','http://data.bnf.fr/vocabulary/roles/r1610','http://data.bnf.fr/vocabulary/roles/r1920','http://data.bnf.fr/vocabulary/roles/r1390','http://data.bnf.fr/vocabulary/roles/r1670','http://data.bnf.fr/vocabulary/roles/r1249','http://data.bnf.fr/vocabulary/roles/r1478','http://data.bnf.fr/vocabulary/roles/r1370','http://data.bnf.fr/vocabulary/roles/r1013','http://data.bnf.fr/vocabulary/roles/r1407','http://data.bnf.fr/vocabulary/roles/r2150','http://data.bnf.fr/vocabulary/roles/r1101','http://data.bnf.fr/vocabulary/roles/r1200','http://data.bnf.fr/vocabulary/roles/r1640','http://data.bnf.fr/vocabulary/roles/r1900','http://data.bnf.fr/vocabulary/roles/r1378','http://data.bnf.fr/vocabulary/roles/r1527','http://data.bnf.fr/vocabulary/roles/r1477','http://data.bnf.fr/vocabulary/roles/r420','http://data.bnf.fr/vocabulary/roles/r1500','http://data.bnf.fr/vocabulary/roles/r1129','http://data.bnf.fr/vocabulary/roles/r1530','http://data.bnf.fr/vocabulary/roles/r1740','http://data.bnf.fr/vocabulary/roles/r900','http://data.bnf.fr/vocabulary/roles/r2360','http://data.bnf.fr/vocabulary/roles/r4060','http://id.loc.gov/vocabulary/relators/inv','http://data.bnf.fr/vocabulary/roles/r271','http://data.bnf.fr/vocabulary/roles/r532','http://data.bnf.fr/vocabulary/roles/r11','http://data.bnf.fr/vocabulary/roles/r3300','http://data.bnf.fr/vocabulary/roles/r850','http://data.bnf.fr/vocabulary/roles/r3090','http://data.bnf.fr/vocabulary/roles/r30','http://data.bnf.fr/vocabulary/roles/r670','http://data.bnf.fr/vocabulary/roles/r2190','http://data.bnf.fr/vocabulary/roles/r4990','http://data.bnf.fr/vocabulary/roles/r1367','http://data.bnf.fr/vocabulary/roles/r1357','http://data.bnf.fr/vocabulary/roles/r43','http://data.bnf.fr/vocabulary/roles/r151','http://data.bnf.fr/vocabulary/roles/r141','http://data.bnf.fr/vocabulary/roles/r1937','http://data.bnf.fr/vocabulary/roles/r4200','http://data.bnf.fr/vocabulary/roles/r2270','http://data.bnf.fr/vocabulary/roles/r3050','http://id.loc.gov/vocabulary/relators/ppm','http://data.bnf.fr/vocabulary/roles/r1039','http://data.bnf.fr/vocabulary/roles/r1031','http://data.bnf.fr/vocabulary/roles/r121','http://data.bnf.fr/vocabulary/roles/r1438','http://data.bnf.fr/vocabulary/roles/r1437','http://data.bnf.fr/vocabulary/roles/r1598','http://data.bnf.fr/vocabulary/roles/r3030','http://data.bnf.fr/vocabulary/roles/r1389','http://data.bnf.fr/vocabulary/roles/r1680','http://data.bnf.fr/vocabulary/roles/r1300','http://data.bnf.fr/vocabulary/roles/r1537','http://data.bnf.fr/vocabulary/roles/r1219','http://data.bnf.fr/vocabulary/roles/r3190','http://data.bnf.fr/vocabulary/roles/r1607','http://data.bnf.fr/vocabulary/roles/r1337','http://data.bnf.fr/vocabulary/roles/r1710','http://data.bnf.fr/vocabulary/roles/r3310','http://id.loc.gov/vocabulary/relators/prm','http://data.bnf.fr/vocabulary/roles/r2310','http://id.loc.gov/vocabulary/relators/tyg','http://data.bnf.fr/vocabulary/roles/r1258','http://data.bnf.fr/vocabulary/roles/r91','http://data.bnf.fr/vocabulary/roles/r1340','http://data.bnf.fr/vocabulary/roles/r3140','http://data.bnf.fr/vocabulary/roles/r1377','http://data.bnf.fr/vocabulary/roles/r2180','http://data.bnf.fr/vocabulary/roles/r1688','http://data.bnf.fr/vocabulary/roles/r1659','http://data.bnf.fr/vocabulary/roles/r1540','http://data.bnf.fr/vocabulary/roles/r2030','http://data.bnf.fr/vocabulary/roles/r1309','http://data.bnf.fr/vocabulary/roles/r1750','http://data.bnf.fr/vocabulary/roles/r2250','http://data.bnf.fr/vocabulary/roles/r1820','http://data.bnf.fr/vocabulary/roles/r3980','http://data.bnf.fr/vocabulary/roles/r1790','http://data.bnf.fr/vocabulary/roles/r1800','http://data.bnf.fr/vocabulary/roles/r273','http://data.bnf.fr/vocabulary/roles/r1720','http://data.bnf.fr/vocabulary/roles/r2060','http://data.bnf.fr/vocabulary/roles/r611','http://data.bnf.fr/vocabulary/roles/r1600','http://data.bnf.fr/vocabulary/roles/r2266','http://data.bnf.fr/vocabulary/roles/r3320','http://data.bnf.fr/vocabulary/roles/r51','http://data.bnf.fr/vocabulary/roles/r1728','http://data.bnf.fr/vocabulary/roles/r1557','http://data.bnf.fr/vocabulary/roles/r1747','http://data.bnf.fr/vocabulary/roles/r1797','http://data.bnf.fr/vocabulary/roles/r1940','http://data.bnf.fr/vocabulary/roles/r1459','http://data.bnf.fr/vocabulary/roles/r1169','http://data.bnf.fr/vocabulary/roles/r1817','http://data.bnf.fr/vocabulary/roles/r1837','http://data.bnf.fr/vocabulary/roles/r1418','http://data.bnf.fr/vocabulary/roles/r810','http://id.loc.gov/vocabulary/relators/mfr','http://data.bnf.fr/vocabulary/roles/r4050','http://data.bnf.fr/vocabulary/roles/r2350','http://id.loc.gov/vocabulary/relators/bjd','http://data.bnf.fr/vocabulary/roles/r103','http://data.bnf.fr/vocabulary/roles/r521','http://data.bnf.fr/vocabulary/roles/r490','http://data.bnf.fr/vocabulary/roles/r123','http://data.bnf.fr/vocabulary/roles/r93','http://data.bnf.fr/vocabulary/roles/r711','http://data.bnf.fr/vocabulary/roles/r3080','http://data.bnf.fr/vocabulary/roles/r481','http://data.bnf.fr/vocabulary/roles/r1748','http://data.bnf.fr/vocabulary/roles/r2370','http://data.bnf.fr/vocabulary/roles/r2206','http://data.bnf.fr/vocabulary/roles/r113','http://data.bnf.fr/vocabulary/roles/r53','http://data.bnf.fr/vocabulary/roles/r740','http://data.bnf.fr/vocabulary/roles/r2096','http://data.bnf.fr/vocabulary/roles/r2240','http://data.bnf.fr/vocabulary/roles/r313','http://data.bnf.fr/vocabulary/roles/r1947','http://data.bnf.fr/vocabulary/roles/r1159','http://data.bnf.fr/vocabulary/roles/r4130','http://data.bnf.fr/vocabulary/roles/r1870','http://data.bnf.fr/vocabulary/roles/r413','http://data.bnf.fr/vocabulary/roles/r4980','http://data.bnf.fr/vocabulary/roles/r1229','http://data.bnf.fr/vocabulary/roles/r2256','http://data.bnf.fr/vocabulary/roles/r443','http://data.bnf.fr/vocabulary/roles/r3240','http://data.bnf.fr/vocabulary/roles/r1139','http://data.bnf.fr/vocabulary/roles/r2040','http://data.bnf.fr/vocabulary/roles/r1149','http://data.bnf.fr/vocabulary/roles/r1807','http://data.bnf.fr/vocabulary/roles/r1948','http://data.bnf.fr/vocabulary/roles/r1810','http://data.bnf.fr/vocabulary/roles/r1011','http://data.bnf.fr/vocabulary/roles/r1649','http://data.bnf.fr/vocabulary/roles/r1033','http://data.bnf.fr/vocabulary/roles/r1268','http://data.bnf.fr/vocabulary/roles/r1888']



for prop in listeProp:
    sparql = SPARQLWrapper(sparqlEndpoint)
    sparql.setQuery("""
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX frbr-rda: <http://rdvocab.info/uri/schema/FRBRentitiesRDA/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    select distinct ?prop (count(?prop) as ?NbProp) where {
      ?frbrExpression a frbr-rda:Expression.
      ?frbrExpression  owl:sameAs ?Expression.
      ?Expression <""" + prop + """> ?val.
      ?Expression ?prop ?val.
        ?val a foaf:Person.
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    datasetProprietes = results["results"]["bindings"]
    for el in datasetProprietes:
        ListesConceptsProprietes1.append("Expression")
        ListesConceptsProprietes2.append(prop)
        ListesConceptsProprietes3.append("foaf:Person")
        ListesConceptsProprietes4.append(el.get("NbProp").get("value"))

for prop in listeProp:
    sparql = SPARQLWrapper(sparqlEndpoint)
    sparql.setQuery("""
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX frbr-rda: <http://rdvocab.info/uri/schema/FRBRentitiesRDA/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    select distinct ?prop (count(?prop) as ?NbProp) where {
      ?frbrExpression a frbr-rda:Expression.
      ?frbrExpression  owl:sameAs ?Expression.
      ?Expression <""" + prop + """> ?val
      ?Expression ?prop ?val.
        ?val a foaf:Organization.
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    datasetProprietes = results["results"]["bindings"]
    for el in datasetProprietes:
        ListesConceptsProprietes1.append("Expression")
        ListesConceptsProprietes2.append(prop)
        ListesConceptsProprietes3.append("foaf:Organization")
        ListesConceptsProprietes4.append(el.get("NbProp").get("value"))



s1 = pd.Series(ListesConceptsProprietes1, name='Domaines')
s2 = pd.Series(ListesConceptsProprietes2, name='Proprietes')
s3 = pd.Series(ListesConceptsProprietes3, name='Sous-domaines')
s4 = pd.Series(ListesConceptsProprietes4, name='Nb_Liens')

#s4 = pd.Series(ListeChamps041, name='Champs_041')

tableau = pd.concat([s1, s2, s3, s4], axis=1)
tableau_dedup = tableau.drop_duplicates


def func(row):
    xml = ['<item>']
    for field in row.index:
        xml.append('  <field name="{0}">{1}</field>'.format(field, row[field]))
    xml.append('</item>')
    return '\n'.join(xml)

tableauXML =  "\n".join(tableau_dedup.apply(func, axis=1))
tableauXML = "<?xml version='1.0' encoding='UTF-8'?>\n<root>\n" + tableauXML + "\n</root>"

#print(tableau)

#print (tableauXML)
#création du fichier XML encodé en UTF-8 (utilisation Codecs)

filename = directory + nomStr
with io.open(filename,'w',encoding='utf8') as f:
    f.write(tableauXML)
    f.close()
