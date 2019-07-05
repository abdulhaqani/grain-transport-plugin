# -*- coding: utf-8 -*-
"""
 ==========================================================================
 $Id: qgisModule.py,v 1.1 2019/07/05 AHaqani Exp $
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
#IMPORTS
import os
import random
from abc import ABCMeta, abstractmethod
from enum import Enum
import numpy as np
from collections import defaultdict
from dbfread import DBF
import csv
import sys
import pandas as pd
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QInputDialog, QLineEdit

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .grainTransport_dialog import grainTransportDialog
import os.path

"""
HELPER FUNCTIONS AND CLASSES
The following 2 classes are helpers to export and read the data to obtain the desired output
"""


def dbf_to_csv(dbf_table_pth):  # Input a dbf, output a csv, same name, same path, except extension
    csv_fn = dbf_table_pth[:-4] + ".csv"  # Set the csv file name
    exists = os.path.isfile(dbf_table_pth)

    if exists:
        table = DBF(dbf_table_pth)  # table variable is a DBF object
        with open(csv_fn, 'w', newline='') as f:  # create a csv file, fill it with dbf content
            writer = csv.writer(f)
            writer.writerow(table.field_names)  # write the column name
            for record in table:  # write the rows
                writer.writerow(list(record.values()))
        return csv_fn  # return the csv name

    else:
        print("File does not exist")
        return False


class Data:
    # create an object which has all the data (going to remove all the subdivisions later, just put them for ease)
    def __init__(self, file):
        # run method to convert dbf to csv
        exists = os.path.isfile(file)
        if not exists:
            self.csvFile = False
            print("File path does not exist")
            return
        self.csvFile = dbf_to_csv(file)
        # read in the dbf
        # convert it to a df

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
TRAIN CLASSES
The following classes include an abstract class for train objects, and an implementation
of a train class
"""


class TrainAbstract(object):
    __metaClass__ = ABCMeta

    def __init__(self, carType):
        self.type = carType  # enum to see whether this is a passenger or freight train
        self.trainWeight = 10  # assume train weighs 10 tonnes
        super().__init__()
        self.time = 0
        self.loadTime = 0  # not using for testing, this is here in case loading/removing are inherently different
        self.removeTime = 0  # not using for testing, same reason as loadtime
        self.cars = []  # empty list to hold the cars

    # Modifiers
    # currently using weight (tons)
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
        self.maxCars = maxCars  # maximum number of cars on the train
        self.numCars = 0

    def loadTrain(self):
        i = 0
        print(self.cars.__len__())
        while i < self.cars.__len__():  # check each car
            if self.cars[i].empty == True:  # if the car is empty
                self.cars[i].loadCar(1)  # load the car
            i += 1
            if i == self.cars.__len__():  # every car has been checked to try to add weight
                print("Every car is full \n")

    def unloadTrain(self):
        i = 0
        while (i < self.cars.__len__()):  # check each car
            if (self.cars[i].empty != True):  # if the car is not empty
                self.cars[i].unLoadCar(1)  # unload the car
            i += 1
            if (i == self.cars.__len__()):  # every car has been checked to try to add weight
                print("Every car is empty \n")

    def addCar(self, car):
        if (self.numCars < self.maxCars):
            self.cars.append(car)
            self.numCars += 1
        else:
            print("TRAIN IS AT MAX CAPACITY")

    def removeCar(self, car):
        if (self.numCars > 0):
            self.cars.pop(self.numCars - 1)  # assume car attachment/removal works like a stack
            self.numCars -= 1
        else:
            print("TRAIN IS EMPTY")

    # getters
    def getNumCars(self):
        return self.numCars

    def getWeight(self):
        weight = self.trainWeight
        i = 0
        while (i < self.cars.__len__()):
            weight += self.cars[i].GetWeight()
        return weight

    def getStopTime(self):
        time = 0
        i = 0
        while (i < self.cars.__len__()):
            time += self.cars[i].getStopTime()
            i += 1
        return time


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

