# -*- coding: utf-8 -*-
"""
 ==========================================================================
 $Id: qgisModule.py,v 1.1 2019 AHaqani Exp $
 Grain Transport
 ==========================================================================
 (C)opyright:

   Abdul Haqani
   Department of Agriculture, Statistics Canada
   170 Jean Talon st.
   Ottawa, On., K1A 0T6
   Canada.

 Creator: Abdul Haqani
 Email:   abdul.haqani@canada.ca
 Phone Number: 343-549-8559
 ==========================================================================
"""
# IMPORTS
import os
import random
from abc import ABCMeta, abstractmethod
from enum import Enum

from collections import defaultdict
from dbfread import DBF
import csv
from qgis.core import QgsProject
import pandas as pd
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QInputDialog, QLineEdit, QDialog

# Initialiser les ressources Qt à partir du dossier ressources.py
from .resources import *

from .grainTransport_dialog import grainTransportDialog
import os.path


"""
FONCTIONS ET CLASSES DE L’ASSISTANT
Les deux classes suivantes sont les assistants de l’exportation et de la lecture des données pour obtenir les données de sortie désirées. 
"""


def dbf_to_csv(dbf_table_pth):  # Entrer un fnl, produire un csv, même nom, même chemin d’accès, sauf extension
    csv_fn = dbf_table_pth[:-4] + ".csv"
    exists = os.path.isfile(dbf_table_pth)

    if exists:
        table = DBF(dbf_table_pth)
        with open(csv_fn, 'w', newline='') as f:  # créer un fichier csv, le remplir avec un contenu fnl
            writer = csv.writer(f)
            writer.writerow(table.field_names)
            for record in table:  # write the rows
                writer.writerow(list(record.values()))
        return csv_fn  # renvoyer le nom csv

    else:
        print("File does not exist")
        return False


class Data:
    # créer un objet qui contient toutes les données (nous retirerons toutes les subdivisions plus tard; on les a tout simplement mises par souci de commodité)
    def __init__(self, file):
        # exécuter la méthode pour convertir fnl en csv
        exists = os.path.isfile(file)

        if not exists:
            self.csvFile = False
            print("File path does not exist")
            return

        self.csvFile = dbf_to_csv(file)

        self.df = pd.read_csv(self.csvFile)
        self.fromTrackNIDDf = self.df.FTRACKNID
        self.toTrackNIDDf = self.df.TOTRACKNID
        self.speed = self.df.SPEEDFREIT
        self.lengthDf = self.df.TOLENGTHKM


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

"""
CLASSES DE TRAIN
Les classes suivantes incluent une classe abstraite pour les objets de train et une implémentation
d'une classe de train
"""


class TrainAbstract(object):
    __metaClass__ = ABCMeta

    def __init__(self, carType):
        self.type = carType  # enum pour vérifier s’il s’agit d’un train de voyageur ou de marchandise
        self.trainWeight = 10  # on suppose que le train pèse 10 tonnes
        super().__init__()
        self.time = 0
        self.loadTime = 0  # on ne l’utilise pas pour l’essai, elle est présente au cas où le chargement et le déchargement seraient fondamentalement différents
        self.removeTime = 0  # on ne l’utilise pas pour l’essai pour la même raison que le temps de chargement
        self.cars = []  # liste vide pour contenir les wagons

    # Modificateurs
	# on utilise actuellement le poids (tonnes)
    @abstractmethod
    def loadTrain(self): pass

    @abstractmethod
    def unloadTrain(self): pass

    @abstractmethod
    def addCar(self, car): pass

    @abstractmethod
    def removeCar(self, car): pass

    # getters
    @abstractmethod
    def getNumCars(self): pass

    @abstractmethod
    def getWeight(self): pass

    @abstractmethod
    def getStopTime(self): pass


