# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:01:25 2017

@author: Lully
"""

from lxml import etree
from lxml.html import parse
from urllib import request
from collections import defaultdict

ns = {"bnf-onto":"http://data.bnf.fr/ontology/bnf-onto/", 
      "bnfroles":"http://data.bnf.fr/vocabulary/roles/", 
      "dcterms":"http://purl.org/dc/terms/", 
      "foaf":"http://xmlns.com/foaf/0.1/", 
      "marcrel":"http://id.loc.gov/vocabulary/relators/", 
      "owl":"http://www.w3.org/2002/07/owl#", 
      "rdagroup1elements":"http://rdvocab.info/Elements/", 
      "rdarelationships":"http://rdvocab.info/RDARelationshipsWEMI/", 
      "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", 
      "rdfs":"http://www.w3.org/2000/01/rdf-schema#"}

urlroot = input("URL racine : ")

if (urlroot == ""):
    urlroot = "http://pfvdata.bnf.fr/"

#URI test page Auteur
URIaut = "11896834/christine_de_pisan/"
pageAUT = parse(urlroot + URIaut)
ARKaut = pageAUT.find("//meta[@name='DC.identifier']").get("content")
#URI manifestation pour tests Expression, Oeuvre, Concept
ARKmanif = "ark:/12148/cb380880420"
#URI manifestation pour test relation sujet
ARKmanifSujet = "ark:/12148/cb358430469"

resultats = defaultdict(bool)

    
def func_test_generique(page,path):
    print(path)
    test = False
    if (page.find(path, namespaces=ns) is True):
        test = True
    return test

#==============================================================================
# 1. Vérifier que l'export RDF d'une page Auteur contient bien !
# 	a. l'ARK#about de la personne : a un rdf:type foaf:Person ou foaf:Organization
# 	b. la relation ARK foaf:focus ARK#about
# 	c. la relation ARK#about owl:sameAs ARK#foaf:Person/foaf:Organization
#     
#==============================================================================

def checkRDFAuthor(URIauteur,ARK):
    URIautRDFXML = urlroot + URIauteur + "rdf.xml"
    page = etree.parse(request.urlopen(URIautRDFXML))
#test 1.a
    path = "//rdf:Description[@rdf:about='" + urlroot + ARK + "#about']/rdf:type"
    resultats["Auteur_testType"] = func_test_attribut(page,path, "rdf:resource", "http://xmlns.com/foaf/0.1","contains")
#test 1.b  
    path = "//rdf:Description[@rdf:about='" + urlroot + ARK + "']/foaf:focus[@rdf:resource='" + urlroot + ARK + "#about" + "']"      
    resultats["Auteur_testfocus"] = func_test_generique(page,path)
#test 1.c
    path = "//rdf:Description[@rdf:about='" + urlroot + ARK + "#about']/owl:sameAs[@rdf:resource='" + urlroot + ARK + "#foaf:Person']"
    resultats["Auteur_testsameAs"] = func_test_generique(page,path)


def func_test_attribut(page,path,attr_name,string,test):
    test = False
    count = 0
    if (test == "contains"):
        for node in page.xpath(path, namespaces=ns):
            attr_value = node.get(attr_name)
            if (attr_value.find(string) > -1):
                count += 1
    if (count > 0):
        test = True
    return test
#==============================================================================
# 2. Vérifier qu'une sérialisation RDF d'un ARK de manifestation contient :
# 	a. ARKmanif#about a frbr-rda:Manifestation
# 	b. ARKmanif#Expression a frbr-rda:Expression
# 	c. ARKmanif#about rdarelationships:expressionManifested ARKmanif#Expression
# 	d. ARKmanif foaf:focus ARKmanif#about
# 	e. ARKmanif a foaf:Document
# 	f. ARKmanif#about rdarelationships:workManifested ARKoeuvre#about
# 	
#==============================================================================

def checkRDFManif(ARKmanif):
    URImanifRDFXML = urlroot + ARKmanif
    page = etree.parse(request.urlopen(URImanifRDFXML))
#test 2.a
    path = "//rdf:Description[@rdf:about='" + urlroot + ARKmanif + "#about']/rdf:type[@rdf:resource='http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation']"
    resultats["Manif_testType"] = func_test_generique(page,path)

#test 2.b
    path = "//rdf:Description[@rdf:about='" + urlroot + ARKmanif + "#Expression']/rdf:type[@rdf:resource='http://rdvocab.info/uri/schema/FRBRentitiesRDA/Expression']"
    resultats["Expression_testType"] = func_test_generique(page,path)        
#test 2.c
    path = "//rdf:Description[@rdf:about='" + urlroot + ARKmanif + "#about']/rdarelationships:expressionManifested[@rdf:resource='" + ARKmanif + "#Expression']"
    resultats["Manif_lien_Expression"] = func_test_generique(page,path)        
#test 2.d
    path = "//rdf:Description[@rdf:about='" + urlroot + ARKmanif + "']/foaf:focus[@rdf:resource='" + ARKmanif + "#about']"
    resultats["Manif_foaf_focus"] = func_test_generique(page,path)        
#test 2.e
    path = "//rdf:Description[@rdf:about='" + urlroot + ARKmanif + "']/rdf:type[@rdf:resource='http://www.w3.org/2004/02/skos/core#Concept']"
    resultats["Manif_foaf_document"] = func_test_generique(page,path)        
#test 2.f
    path = "//rdf:Description[@rdf:about='" + urlroot + ARKmanif + "#about']/rdarelationships:workManifested[contains(@rdf:resource,'#about')]"
    resultats["Manif_lien_oeuvre"] = func_test_attribut(page,path,"rdf:resource","#about","contains")        
#==============================================================================
# 3. Vérifier la relation manifestation - sujet
# 	a. ARKmanif#about dcterms:subject ARKsujet
#==============================================================================
def checkRDFManifSujet(ARKmanif):
    URImanifRDFXML = urlroot + ARKmanif
    page = etree.parse(request.urlopen(URImanifRDFXML))
    path = "//rdf:Description[@rdf:about='" + urlroot + ARKmanif + "#about']/dcterms:subject"
    resultats["Manif_Sujet"] = func_test_attribut(page,path,"rdf:resource","ark","contains")        


def checkAll():
    checkRDFAuthor(URIaut,ARKaut)
    checkRDFManif(ARKmanif)
    checkRDFManifSujet(ARKmanifSujet)
    
if __name__ == '__main__':
    checkAll()
    print(resultats)