"""
TRACK CLASSES
The following includes the abstract class and an implementation for a track type
Please note that since no data was provided while implementing this, that the 
speed relationship was entirely assumed. A more accurate relationship can be 
obtained if a dataset is provided, and a neural network is trained off of that.
"""


# the following abstract class is for the TrainEdge class
class TrackAbstract(object):
    __metaClass__ = ABCMeta

    def __init__(self, length, numLines, speed):
        self.length = length  # constant
        self.numLines = numLines  # constant
        self.currentTrains = SLinkedList()
        self.speed = speed  # constant
        super().__init__()

    # Modifiers
    @abstractmethod
    def addTrain(self, train): pass

    @abstractmethod
    def removeTrain(self, train): pass

    @abstractmethod
    def addNode(self, node): pass

    # setters
    @abstractmethod
    def setTime(self): pass

    # getters
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


# the following is the class which contains the details for each rail
class TrackEdge(TrackAbstract):

    def __init__(self, speed, length, numLines):
        super().__init__(speed, length, numLines)
        # for now we are using length is the number of length units that required to increase capacity by 1
        # for example, if 5km is the unit required to increase capacity by 1, a track of length 100km has capacity 20
        self.capacity = length * numLines  # constant
        self.numTrains = 0

        # currently it is assumed that all trains are equally spaced
        self.howFull = self.numTrains / self.capacity

        """ASSUMED RELATIONSHIP FOR SPEED"""
        self.speed = self.speed * (1 / (1 + (self.numTrains / self.capacity)))
        # for the purpose of this project, assume the time to travel=(length*(capacity/1+numTrains))/topSpeed where
        # time is going to be the weight for the shortest path algorithm implementation
        self.time = 0

    # add a train on the line
    def addTrain(self, train):
        self.currentTrains.addAtBegining(train)
        self.numTrains += 1
        self.howFull = self.numTrains / self.capacity
        self.setSpeed()

    # remove a train
    def removeTrain(self, train):
        self.currentTrains.removeLastElement(train)
        self.numTrains -= 1
        self.howFull = self.numTrains / self.capacity
        self.setTime()
        print("removed train from track")

    # update and set the time
    def setSpeed(self):
        # assume each train slows it down by a factor of (capacity / (1 + numtrains))
        if self.numTrains <= self.capacity:
            self.speed = self.speed * (1 / (1 + (self.numTrains / self.capacity)))

        # assume that if the number of trains exceeds the capacity then it is twice as slow
        else:
            self.speed = self.speed * (0.5 / (1 + (self.numTrains / self.capacity)))

    # getters
    # def getStations(self):

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
CAR CLASSES
The following is 3 classes, one is an abstract class for Car classes, the other 2
are implementations for passenger and produce car classes. Another one which may 
be desired is a produceAndPassenger car, but for the purposes of this test, it was
not required. Since no information was given on the impact of cars, Enumerators 
were used to classify the impact that different cars can have. 
"""


# currently assuming that only 2 types of Car types exist
class CarEnumerator(Enum):
    PASSENGERCAR = 1
    PRODUCECAR = 2


# Currently assuming only these car sizes exist
class CarSizeEnumerator(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    EXTRALARGE = 4


# Car parent class
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


# Passenger Car class implementation
class PassengerCar(carAbstract):
    def __init__(self, carEnum, carSizeEnum):
        carAbstract.__init__(self, carEnum, carSizeEnum, self.numLoadStops)
        # assume that a small car weighs 10 tonnes, also neglect passenger weight
        self.weight = carSizeEnum.value * 10
        # assume that a small car takes 15 minutes to load passengers
        self.trainStopTime = carSizeEnum.value * 0.25
        self.totalStopTime = 0
        self.numLoadStops = self.numLoadStops

    # assume each stop time depends only on the numStations
    # note, since it's a passenger car, weight change is negligible
    def loadCar(self):
        self.totalStopTime += self.numLoadStops * self.trainStopTime

    # Stop time for this specific car
    def getStopTime(self):
        return self.totalStopTime

    def getWeight(self):
        return self.weight


# Produce Car implementation
class ProduceCar(carAbstract):
    def __init__(self, carEnum, carSizeEnum, numLoadStops, numUnLoadStops):
        carAbstract.__init__(self, carEnum, carSizeEnum, numLoadStops)
        # assume that a small car weighs 10 tons (empty)
        self.weight = self.size * 10
        # assume that a small car takes 10 minutes to load/unload 10 tonne car
        # also assume that small car capacity = 10 tonnes, medium = 20 tonnes, large = 30 tonnes, extra large = 40 tonne
        self.trainStopTime = self.size * 0.5  # const
        # assume only 1 load and 1 unload per car
        self.numLoadStops = numLoadStops
        self.numUnLoadStops = numUnLoadStops
        self.totalStopTime = 0
        self.empty = True

    # assume each stop time depends only on the numStations
    # also currently assume load and unload car takes same amount of time
    # finally, currently assuming cars can either be full or empty

    # if empty then load
    def loadCar(self, numStations):
        if (self.empty == True):
            self.totalStopTime += numStations * self.trainStopTime
            self.weight += self.size * 20  # assume load in car weighs twice the car itself
            self.empty = False
        else:
            return

    # if full then unload
    def unLoadCar(self, numStations):
        if (self.empty == False):
            self.totalStopTime += numStations * self.trainStopTime
            self.weight -= self.size * 20  # assume load in car weighs twice the car itself
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
DATA STRUCTURES AND SHORTEST PATH ALGORITHM
The following 2 classes are the data structures used to map the data
Graph and node create the map
The function 'weightedShortestPath(railGraph, initial, end)' has the implementation 
for the shortest path algorithm. It takes into account many different variables
that are parameterized in the container classes. The train, car, and tracks 
classes have the implementation for the weights (time), this algorithm simply 
calls those class' methods to obtain the weights. Any adjustment for how the 
variables impact the time should be done to those class' 'getTime()' methods
"""