class Train(TrainAbstract):

    def __init__(self, maxCars):
        super().__init__(self)
        self.maxCars = maxCars
        self.numCars = 0

    def loadTrain(self):
        i = 0
        print(self.cars.__len__())
        while i < self.cars.__len__():
            if self.cars[i].empty:
                self.cars[i].loadCar(1)
            i += 1
            if i == self.cars.__len__():
                print("Every car is full \n")

    def unloadTrain(self):
        i = 0
        while i < self.cars.__len__():
            if not self.cars[i].empty:
                self.cars[i].unLoadCar(1)
            i += 1
            if i == self.cars.__len__():
                print("Every car is empty \n")

    def addCar(self, car):
        if self.numCars < self.maxCars:
            self.cars.append(car)
            self.numCars += 1
        else:
            print("TRAIN IS AT MAX CAPACITY")

    def removeCar(self, car):
        if self.numCars > 0:
            self.cars.pop(self.numCars - 1)
            self.numCars -= 1

        else:
            print("TRAIN IS EMPTY")

    def getNumCars(self):
        return self.numCars

    def getWeight(self):
        weight = self.trainWeight
        i = 0
        while i < self.cars.__len__():
            weight += self.cars[i].GetWeight()
        return weight

    def getStopTime(self):
        time = 0
        i = 0
        while i < self.cars.__len__():
            time += self.cars[i].getStopTime()
            i += 1
        return time


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

"""
CLASSES DE VOIES
Voici la classe abstraite et une mise en œuvre pour un type de voie. 
Veuillez noter que puisqu’aucune donnée n’a été fournie pendant cette mise en œuvre,  
la relation relative à la vitesse a entièrement été supposée. Il est possible d’obtenir une relation plus exacte  
si un ensemble de données est fourni, et qu’un réseau neuronal est créé à partir de l’ensemble. 
"""


# la classe abstraite suivante concerne la classe TrainEdge
class TrackAbstract(object):
    __metaClass__ = ABCMeta

    def __init__(self, length, numLines, speed):
        self.length = length
        self.numLines = numLines

        self.currentTrains = SLinkedList()
        self.speed = speed

        super().__init__()

    @abstractmethod
    def addTrain(self, train): pass

    @abstractmethod
    def removeTrain(self, train): pass

    @abstractmethod
    def addNode(self, node): pass

    @abstractmethod
    def setTime(self): pass

    @abstractmethod
    def getStations(self): pass

    @abstractmethod
    def getHowFull(self): pass

    @abstractmethod
    def getLength(self): pass

    @abstractmethod
    def getStart(self): pass

    @abstractmethod
    def getEnd(self): pass

    @abstractmethod
    def getLineType(self): pass

    @abstractmethod
    def getTime(self): pass


# ce qui suit est la classe qui contient les détails de chaque voie ferrée

class TrackEdge(TrackAbstract):

    def __init__(self, speed, length, numLines):
        super().__init__(speed, length, numLines)
        # pour l’instant, nous utilisons la longueur, qui est le nombre d’unités de longueur requis pour accroître la capacité de 1
        # par exemple, si 5 km est l’unité requise pour accroître la capacité de 1, une voie d’une longueur de 100 km a une capacité de 20
        self.capacity = length * numLines  # constant
        self.numTrains = 0

        # actuellement, on présume que tous les trains sont espacés de façon égale
        self.howFull = self.numTrains / self.capacity

        """RELATION SUPOSEÉ POUR LA VITESSE"""
        self.speed = self.speed * (1 / (1 + (self.numTrains / self.capacity)))
        # pour les besoins du présent projet, on présume que le temps qu’il faut pour voyager = (longueur*(capacité/1+nombreTrains))/vitesseMaximale où 
        # le temps sera le poids pour la mise en œuvre de l’algorithme de chemin d’accès le plus court
        self.time = 0

    # ajouter un train sur la ligne
    def addTrain(self, train):
        self.currentTrains.addAtBegining(train)
        self.numTrains += 1
        self.howFull = self.numTrains / self.capacity
        self.setSpeed()

    # retirer un train
    def removeTrain(self, train):
        self.currentTrains.removeLastElement(train)
        self.numTrains -= 1
        self.howFull = self.numTrains / self.capacity
        self.setTime()
        print("removed train from track")

    # actualiser et établir le temps
    def setSpeed(self):
        # on suppose que chaque train le ralentit par un facteur de (capacité/91+nombre de trains)
        if self.numTrains <= self.capacity:
            self.speed = self.speed * (1 / (1 + (self.numTrains / self.capacity)))

        # on suppose que si le nombre de trains dépasse la capacité, le temps est deux fois plus lent
        else:
            self.speed = self.speed * (0.5 / (1 + (self.numTrains / self.capacity)))

    def getHowFull(self):
        self.howFull = self.numTrains / self.capacity

        return self.howFull

    def getLength(self):

        return self.length

    def getlineType(self):

        return self.trackTypeEnum

    def getTime(self):

        return self.length / self.speed


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

