<?xml version="1.0" encoding="UTF-8"?>
<!--Feuille de style qui récupère un fichier en sortie du script Python databnf-concepts-properties.py
et en fait un fichier GEXF importable dans Gephi
Au passage, cette feuille de style XSL nettoie les espaces de nom de databnf en les remplaçant par leurs préfixes
Certains noeuds, liés uniquement à la déclaration de l'ontologie elle-même (et non au contenu des ressources dans data.bnf.fr
sont filtrées pour ne pas être envoyées dans Gephi-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output indent="yes"/>

  
<xsl:variable name="namespaces">
<it><uri>http://www.w3.org/2002/07/owl#</uri><ns>owl</ns></it>
<it><uri>http://www.w3.org/2001/XMLSchema#</uri><ns>xsd</ns></it>
<it><uri>http://purl.org/dc/dcmitype/</uri><ns>dcmitype</ns></it>
<it><uri>http://www.w3.org/2004/02/skos/core#</uri><ns>skos</ns></it>
<it><uri>http://www.w3.org/2000/01/rdf-schema#</uri><ns>rdfs</ns></it>
<it><uri>http://rdvocab.info/uri/schema/FRBRentitiesRDA/</uri><ns>frbr-rda</ns></it>
<it><uri>http://www.w3.org/2003/01/geo/wgs84_pos#</uri><ns>geo</ns></it>
<it><uri>http://data.bnf.fr/ontology/bnf-onto/</uri><ns>bnf-onto</ns></it>
<it><uri>http://rdvocab.info/RDARelationshipsWEMI/</uri><ns>rdarelationships</ns></it>
<it><uri>http://isni.org/ontology#</uri><ns>isni</ns></it>
<it><uri>http://www.w3.org/1999/02/22-rdf-syntax-ns#</uri><ns>rdf</ns></it>
<it><uri>http://www.w3.org/TR/owl-time/</uri><ns>owl-time</ns></it>
<it><uri>http://www.loc.gov/standards/mads/rdf/v1.html#</uri><ns>madsrdf</ns></it>
<it><uri>http://id.loc.gov/vocabulary/relators/</uri><ns>marcrel</ns></it>
<it><uri>http://www.w3.org/XML/1998/namespace</uri><ns>xml</ns></it>
<it><uri>http://purl.org/dc/terms/</uri><ns>dcterms</ns></it>
<it><uri>http://purl.org/ontology/bibo/</uri><ns>bibo</ns></it>
<it><uri>http://rdvocab.info/ElementsGr2/</uri><ns>rdagroup2elements</ns></it>
<it><uri>http://data.bnf.fr/vocabulary/roles/</uri><ns>bnf-roles</ns></it>
<it><uri>http://xmlns.com/foaf/0.1/</uri><ns>foaf</ns></it>
<it><uri>http://www.openlinksw.com/schemas/virtrdf#</uri><ns>lod</ns></it>
<it><uri>http://www.w3.org/2003/06/sw-vocab-status/ns#</uri><ns>sw-vocab</ns></it>
<it><uri>http://metadataregistry.org/uri/profile/RegAp/</uri><ns>regap</ns></it>
<it><uri>http://www.w3.org/ns/sparql-service-description#</uri><ns>spq</ns></it>
<it><uri>http://www.loc.gov/mads/rdf/v1#</uri><ns>madsrdf</ns></it>
<it><uri>http://id.loc.gov/vocabulary/iso639-2/</uri><ns>iso639-2</ns></it>
<it><uri>http://purl.org/dc/dcam/</uri><ns>dcdcam</ns></it>
</xsl:variable>
  
  <xsl:template name="solve_ns">
    <xsl:param name="long_uri"/>
    <xsl:variable name="resolution">
              <xsl:for-each select="$namespaces//it">
                <xsl:if test="contains($long_uri, uri)">
                  <xsl:value-of select="ns"/>:<xsl:value-of select="substring-after($long_uri, uri)"/>
                </xsl:if>
              </xsl:for-each>
              </xsl:variable>
              <xsl:choose>
                <xsl:when test="$resolution = ''"><xsl:value-of select="$long_uri"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="$resolution"/></xsl:otherwise>
              </xsl:choose>
  </xsl:template>
  
    <xsl:template match="/">
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
    <meta lastmodifieddate="2016-04-28">
        <creator>Etienne Cavalié</creator>
        <description>Données data.bnf.fr</description>
    </meta>
    <graph mode="static" defaultedgetype="directed">
        <nodes>
            <xsl:for-each select="//item/field[@name='Domaines']">
            <xsl:choose>
              <xsl:when test=". = 'http://www.w3.org/2000/01/rdf-schema#Class' or . = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property' or . = 'http://www.w3.org/2002/07/owl#Property' or . = 'http://www.w3.org/2002/07/owl#Class' or starts-with(., 'http://www.w3.org/ns/sparql-service-description#') or starts-with(., 'http://www.openlinksw.com/schemas/virtrdf#')"/>
            <xsl:otherwise>
            <xsl:variable name="pos" select="concat(parent::item/position(), '-', position())"/>
              <xsl:variable name="precedents">
                <xsl:for-each select="preceding::item">
                  <xsl:value-of select="field[@name='Domaines']"/>|<xsl:value-of select="field[@name='Sous-domaines']"/>|
                </xsl:for-each>
                </xsl:variable>
                <xsl:if test="not(contains($precedents, .))">
                  <node>
                    <xsl:attribute name="id">
                      <xsl:call-template name="solve_ns"><xsl:with-param name="long_uri" select="."/></xsl:call-template>
                    </xsl:attribute>
                      <xsl:attribute name="label">
                      <xsl:call-template name="solve_ns"><xsl:with-param name="long_uri" select="."/></xsl:call-template>
                    </xsl:attribute>
                  </node>
                </xsl:if></xsl:otherwise></xsl:choose>
           </xsl:for-each>
            <xsl:for-each select="//item/field[@name='Sous-domaines']">