# graph for the rail system
class Graph():
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = defaultdict(list)
        self.trackEdges = {}

    # This constructs the map skeleton, no trains or cars are added
    def add_edge(self, from_node, to_node, trackEdge):
        # Note: assumes edges are bi-directional
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        # Use trackEdge to allow the graph weights to be mutable via TrackEdge class

        self.trackEdges[(from_node, to_node)] = trackEdge
        self.trackEdges[(to_node, from_node)] = trackEdge


# node class for train intersections (and possibly pick ups)
class Node:
    def __init__(self, dataval):
        self.dataval = dataval
        self.nextval = None

    def getVal(self):
        return self.dataval


# Singly linked list
class SLinkedList:
    def __init__(self):
        self.head = Node(None)

    # Print the linked list
    def printLList(self):
        printval = self.head.dataval
        while printval is not None:
            print(printval.dataval)
            printval = printval.next

    # Add newnode at beginning
    def addAtBegining(self, newdata):
        NewNode = Node(newdata)

        # Update the new nodes next val to existing node
        NewNode.next = self.head
        self.head = NewNode

    # Add New node at end
    def addAtEnd(self, newdata):
        NewNode = Node(newdata)
        if self.head is None:
            self.head = NewNode
            return
        last = self.head
        while (last.next):
            last = last.next
        last.next = NewNode

    # Add node in between nodes (note probably won't need)
    def addInbetween(self, middle_node, newdata):
        if middle_node is None:
            print("The mentioned node is absent")
            return

        NewNode = Node(newdata)
        NewNode.next = middle_node.next
        middle_node.next = NewNode

    # Remove First element
    def removeFirstElement(self):
        if (self.head is None):
            return
        self.head = self.head.next

    # Remove Last element
    def removeLastElement(self):
        if (self.head is None):
            return
        temp = self.head
        while (temp.next is not None):
            temp = temp.next
        temp.next = None

    # Remove node at key
    def removeNode(self, Removekey):

        temp = self.head

        if (temp is not None):
            if (temp.data == Removekey):
                self.head = temp.next
                temp = None
                return

        while (temp is not None):
            if temp.data == Removekey:
                break
            prev = temp
            temp = temp.next

        if (temp == None):
            return

        prev.next = temp.next
        temp = None


