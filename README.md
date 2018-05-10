
# ADAotp - Analogue Data Acquisition of the poor

<img src="../master/Img/Start page.JPG" height="250"/> <img src="../master/Img/Monotoring page_1.JPG" height="250"/>
<img src="../master/Img/Monotoring page_2.JPG" height="250"/> <img src="../master/Img/Monotoring page_3.JPG" height="250"/>

Analogue Data Acquisition of the poor is a solution to acquire, real time monitoring and save analogue data from any kind of source that can send data throw serial connection as a comma separated string (<name of the 1st serie>,<numerical data of the 1st serie>,<units of the 1st serie>,<name of the 2nd serie>,<numerical data of the 2nd serie>,<units of the 2nd serie>, ...
i.e.  "Temperature1,19.87,°C,Temperature2,15.90,°C,Temperature3,395.02,°C,Current,183,mA,Hydrogen,473,ppm,Pressure,4.2361111640,Psi"

The project is composed of 2 different parts:
- The Arduino part that manage sensors and data formating for serial transfer.
- The Python part that:
  - receive data from serial connection (Arduino, RapsberryPy, other...)
  - Process data for real time visualization
  - Manage data saving to csv file for additionnal anylisis in spreadsheet or any kind of softwarecsv compatible.
  
Le projet se compose donc de 2 parties distinctes:
- La partie Arduino qui gérer les capteurs et la mise en forme des données pour leur transfère par liaison série.
- La partie Python qui 
  - lit le flux de données en provenance de l'Arduino, 
  - le met en forme pour sa visualisation en temps réel
  - permet le stockage des données sous forme de fichier csv pour une exploitation plus fine par un tableur ou tout autre application pouvant exploiter les données au format csv.
<img src="../master/Img/csv file.JPG" />
<img src="../master/Img/csv file_2.JPG" height="200"/><img src="../master/Img/csv file_3.JPG" height="200"/>

# Développements et améliorations souhaités à venir:

- Coté Arduino :
   - Gérer plusieurs capteurs de température simultanément I2C.
   - Inclure un capteur de tension (Volt) qui, associé au capteur de courant, permettra de monitorer une puissance consommée.
   - Inclure la gestion d'un multiplexeur analogique 16 voies (type 74HC4067 16-channel analog multiplexer/démultiplexer) pour augmenter la capacité gestion des sources analogiques de l'Arduino.
  - Optimisation du code (faire un truc plus clean ;) )
  
- Coté Python :
  - ~~Sauvegarde des paramètres~~ Fait
  - ~~Implémenter des StringVar() pour mettre à jour automatiquement différents libellés de l'interface graphique (Port COM , baudrate, etc...)~~ Fait mais pas avec des StringVar
  - ~~Paramétrer l'ordre et la disposition des graphiques non plus en dur dans le code, mais par choix dans l'interface graphique, quelle que soit l'ordre des données reçue de l'Arduino~~. Fait. Plusieurs dispositions possibles.
  - ~~Possibilité de nettoyer les graphiques (reset).~~ Fait
  - ~~Mettre en place la disposition des éléments graphiques par la méthode .grid et non plus .pack afin d'améliorer l'ergonomie et le rendu~~. Fait
  - ~~Choisir le nombre de graphiques et les données à afficher simultanément (Ex: un graphique unique du courant, ou 2 graphiques superposés avec 1 pour le courant et 1 autre pour la pression, 4 graphiques ...)~~ Fait
  - Choisir le nombre de données simultanées par graphique (Ex: le courant seul, le courant + la tension, le courant + la tension + la température, etc...)
  - Proposer des opération de calcul (Ex: Puissance = Tension * Courant
  - Produire des statistiques simples en temps réel (Max, min, Moyenne, écart type, ...)
  - produire des indicateurs visuels paramétrables (augmentation, stabilité, diminution)
  - Paramétrer des alertes simples (valeur supérieure à... inférieur à ... comprise entre...)

# Contributeurs
Christophe Campain
