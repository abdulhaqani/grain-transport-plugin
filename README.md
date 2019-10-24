# GrainTransportPyQGISScript

French text below

On the qgis python console, running this will provide the shortest path from 2 points on a train network.

# This system requires the following considerations to run smoothly.

- The model requires the following packages installed

  - dbfread
  - numpy
  - pandas
  - pip

- Lines 80-83 require edits for your project to operate. The edits are as follows;

  - The column names for each DF need to be changed to the names on your associated project. For example, if your length column on the .dbf file had a name "Length" instead of "LENGTHKM", just change the column name to yours. (Right side after self.df.\*)

- For inputs, the inputs are in the following formats;
  - FILENAME is input as: filename.dbf
  - FromTrackId and ToTrackId are based on the rail lines, rail lines are separated by junctions in qgis. Obtain the start and end line from the attribute table and input their unique IDs.
  - The inputs are all to be separated by commas with no spaces.
    - An example input is as follows:
      - C:\Users\NAME\QGISDatasets\Railway\JJunctTrack50BFinal.dbf,3d5fa20bbe56420a8298d44f9855d54b,f847646e1860467e957e3ba18b742a5f
- Lines 817, and 818 require the following edit;
  - The names of the layers need to be set to the name of your project layers. layer is the junction vector layer, layer2 is the track line vector layer
- Lines 850 and 853 require the following edit;
  - 'FTRACKNID' in line 850 needs to be changed to your track junction id column name, and 'NID' in line 853 needs to be changed to the track segment column name

The System works as follows;

- The track lines are given a time based on the lengths, line speed, and based on the trains that populate it.

  - The trains that populate it are given times based on the number of cars and size of cars on it.

    - The cars are given times based on their size.

- When trackline.getTime() is called, it obtains the time contributed by the tracks, and the time contributed by each train,
  and the trains get the time contributed by each car, then all of them are cascaded onto eachother.

- lines 832 to 845 are commented out, however, they have the more accurate representation of the path than lines 846 to 855. The reason why they were commented out is because of the overlapping junctions hiding selected layers. For the purpose of viewing a map, multidirectional junctions at the same location were all highlighted.

- lines 778 to 802 randomly populated the lines for the purpose of testing and viewing how the addition of trains and cars to the lines impacted the outputs. It worked fully as intended, however, on pyqgis due to the lower power of the pyqgis module when compared to a regular python console, it cause qgis to crash. When the algorithm was ran on an external console it ran exactly as intended and took less than 20 seconds to complete the path output.

---

# In this proof of concept the following variables have been taken into consideration;

- Railway types
- Number of lines for each track
- Distance between intersections
- Speed on the railway type
- Capacity of the railway (assumed a relationship between traffic and speed)
- Train types (passenger or freight)
- Weight of the Trains (not used, but basic requirements implemented)
- Number of Cars attached to the train
- Number of times cars are loaded/unloaded (assumed time relationship with size)
- Car size
- Whether the cars are full or not

---

# The following have not been implemented as of yet

- Train subclasses (acceleration, how they handle turns, length, whether they can traverse specific lines etc)
- Car partial loading/unloading, assumed 100% loading/unloading each time
- Train density at stations, as of now while loading/unloading assumed to not influence any moving trains
- Weather has completely been disregarded
- Time of year

---

# Next steps:

- To obtain a model with info more related to real life, run the model using a machine learning algorithm, likely a neural network with data for times given by a couple years of info. The datasets in the neural network machine learning algorithm would be as follows;

  - Time of day
  - Time of year
  - Time to travel between lines
  - Number of trains
  - Number of cars on trains
  - Number of stops by train

- Along with any other important information.

- Then using the neural network, the getTime methods can be edited using the machine learning algorithm. This would allow for a self improving model which would be fairly easily implemented by using data that is fairly easily acqiurable using the gps systems on each train.

- To go even further, real time info can be inputted on the machine learning algorithm to further optimize the system, though this would require a higher investment for the improved information.

- It should be noted that the implementation of the shortest path algorithm does not require edits to optimize the algorithm, rather it would require edits to the getTime methods, which once again can be done by inputting more accurate relations, or a machine learning algorithm.




# AnalysedeRéseau-TransportdesGrains

Dans la console qgis python, le fait d’exécuter ce code fournira le chemin le pl us cours à partir de deux points sur un réseau ferroviaire.

# Ce système requiert les considérations suivantes pour qu’il fonctionne bien. 

– Le modèle exige que les progiciels suivants soient installés

  - dbfread
  – numpy
  – pandas
  – pip

– Les lignes 80 à 83 doivent être modifiées pour que votre projet fonctionne. Voici les modifications : 

  – Le nom des colonnes pour chaque DF doit être modifié par le nom de votre projet associé. Par exemple, si votre colonne « longueur » dans le dossier .dbf portait le nom « Longeur » au lieu de « LNGRKM », modifiez tout simplement le nom de la colonne par le nom qui apparaît dans votre projet. (côté droit après self.df.\*)

