# WiFi_Positioning_System
This is a proto WPS (Wi-Fi positioning system). It uses principles of bilateration and simple netowork programming to estimate the position of a client.

The 3 Python scripts (Server1.py, Server2.py, and Client_to_Locate.py) were all running in different machines.
Server1.py was running in a VPS hosted in Sioux City, IA, USA.
Server2.py was running in a Google Cloud VM hosted in Tokyo, Japan.
Client_to_Locate.py was running in another server hosted in Sioux City, IA, USA - this is the script to run in the client that one is trying to locate.

The explanation of each file goes as follows:

# Server1.py
This is the "main" server if you may.
Run this script first. It will run a traceoroute processes to count the router hops to a target server.
In this case, it was running the 
