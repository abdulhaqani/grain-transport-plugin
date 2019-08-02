# GrainTransportPyQGISScript
On the qgis python console, running this will provide the shortest path from 2 points on a train network.

# This system requires the following considerations to run smoothly.

- The model requires the following packages installed
  - dbfread	
  - numpy	
  - pandas	
  - pip	

- Lines 80-83 require edits for your project to operate. The edits are as follows;
  - The column names for each DF need to be changed to the names on your associated project. For example, if your length column on the .dbf file had a name "Length" instead of "LENGTHKM", just change the column name to yours. (Right side after self.df.*)
  
- For inputs, the inputs are in the following formats;
  - FILENAME is input as: filename.dbf
  - FromTrackId and ToTrackId are based on the rail lines, rail lines are separated by junctions in qgis. Obtain the start and end line from the attribute table and input their unique IDs. 
  - The inputs are all to be separated by commas with no spaces.
    - An example input is as follows:
      - C:\Users\NAME\QGISDatasets\Railway\JJunctTrack50BFinal.dbf,3d5fa20bbe56420a8298d44f9855d54b,f847646e1860467e957e3ba18b742a5f
- Lines 813, and 814 require the following edit;
  - The names of the layers need to be set to the name of your project layers. layer is the junction vector layer, layer2 is the track line vector layer

The System works as follows;
- The track lines are given a time based on the lengths, line speed, and based on the trains that populate it.
  - The trains that populate it are given times based on the number of cars and size of cars on it.
    - The cars are given times based on their size.
    
- When trackline.getTime() is called, it obtains the time contributed by the tracks, and the time contributed by each train, 
and the trains get the time contributed by each car, then all of them are cascaded onto eachother. 

- lines 828 to 841 are commented out, however, they have the more accurate representation of the path than lines 842 to 851. The reason why they were commented out is because of the overlapping junctions hiding selected layers. For the purpose of viewing a map, multidirectional junctions at the same location were all highlighted.

- lines 775 to 799 randomly populated the lines for the purpose of testing and viewing how the addition of trains and cars to the lines impacted the outputs. It worked fully as intended, however, on pyqgis due to the lower power of the pyqgis module when compared to a regular python console, it cause qgis to crash. When the algorithm was ran on an external console it ran exactly as intended and took less than 20 seconds to complete the path output. 

********************************

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

********************************

# The following have not been implemented as of yet
- Train subclasses (acceleration, how they handle turns, length, whether they can traverse specific lines etc)
- Car partial loading/unloading, assumed 100% loading/unloading each time
- Train density at stations, as of now while loading/unloading assumed to not influence any moving trains
- Weather has completely been disregarded
- Time of year

********************************

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
