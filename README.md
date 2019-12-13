# WiFi_Positioning_System
This is a proto WPS (Wi-Fi positioning system). It uses principles of bilateration and simple netowork programming to estimate the position of a client.

# How does it work?
In a nutshell, the 2 servers (Server1 and Server2) have known coordenates and the distance between the two server is known.
Based on this, the 2 servers communicate to try to estimate an "average speed" for the communication, taking into account several things about the network such as hops and lag.
With this information, both servers perform a bilateration to try to find the location of the client.
See more information below.

When I built this, the 3 Python scripts (Server1.py, Server2.py, and Client_to_Locate.py) were running in different machines.
Server1.py was running in a Compute Market VPS hosted in Sioux City, IA, USA.
Server2.py was running in a Google Cloud VM hosted in Tokyo, Japan.
Client_to_Locate.py was running in another server hosted in Sioux City, IA, USA - this is the script to run in the client that one is trying to locate.

The explanation of each directory goes as follows:

# Server1
This is the "main" server if you may. Run this script first. 
1) When started, the server will run a traceoroute processes (trace_Server2.sh) to count the router hops to your specified target server.
2) It will then connect to Server2 and average the time difference in 500 communications. It does this by sending a message with the time the message was sent, and comparing it to the time when the message was received by the other server.
3) It then runs calculations to determine the average speed of the connection.
4) It initializes a new socket to wait for the client connection.

# Server2
Pretty similar to Server1. Run after the Traceroute process of Server1 is completed.
It will then perform the same steps outlined above for Server1.

# Client
This is the client one is trying to estimate the coordenates of. Run when Server1 and Server2 are up and listening for a new connection.
1) When started, the client will fork the process and each process will connect to each server.
2) Each process will perform a traceroute subprocess with each server, and wait until the servers perform a traceroute back at them.
3) Each process will communicate with their respective target server over 100 times and get an average in the time difference of the communication.
4) Each process will send the result to the respective server which will determine an estimated distance for the client.
5) Finally the client should transform the distances and coordenates received by the servers into coordenates estimating its own location (this function is not built yet).



# REMEMBER TO UPDATE AND PUT IN THE INFORMATION OF YOUR OWN MACHINES!
1) Update IP adresses and Ports
2) Update the Coordenates of the 2 known machines 
3) Update the hard coded distance between the 2 known machines

-------------------------------------------------------------------------------------------------------------------------------
Feel free to use my code for whatever you want. If you have any questions just hit me up here or DM on twitter @SamuelPadillaC