"""
CLASSES DE WAGONS
Voici 3 classes; l’une est une classe abstraite pour les classes Wagon, les deux autres 
sont des mises en œuvre pour les classes voyageurs et wagon de marchandise. Une autre qu’on voudra peut-être est  
un wagon marchandisesEtVoyageurs, mais pour les besoins du présent essai, elle 
n’est pas requise. Puisqu’aucune information n’a été donnée sur les incidences des wagons, des agents recenseurs 
ont été utilisés pour classer l’incidence que différents wagons peuvent avoir. 
"""


# on présume actuellement que seuls 2 types de wagons existent
class CarEnumerator(Enum):
    PASSENGERCAR = 1
    PRODUCECAR = 2


# On présume actuellement que seules ces tailles de wagon existent
class CarSizeEnumerator(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    EXTRALARGE = 4


# Classe de wagons principale
class carAbstract(object):
    __metaClass__ = ABCMeta

    def __init__(self, carEnum, carSizeEnum, numLoadStops):
        self.type = carEnum.value
        self.size = carSizeEnum.value
        self.numLoadStops = numLoadStops
        super().__init__()

    @abstractmethod
    def loadCar(self, value): pass

    @abstractmethod
    def unLoadCar(self, value): pass

    @abstractmethod
    def getWeight(self): pass

    @abstractmethod
    def getStopTime(self): pass


# Mise en œuvre de la classe de wagon de voyageurs
class PassengerCar(carAbstract):
    def __init__(self, carEnum, carSizeEnum):
        carAbstract.__init__(self, carEnum, carSizeEnum, self.numLoadStops)
        # on suppose qu’un petit wagon pèse 10 tonnes. On ne tient pas compte du poids des voyageurs
        self.weight = carSizeEnum.value * 10
        # on suppose qu’il faut 15 minutes pour monter des voyageurs dans un petit wagon
        self.trainStopTime = carSizeEnum.value * 0.25
        self.totalStopTime = 0
        self.numLoadStops = self.numLoadStops

    # on suppose que chaque temps d’arrêt ne dépend que du nomStations
    # remarque, puisqu’il s’agit d’un wagon de voyageurs, la variation de poids est négligeable
    def loadCar(self):
        self.totalStopTime += self.numLoadStops * self.trainStopTime

    # Temps d’arrêt pour ce wagon en particulier
    def getStopTime(self):
        return self.totalStopTime

    def getWeight(self):
        return self.weight


# Mise en œuvre d’un wagon de marchandises
class ProduceCar(carAbstract):
    def __init__(self, carEnum, carSizeEnum, numLoadStops, numUnLoadStops):
        carAbstract.__init__(self, carEnum, carSizeEnum, numLoadStops)
        # on suppose qu’un petit wagon pèse 10 tonnes (vide)
        self.weight = self.size * 10
        # on suppose qu’il faut 10 minutes pour charger ou décharger un wagon de 10 tonnes
        # on suppose aussi que la capacité d’un petit wagon = 10 tonnes, moyen wagon = 20 tonnes, grand wagon = 30 tonnes, très grand wagon = 40 tonnes
        self.trainStopTime = self.size * 0.5  # const
        # on suppose qu’il n’y a qu’un chargement et qu’un déchargement par wagon
        self.numLoadStops = numLoadStops
        self.numUnLoadStops = numUnLoadStops
        self.totalStopTime = 0
        self.empty = True

    # on suppose que chaque temps d’arrêt ne dépend que du nomStations
    # on suppose qu’actuellement, le chargement et le déchargement d’un wagon prennent le même temps
    # enfin, on suppose qu’actuellement, les wagons peuvent être soit pleins ou vides

    # si vide, charger
    def loadCar(self, numStations):
        if self.empty:
            self.totalStopTime += numStations * self.trainStopTime
            self.weight += self.size * 20  # on suppose que le chargement du wagon pèse deux fois plus que le wagon lui-même
            self.empty = False
        else:
            return

    # si plein, décharger
    def unLoadCar(self, numStations):
        if not self.empty:
            self.totalStopTime += numStations * self.trainStopTime
            self.weight -= self.size * 20  # on suppose que le chargement du wagon pèse deux fois plus que le wagon lui-même
            self.empty = True
        else:
            return

    def getStopTime(self):
        return self.totalStopTime

    def getWeight(self):
        return self.weight


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

"""
STRUCTURES DES DONNÉES ET ALGORITHME DU CHEMIN D’ACCÈS LE PLUS COURT
Les deux classes suivantes sont les structures de données utilisées pour cartographier les données
Le graphique et le nœud créent la carte
La fonction 'weightedShortestPath(railGraph, initial, end)'  est mise en œuvre 
pour l’algorithme du chemin d’accès le plus court. Elle tient compte de nombreuses variables différentes
qui sont paramétrées dans les classes associées au conteneur. Les classes train, wagon et voies 
sont mises en œuvre pour les poids (temps). Cet algorithme  
appelle simplement les méthodes de ces classes pour obtenir les poids. Toute modification de la façon
dont les variables influencent le temps doit être apportée aux méthodes 'getTime()' de ces classes.
"""


# graphique pour le système ferroviaire
class Graph():
    def __init__(self):
        """
    self.edges est un dict de tous les prochains nœuds possibles.
    p. ex. {'X': ['A', 'B', 'C', 'E'], ...}
    self.weights comprend tous les poids entre deux nœuds, 
    où les deux nœuds comme tuple sont la clé. 
    p. ex. {('X', 'A'): 7, ('X', 'B'): 2, ...}
    """
        self.edges = defaultdict(list)
        self.trackEdges = {}

    # Cet élément construit le squelette de la carte; aucun train ni wagon n’est ajouté
    def add_edge(self, from_node, to_node, trackEdge):
        # Remarque : on suppose que les bordures sont bidirectionnelles.
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        # Utiliser trackEdge pour permettre le déplacement des poids du graphique par l’entremise de la classe TrackEdge

        self.trackEdges[(from_node, to_node)] = trackEdge
        self.trackEdges[(to_node, from_node)] = trackEdge


# classe nœud pour les intersections de train (et possiblement la collecte)
class Node:
    def __init__(self, dataval):
        self.dataval = dataval
        self.nextval = None

    def getVal(self):
        return self.dataval


# Liste liée de façon simple
class SLinkedList:
    def __init__(self):
        self.head = Node(None)

    # Reproduire la liste liée
    def printLList(self):
        printval = self.head.dataval
        while printval is not None:
            print(printval.dataval)
            printval = printval.next

    # Ajouter un nouveau nœud au début
    def addAtBegining(self, newdata):
        NewNode = Node(newdata)

        # Actualiser la prochaine valeur des nouveaux nœuds au nœud existant
        NewNode.next = self.head
        self.head = NewNode

    # Ajouter un nouveau nœud à la fin
    def addAtEnd(self, newdata):
        NewNode = Node(newdata)
        if self.head is None:
            self.head = NewNode
            return
        last = self.head
        while (last.next):
            last = last.next
        last.next = NewNode

    # Ajouter un nœud entre des nœuds (remarque : ne sera probablement pas requis)
    def addInbetween(self, middle_node, newdata):
        if middle_node is None:
            print("The mentioned node is absent")
            return

        NewNode = Node(newdata)
        NewNode.next = middle_node.next
        middle_node.next = NewNode

    # Supprimer le premier élément
    def removeFirstElement(self):
        if self.head is None:
            return
        self.head = self.head.next

    # Supprimer le dernier élément
    def removeLastElement(self):
        if self.head is None:
            return
        temp = self.head
        while temp.next is not None:
            temp = temp.next
        temp.next = None

    # Supprimer un nœud à un endroit clé
    def removeNode(self, Removekey):
        temp = self.head
        if temp is not None:
            if temp.data == Removekey:
                self.head = temp.next
                temp = None
                return

        while temp is not None:
            if temp.data == Removekey:
                break
            prev = temp
            temp = temp.next

        if temp is None:
            return

        prev.next = temp.next

        temp = None


# algorithme du chemin d’accès le plus court

def weightedShortestPath(railGraph, initial, end):
    # les chemins d’accès les plus courts sont un dict de nœuds
    # dont la valeur est un tuple de (nœud, poids précédent)
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()
    if railGraph.edges[initial] is None:
        print("initial node does not exist")
        return
    elif railGraph.edges[end] is None:
        print("end node does not exist")
        return
    while current_node != end:
        visited.add(current_node)
        destinations = railGraph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node in destinations:
            temp = railGraph.trackEdges[(current_node, next_node)]
            weight = temp.getTime() + weight_to_current_node
            # si nous ne l’avons pas déjà examiné
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                # établir la valeur actuelle et vérifier si elle est plus courte que l’ancien chemin d’accès le plus court
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    # établir le prochain nœud à côté du nœud actuel
                    shortest_paths[next_node] = (current_node, weight)

        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return "Route Not Possible"
        # le prochain nœud est la destination dont le poids est le plus faible
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # Revenir aux destinations par le chemin le plus court
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    # Chemin inverse
    path = path[::-1]
    i = 0
    weight = 0
    while i < (path.__len__() - 1):
        temp = railGraph.trackEdges[(path[i], path[i + 1])]
        # temp indique une limite de voie, temp.getTime renvoie le temps pour chaque arrêt
        # getTemp tient compte de chaque train, et de chaque wagon de chaque train
        weight += temp.getTime()
        i += 1
    message = QInputDialog()
    input, ok = QInputDialog.getText(message, "Time", "Total stop time for the trip is: " + weight.__str__() + " hours \n",
                                QLineEdit.Normal,
                                '')
    print("Total time for the trip is: " + weight.__str__() + " hours \nThe path to be taken is: ")
    print(path)
    return [path, weight]

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

class grainTransport:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'grainTransport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&grain Transport')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('grainTransport', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.action = QAction(
            QIcon(self.plugin_dir + '/icon.png'),
            'Grain Transport', self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)
        
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('&Grain Transport', self.action)
        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&grainTransport Shortest Path'),
                action)
            self.iface.removeToolBarIcon(action)

    def pathTest(self):
        qid = QInputDialog()

        “””tout exécuter”””
        railGraph = Graph()
        input, ok = QInputDialog.getText(qid, "Entrer les entrées", "Entrer les entrées comme 'nomDeFichier,début,fin'",
                                         QLineEdit.Normal,
                                         "FILEPATH" + "," + "FromTrackID" + "," + "ToTrackId")
        x = ""
        y = ""
        z = ""
        if ok:
            x = input.split(",")[0]
            if x == "FILEPATH":
                print("Enter valid inputs")
                return
            print(x)
            try:
                y = input.split(",")[1]
                if y == "FromTrackID":
                    print("Enter valid inputs")
                    return
                print(y)
            except:
                print("Input start junction after comma")
            try:
                z = input.split(",")[2]
                if z == "ToTrackID":
                    print("Enter valid inputs")
                    return
                print(z)
            except:
                print("Input end junction after comma")
            if not x:
                print("Ooops! FileName value is missing!")
                return
            if not y:
                print("Ooops! From Junction value is missing!")
                return
            if not z:
                print("Ooops! To Junction value is missing!")
                return
            file = x
            start = y
            end = z
        else:
            print("Cancelled")
            return

        data = Data(file)
        if data.csvFile is False:
            return
        edges = defaultdict(list)
        # créer le graphique
        for i in range(len(data.df)):
            rand = random.randint(0, 5)
            trackEdge = TrackEdge(float(data.lengthDf.iloc[i]), float(data.speed.iloc[i]), 1)
            railGraph.add_edge(data.fromTrackNIDDf.iloc[i], data.toTrackNIDDf.iloc[i], trackEdge)

        # Le code de commentaire suivant a été utilisé pour essayer la façon dont l’ajout de wagons 
        # et de trains influence le temps, et le code a fonctionné comme voulu. Il a rempli les lignes des wagons 
        # de façon aléatoire. Ce code fonctionne lorsqu’on exécute le programme dans une console python externe.
        # Toutefois, lorsqu’on l’exécute dans une console python qgis, qgis 
        # fige parce que le nombre de calculs est trop élevé pour cette console python trop faible 
        # Afin d’exécuter le code commenté ci-dessous, il faut un ordinateur ou 
        # un réseau d’ordinateurs puissant. 

        #        for j in range(rand):                                           # for each train on the line
        #            randMaxCar = random.randint(0,10)
        #            randCar = random.randint(0, randMaxCar)
        #            train = Train(randMaxCar)                            # create a train with a max number of
        #            cars
        #            for k in range(randCar):                                    # for each car on the train
        #                #carEnum = random.randint(1,2)
        #                carEnum = CarEnumerator.PRODUCECAR
        #                carSize = random.randint(1, 4)
        #                if carSize == 1:
        #                    carSizeEnum = CarSizeEnumerator.SMALL
        #                elif carSize == 2:
        #                    carSizeEnum = CarSizeEnumerator.MEDIUM
        #                elif carSize == 3:
        #                    carSizeEnum = CarSizeEnumerator.LARGE
        #                else:
        #                    carSizeEnum = CarSizeEnumerator.EXTRALARGE
        #                car = ProduceCar(carEnum, carSizeEnum, 1, 1)        # create the car, assume 1 load and
        #                1 unload
        #                car.loadCar(car.numLoadStops)
        #                car.unLoadCar(car.numUnLoadStops)
        #
        #                train.addCar(car)                                       # add to the train
        #            train.loadTrain()
        #            trackEdge.addTrain(train)                                   # add the train to the tracks

        # ajouter la ligne sur laquelle se trouvent les trains et leurs wagons sur le graphique 

        # Il faut filtrer les nœuds du graphique
        a = weightedShortestPath(railGraph, start, end)
        path = a[0]
        time = a[1]
        if trackEdge.currentTrains.head.dataval is not None:
            stopTime = trackEdge.currentTrains.head.dataval.getStopTime()
            print("Total stop time for the trip is: " + stopTime.__str__() + " hours \n")
            
        return path

    def test(self):
        layer = QgsProject.instance().mapLayersByName('TrackJunctions')[0]
        layer2 = QgsProject.instance().mapLayersByName('TrackLines')[0]
        path = self.pathTest()
        if not path:
            print("NO PATH POSSIBLE")
            return
        x = []
        y = []
        # Le code de commande suivant concerne les directions des jonctions avec les 
        # mêmes ID. Toutefois, sur la carte dotée de ce code, bon nombre des nœuds sélectionnés sont 
        # cachés par des nœuds superposés. Par conséquent, même si c’est plus juste aux 
        # fins de la visualisation au moyen de QGIS, le bloc de code a été remplacé par un bloc qui 
        # sélectionne les jonctions superposées qui tiennent compte des différentes directions.
        # Les lignes en surbrillance n’ont aucun effet. Toutefois, ce ne sont que les nœuds

        #    for i in range(len(path) - 1):
        #        j = path[i]
        #        k = path[i+1]
        #        layer.selectByExpression('\"FTrackNID\" IS\'%s\' AND\"TOTrackNID\" IS\'%s\'' %(j, k))
        #        for l in layer.selectedFeatureIds():
        #            x.append(l)
        #    layer.selectByExpression('\"FTrackNID\" IS\'%s\'' %(path[len(path)-1]))
        #    for l in layer.selectedFeatureIds():
        #        x.append(l)
        #    for i in range(len(path)):
        #        j = path[i]
        #        layer2.selectByExpression('\"NID\" IS\'%s\'' %j)
        #        for l in layer2.selectedFeatureIds():
        #            y.append(l)
        if not path:
            return
        for i in range(len(path)):
            j = path[i]
            layer.selectByExpression('\"FTrackNID\" IS\'%s\'' % j)
            for l in layer.selectedFeatureIds():
                x.append(l)
            layer2.selectByExpression('\"NID\" IS\'%s\'' % j)
            for l in layer2.selectedFeatureIds():
                y.append(l)

        layer.select(x)
        layer2.select(y)
        self.iface.actionZoomToSelected().trigger()

    def run(self):
        # exécuter la méthode qui réalise tout le réel travail
        # créer le dialogue avec des éléments (après la traduction) et conserver les références
        # Ne créer le GUI qu’une fois en rappel afin qu’il ne charge que lorsque le module est lancé. 
        if self.first_start:
            self.first_start = False
        dlg = grainTransportDialog()
        # montrer le dialogue
        dlg.show()
        # Exécuter la boucle de l’événement du dialogue
        result = dlg.exec_()
        # Vérifier si on a appuyé sur OK
        if result:
            self.test()
            



