<?php

/*
Récupération des n° ARK et NNB à partir d'une requête par ISBN
Principe : parser la page HTML, ouvrir chaque notice résultat (de la première page de résultats, donc <= 10 résultats) et récupérer l'ARK
*/

header('Content-Type: text/xml');
echo '<?xml version="1.0" encoding="UTF-8"?>';

$isbn = $_GET['isbn'];
$url = "http://catalogue.bnf.fr/rechercher.do?motRecherche=" . $isbn . "&amp;critereRecherche=0&amp;depart=0&amp;facetteModifiee=ok"; 


$ch = curl_init();
$timeout = 5;
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
$html = curl_exec($ch);
curl_close($ch);

# Create a DOM parser object
$dom = new DOMDocument();
@$dom->loadHTML($html);

echo "<bnf service='isbn2ark' author='Etienne Cavalie - Lully - rien d officiel ici (pur bricolage)'>\n";
echo "<query>\n";
echo "<isbn>$isbn</isbn>\n";
echo "<url>$url</url>\n";
echo '</query>';
echo '<result>';

function isbn2ark($source) 
 {
 	if (is_object($source)) {
  #foreach($source ->find('input[name]') as $element) 
  foreach($source ->getElementsByTagName('a') as $abbr_record) 
    {
       $title = $abbr_record->getAttribute("title");
       if ($title == "Voir la notice") 
       	{
		   $ark = $abbr_record->getAttribute("href"); 
		   $ark = substr($ark,1);
		   $nnb = substr($ark, 13, 8);
		   $arkCatalogue = "http://catalogue.bnf.fr/$ark";
		   
			   echo "<ark arkId='$ark' nnb='$nnb'>$arkCatalogue</ark>\n";
      }
   }	
 }
}

isbn2ark($dom);
echo "</result>\n";

echo '</bnf>';

?>