– Quant aux données d’entrée, elles sont aux formats suivants : 
  – NOMFICHIER est entré comme nomfichier.dbf
  – VOIE_O_ODN et VOIE_D_IDN sont fondés sur les lignes des voies. Les lignes des voies sont séparées par des jonctions dans qgis. Obtenir la ligne de début et de fin à partir du tableau des attributs, et saisir leur ID unique.
  – Les données d’entrées doivent être séparées par des virgules sans espace.
    – Voici un exemple de donnée d’entrée: 
      – C:\Users\NAME\QGISDatasets\Railway\JJunctTrack50BFinal.dbf,3d5fa20bbe56420a8298d44f9855d54b,f847646e1860467e957e3ba18b742a5f 
– Les lignes 817 et 818 nécessitent les modifications suivantes : 
  – Le nom des couches doit être le nom des couches de votre projet. La couche est la couche vectorielle de la jonction, la couche2 est la couche vectorielle de la ligne des voies
– Les lignes 850 et 853 requièrent les modifications suivantes : 
  – 'VOIE_O_IDN' sur la ligne 850 doit être modifiée par le nom de la colonne de l’ID de votre jonction des voies, et « IDN » sur la ligne 853 doit être modifiée par le nom de la colonne du segment de la voie. 

Le système fonctionne comme suit : 

– Les lignes des voies reçoivent un temps en fonction des longueurs, de la vitesse sur la voie, et des trains qui s’y trouvent. 

  – Les trains qui s’y trouvent reçoivent des temps en fonction du nombre de wagons et de la taille des wagons qui y sont attachés. 

    – Les wagons reçoivent des temps en fonction de leur taille.

– Lorsqu’on interroge le code trackline.getTime(), celui-ci obtient le temps apporté par les voies, et le temps apporté par chaque train, 
  et les trains reçoivent le temps qu’apporte chaque wagon, puis chacun d’entre eux tombent en cascade sur l’un l’autre. 

– les lignes 832 à 845 sont commentées. Toutefois, elle représente de façon plus précise le chemin que les lignes 846 à 855. Elles sont commentées en raison des jonctions superposées qui cachent les couches sélectionnées. Aux fins de consultation d’une carte, les jonctions multidirectionnelles aux mêmes endroits ont toutes été mises en surbrillance.

– les lignes 778 à 802 remplissent aléatoirement les lignes pour faire l’essai et vérifier la façon dont l’ajout de tains et de wagons sur les lignes influence les données de sortie. Tout a fonctionné comme voulu. Toutefois, dans pyqgis, en raison de la puissance moindre du module pyqgis comparativement à une console python normale, qgis a planté. Lorsque l’algorithme a été exécuté dans une console externe, il a fonctionné comme voulu et le processus de sortie s’est effectué en moins de 20 secondes. 

---

# Dans la présente validation de principe, les variables suivantes ont été prises en considération; 

– Types de chemin de fer
– Nombre de lignes pour chaque voie
– Distance entre les intersections
– Vitesse sur le type de voie ferrée
– Capacité de la voie ferrée (suppose une relation entre le trafic et la vitesse)
– Types de trains (voyageurs ou marchandise)
– Poids des trains (on ne l’utilise pas, mais des exigences de base sont mises en œuvre)
– Nombre de wagons attachés au train
– Nombre de fois que les wagons sont chargés et déchargés (suppose une relation de temps par rapport à la taille)
– Taille du wagon
– Si les wagons sont pleins ou non 

---

# Tes éléments suivants n’ont pas encore été mis en œuvre

– Sous-classes de trains (accélération, comment ils réagissent aux courbes, longueur, s’ils peuvent traverser certaines lignes, et ainsi de suite)
– Chargement ou déchargement partiel, on suppose le chargement et le déchargement en entier chaque fois
– Densité du train aux stations, à l’heure actuelle, alors qu’on suppose que le chargement et le déchargement n’influencent aucun train en mouvement
– Les conditions météorologiques ont été entièrement ignorées 
– Période de l’année

---

# Prochaines étapes

– Pour obtenir un modèle comportant des informations qui se rapportent plus à la vraie vie, exécutez le modèle au moyen d’un algorithme d’apprentissage automatique, possiblement un réseau neuronal avec des données de temps fournies par l’équivalent de quelques années d’informations. Les ensembles de données dans l’algorithme d’apprentissage automatique du réseau neuronal seraient les suivants: 

  – La période de la journée
  – La période de l’année
  – Le temps qu’il faut pour voyager entre les lignes
  – Le nombre de trains
  – Le nombre de wagons que comptent les trains
  – Le nombre d’arrêts qu’un train fait

– Ainsi que toute autre information importante

– Puis, au moyen du réseau neuronal, il est possible de modifier les méthodes getTime grâce à l’algorithme d’apprentissage automatique. Cette modification permet un modèle d’autoamélioration qui serait assez facile à mettre en œuvre au moyen de données assez faciles à obtenir grâce aux systèmes de géolocalisation installés sur chaque train. 

– Pour aller encore plus loin, des renseignements en temps réels peuvent être intégrés dans l’algorithme d’apprentissage automatique pour optimiser le système davantage, bien qu’il faudrait un investissement plus important pour obtenir de meilleurs renseignements.

– Il convient de noter que la mise en œuvre de l’algorithme du chemin le plus court ne requiert pas de modifications pour optimiser l’algorithme. Il exigerait plutôt des modifications aux méthodes getTime, qui, encore une fois, ce qui est possible en entrant des relations plus exactes, ou un algorithme d’apprentissage automatique. 
