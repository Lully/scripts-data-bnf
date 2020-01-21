# coding: utf-8

from SPARQLWrapper import SPARQLWrapper, XML
from collections import defaultdict
from lxml import etree
from pprint import pprint
import urllib.parse
import urllib.request

from stdf import create_file, line2report

ns = {"s":"http://www.w3.org/2005/sparql-results#"}

def query2results(outputfile):
    liste_concepts = {}
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
	SELECT ?uri ?label WHERE {
	  ?uri a skos:Concept ; skos:prefLabel ?label.
	
   FILTER (
     !EXISTS {
      FILTER CONTAINS (str(?uri), "67717").
     }
    )
    }
    LIMIT 100
    """
    url = f"http://data.culture.fr/thesaurus/sparql?query={urllib.parse.quote(query.replace(' ', '+'))}"
    page2arkSet = etree.parse(urllib.request.urlopen(url))
    for result in page2arkSet.xpath("//s:result", namespaces=ns):
        uri = result.find("s:binding[@name='uri']/s:uri", namespaces=ns).text
        label = result.find("s:binding[@name='label']/s:literal", namespaces=ns).text
        liste_concepts[uri] = label
        line2report([uri, label], outputfile)



if __name__ == "__main__":
    outputfile = create_file("extraction_ginco.txt")
    query2results(outputfile)