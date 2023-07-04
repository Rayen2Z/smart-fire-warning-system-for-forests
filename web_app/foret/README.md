Il s'agit ici d'une application web qui fonctionne sous DJANGO.

Son arborescence est comme suit : 

- L’application principale est représentée par le dossier foret, mais cette dernière ne contient pas de template ni de fonctions 
utiles dans notre cas (elle ne fait que router les requêtes vers la sous application Charts qui elle fait tous les traitements).
 
- L’application charts se trouve dans le dossier charts et possède le dossier static qui comprend tous les éléments statiques de notre page web
(CSS, JAVASCRIPT ….) et le dossier template qui lui contient la page HTML qui affiche le graph. 

Deux fichiers sont importants dans le dossier charts se sont views.py et urls.py 
(les autres fichiers sont des fichiers automatiquement générés lors de la création de l’application et n’ont pas été modifiés). 

	- urls.py a pour fonction d'intercepter les requêtes et d’appeler les fonctions correspondantes. 
	- views.py contient deux fonctions index() et update_chart() : 
		index est appelé lors de la première consultation de la page qui affiche le graph.
		update_chart est utilisée pour mettre à jour automatiquement le graph, elle est appelée automatiquement par une fonction JAVASCRIPT.