<xsl:choose>
              <xsl:when test=". = 'http://www.w3.org/2000/01/rdf-schema#Class' or . = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property' or . = 'http://www.w3.org/2002/07/owl#Property' or . = 'http://www.w3.org/2002/07/owl#Class' or starts-with(., 'http://www.w3.org/ns/sparql-service-description#') or starts-with(., 'http://www.openlinksw.com/schemas/virtrdf#')"/>
                          <xsl:otherwise>
            <xsl:variable name="value" select="."/>
            <xsl:variable name="label">
              <xsl:for-each select="$namespaces//it">
                <xsl:if test="contains($value, uri)">
                  <xsl:value-of select="substring-after($value, uri)"/>
                </xsl:if>
              </xsl:for-each>
            </xsl:variable>
            <xsl:variable name="pos" select="concat(parent::item/position(), '-', position())"/>
              <xsl:variable name="precedents">
                <xsl:for-each select="preceding::item">
                  <xsl:value-of select="field[@name='Domaines']"/>|<xsl:value-of select="field[@name='Sous-domaines']"/>|
                </xsl:for-each>
              </xsl:variable>
                <xsl:if test="not(contains($precedents, .))">
                  <node>
                    <xsl:attribute name="id">
                      <xsl:call-template name="solve_ns"><xsl:with-param name="long_uri" select="."/></xsl:call-template>
                    </xsl:attribute>
                      <xsl:attribute name="label">
                      <xsl:call-template name="solve_ns"><xsl:with-param name="long_uri" select="."/></xsl:call-template>
                    </xsl:attribute>
                  </node>
                </xsl:if></xsl:otherwise></xsl:choose>
            </xsl:for-each>
        </nodes>
        <edges>
            <xsl:for-each select="//item">
            <xsl:choose>
                    <xsl:when test="contains(.,  'http://www.w3.org/2000/01/rdf-schema#Class') or contains(.,  'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property') or contains(., 'http://www.w3.org/2002/07/owl#Property') or contains(., 'http://www.w3.org/2002/07/owl#Class') or contains(., 'http://www.w3.org/ns/sparql-service-description#') or contains(., 'http://www.openlinksw.com/schemas/virtrdf#')"/>
            <xsl:otherwise>
              <edge>
                <xsl:attribute name="id"><xsl:value-of select="position()"/></xsl:attribute>
                <xsl:attribute name="label">
                      <xsl:call-template name="solve_ns"><xsl:with-param name="long_uri" select="field[@name='Proprietes']"/></xsl:call-template>
                    </xsl:attribute>
                      <xsl:attribute name="source">
                      <xsl:call-template name="solve_ns"><xsl:with-param name="long_uri" select="field[@name='Domaines']"/></xsl:call-template>
                    </xsl:attribute>
                      <xsl:attribute name="target">
                      <xsl:call-template name="solve_ns"><xsl:with-param name="long_uri" select="field[@name='Sous-domaines']"/></xsl:call-template>
                    </xsl:attribute>
                <xsl:attribute name="weight"><xsl:value-of select="field[@name='Nb_Liens']"/></xsl:attribute>
                </edge>
              </xsl:otherwise></xsl:choose>
            </xsl:for-each>
        </edges>
    </graph>
</gexf>
  </xsl:template>
</xsl:stylesheet>