# shortest path algorithm
def weightedShortestPath(railGraph, initial, end):
    # shortest paths is a dict of nodes
    # whose value is a tuple of (previous node, weight)
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()
    if (railGraph.edges[initial] == None):
        print("initial node does not exist")
        return
    elif (railGraph.edges[end] == None):
        print("end node does not exist")
        return
    while current_node != end:
        visited.add(current_node)
        destinations = railGraph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node in destinations:
            temp = railGraph.trackEdges[(current_node, next_node)]
            weight = temp.getTime() + weight_to_current_node
            # if we havent already visited it
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                # set current and check if it's shorter than the old shortest path
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    # set next node to the current node
                    shortest_paths[next_node] = (current_node, weight)

        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return "Route Not Possible"
        # next node is the destination with the lowest weight
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # Work back through destinations in shortest path
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    # Reverse path
    path = path[::-1]
    i = 0
    weight = 0
    while i < (path.__len__() - 1):
        temp = railGraph.trackEdges[(path[i], path[i + 1])]
        # temp points to a trackedge, temp.getTime returns the time for all stops
        # getTime takes into account each train, and each car on each train
        weight += temp.getTime()
        i += 1
    print("Total time for the trip is: " + weight.__str__() + " hours \nThe path to be taken is: ")
    print(path)
    return ([path, weight])


# ******************************************************************************
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
        self.menu = self.tr(u'&grain Transport Shortest Path')

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


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/grainTransport/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'grainTransport'),
            callback=self.run,
            parent=self.iface.mainWindow())

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

        """running everything """
        railGraph = Graph()
        input, ok = QInputDialog.getText(qid, "Enter inputs", "Enter inputs as 'fileName,start,end'",
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
        if data.csvFile == False:
            return
        edges = defaultdict(list)
        # create the graph
        for i in range(len(data.df)):  # for each line
            rand = random.randint(0, 5)  # generate a random number of trains on the line
            trackEdge = TrackEdge(float(data.lengthDf.iloc[i]), float(data.speed.iloc[i]), 1)
            railGraph.add_edge(data.fromTrackNIDDf.iloc[i], data.toTrackNIDDf.iloc[i], trackEdge)

        #    The following commented code was used for testing how the addition of cars
        #    and trains impact the time, and it worked as intended. it randomly populated
        #    the lines with cars This works when running program in an external python
        #    console, however, when running on qgis python console it causes qgis to
        #    freeze because there are too many calculations for this underpowered python
        #    console. In order to run the commented code below, a stronger computer or
        #    network of computers is required.

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

        # append the line with the trains with the cars onto the graph

        # Need to filter out the graph from/to nodes
        a = weightedShortestPath(railGraph, start, end)
        path = a[0]
        time = a[1]
        if trackEdge.currentTrains.head.dataval is not None:
            stopTime = trackEdge.currentTrains.head.dataval.getStopTime()
            print("Total stop time for the trip is: " + stopTime.__str__() + " hours \n")
        return path

    def test(self):
        layer = QgsProject.instance().mapLayersByName('JJunctTrack50BFinal')[0]
        layer2 = QgsProject.instance().mapLayersByName('MBTrackLines')[0]
        path = self.pathTest()
        if not path:
            print("NO PATH POSSIBLE")
            return
        x = []
        y = []
        # The following commented code is for the directions of the junctions with the
        # same IDs, however on the map with this code many of the selected nodes are
        # hidden by overlapping nodes, therefore, even though it is more correct, for
        # the purposes of viewing on QGIS, The code block was replaced with one that
        # selects the overlapping junctions which accounts for the different directions.
        # The highlighted lines have no effect however, it is only the nodes

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
        layer.zoomToSelected()

    def run(self):
        # Run method that performs all the real work

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if not self.first_start:
            self.first_start = False
            self.dlg = grainTransportDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            self.test()
            



