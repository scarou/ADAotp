# ADAotp - Version Python 3.6 !

Initialement développé en Python 2.7, il est apparu utile de migrer vers Python 3.6 afin de disposer des dernières évolutions de Python et faciliter le recours à l'assitance de développeurs en Python.

<img src="../master/Img/Start page.JPG" height="250"/> <img src="../master/Img/Monotoring page_1.JPG" height="250"/>
<img src="../master/Img/Monotoring page_2.JPG" height="250"/> <img src="../master/Img/Monotoring page_3.JPG" height="250"/>

# Analogue Data Acquisition of the poor

Analogue Data Acquisition of the poor est une solution pour collecter, visualiser en temps réel et sauvegarder les données analogiques produites par des capteurs gérés par Arduino.

Le projet se compose donc de 2 parties distinctes:
- La partie Arduino qui gèrer les capteurs et la mise en forme des données pour leur transfère par liaison série.
- La partie Python qui 
  - lit le flux de données en provenance de l'Arduino, 
  - le met en forme pour sa visualisation en temps réel
  - permet le stockage des données sous forme de fichier csv pour une exploitation plus fine par un tableur ou tout autre application pouvant exploiter les données au format csv.
<img src="../master/Img/csv file.JPG" />
<img src="../master/Img/csv file_2.JPG" height="200"/><img src="../master/Img/csv file_3.JPG" height="200"/>

# Developpements et améliorations souhaités à venir:

- Coté Arduino :
   - Gérer plusieurs capteurs de température simultanément I2C.
   - Inclure un capteur de tension (Volt) qui, associé au capteur de courant, permettra de monitorer une puissance consommée.
   - Inclure la gestion d'un multiplexeur analogique 16 voies (type 74HC4067 16-channel analog multiplexer/demultiplexer) pour augmenter la capacité gestion des sources analogiques de l'Arduino.
  - Optimisation du code (faire un truc plus clean ;) )
  
- Coté Python :
  - Sauvegarde des paramètres
  - Implémenter des StringVar() pour mettre à jour automatiquement différents libellés de l'interface graphique (Port COM , baudrate, etc...)
  - Paraméter l'ordre et la disposition des graphiques non plus en dur dans le code, mais par choix dans l'interface graphique, quelle que soit l'ordre des données reçue de l'Arduino.
  - Possibilité de nettoyer les graphiques (reset).
  - Mettre en place la disposition des éléments graphiques par la méthode .grid et non plus .pack afin d'améliorer l'ergonomie et le rendu.
  - Choisir le nombre de graphiques et les données à afficher simultanément (Ex: un graphique unique du courant, ou 2 graphiques superposés avec 1 pour le courant et 1 aute pour la pression, 4 graphiques ...)
  - Choisir le nombre de données simultanées par graphique (Ex: le courant seul, le courant + la tension, le courant + la tension + la température, etc...)
  - Proposer des opération de calcul (Ex: Puissance = Tension * Courant
  - Produire des statistiques simples en temps réel (Max, min, Moyenne, écart type, ...)
  - produire des indicateurs visuels paramétrables (augmentation, stabilité, diminution)
  - Paramètrer des alertes simples (valeur supérieure à... inférieur à ... comprise entre...)

# Contributeurs
Christophe Campain