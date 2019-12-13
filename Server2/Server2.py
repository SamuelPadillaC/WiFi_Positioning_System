import socket
import sys, time
import subprocess
from statistics import mean

# Define Port
port = 50069
latitude = <"YOUR SERVER2 LATITUDE HERE">
longitude = <"YOUR SERVER2 LONGITUDE HERE">

##########################################
#            DRIVER FUNCTION             #
##########################################
def main ():
    # Welcome Print
    print ("[C] Client process started.")
    print ("[C] This machine is a <information about your machine>.")
    print( "[S] Coordenates of host (Lat, Long): x, y")

    # Running traceroute bash script
    print ("\n\n[C] Running bash taceroute subprocess with target <"IP ADDRESS OF SERVER1">")
    subprocess.call("bash ./trace_compute_market.sh", shell=True)
    print ("[C] Bash subprocess completed.")

    # Create socket object - AF_INET is IPv4 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    print("\n\n[C] Socket successfully created.")

    # connecting to the server 
    s.connect((<"IP ADDRESS OF SERVER1">, port)) 
    print("[C] The socket has successfully connected to 196.52.55.112.")

    client_time_diff = []
    i = 0
    print ("\n\n[C] Averaging the time difference of 500 interactions...\nThis might take a few seconds")

    #Average the time difference between 500 messages
    while i < 501:
        #Sending time
        s.send(bytes(str(time.time()), 'utf-8'))

        # Receive message
        sent_time = float(s.recv(1024))

        # Find and append time difference
        client_time_diff.append(time.time() - sent_time)

        i += 1

    # Sending final average #
    s.send(bytes(str(mean(client_time_diff)), 'utf-8'))

    #Print
    print ("[C] Interactions performed")
    print ("\n\n[C] The average time of the total communication from SERVER - CLIENT was: %2.10f s" % mean(client_time_diff))


    # Calculate number of Hops from Google VM to Compute Market # 
    route, reached = Read_Route("route_to_cm.txt")
    client_hops = Calculate_Hops(route, reached)

    # Hops are measured from local machine to target.
    # The time diff is measured from target to local.
    # Each machine performs the calculations for the other one
    # Send hops and receive.
    print ("[C] Exchanging hop information with server.")
    hops = float(s.recv(1024))
    s.send(bytes(str(client_hops), 'utf-8'))

    # Get Client Averages (based on empirical time)
    print ("\n\n[C] Getting local client averages.")
    client_time_per_hop, client_distance_per_hop, client_conn_speed = Averages(hops, mean(client_time_diff))


    # Sending client averages
    print ("[C] Sending client averages to server.")
    s.send(bytes(str(client_time_per_hop), 'utf-8'))
    time.sleep(2) #Wait for 2 seconds and make sure message is sent
    s.send(bytes(str(client_distance_per_hop), 'utf-8'))
    time.sleep(2)
    s.send(bytes(str(client_conn_speed), 'utf-8'))
    print ("[C] Client averages have been sent.")


    # Receiving Final Averages Back
    print ("\n\n[C] Receiving final averages from Server.")
    final_time_avg = float(s.recv(1024))
    final_time_per_hop = float(s.recv(1024))
    final_distance_per_hop = float(s.recv(1024))
    final_conn_speed = float(s.recv(1024))
    print ("[C] Final averages for triangulation received.")


    # Setting up New Server for triangultion #
    print ("\n\n[C] Creating Server to listen for connections...")

    New_Server(final_distance_per_hop, final_conn_speed)

#################################################
#################################################

def Read_Route(Path):
    # Open the traceroute log file #
    file_object = open(Path, 'r')
    vector_lines = (file_object.readlines()) # Reads all the lines into the vector vector_lines
    file_object.close()

    #Ignore header for vector_lines
    vector_lines = vector_lines[1:]

    #Analyze last line to see if traceroute reached the final destination
    last_line = vector_lines[-1].split()

    if last_line[1] != '*': #This means it reached its final destination
        vector_lines = vector_lines[:-1] #Ignore the last line (target machine)
        
        #Return vector_lines and true
        return vector_lines, True

    else: #Traceroute was blocked someway along the path
        block_index = 0
        lines = vector_lines #copy and reverse vector_lines
        lines.reverse()

        #Find index where traceroute was blocked
        for i in lines:
            z = i.split()
            if z [1] != '*':
                #assign the index of the first valid item to block_index
                block_index = lines.index(i)
                break

        # Redefine lines only with the valid items
        lines = lines[block_index:]
        
        # Redefine vector_lines by reversing lines again
        lines.reverse()
        vector_lines = lines

        #Retrun vector_lines and false
        return vector_lines, False

#################################################
#################################################

def Calculate_Hops(route, reached):
    # Initialize
    hops = len(route) #Got number of hops
    time_per_hop = []

    # Find average spent in every router
    # Note that traceroute sends 3 packets, find the time spent in each packet and average it out
    for line in route:
        line = line.split() #split every line by the space
        packets = [] #initialize packets list

        #Loop through every element in line
        for i in line:
            #Find time unit elements
            if i == 'ms':
                packets.append(float(line[line.index(i) - 1])) #append the previous element of i to packet

        #Append the mean time or * if failed
        errors = 0
        if len(packets) != 0:
            time_per_hop.append(mean(packets)/1000) #divide by 1000 to get s
        else:
            errors += 1

    # Print
    if reached == False:
        print ("\n\n[C] The traceroute process was unable to reach the target machine and determine the exact number of router hops.")
        print ("[C] However, there were at least %d recorded router hops before the process was dropped." % hops)
    else:
        print ("\n\n[C] The traceroute process reached the target machine and recorded %d router hops." % hops)
    
    if errors > 0:
        print ("[C] There were %d hops that did not return any time information." % errors)
        print ("[C] Keep in mind that this might afect the final time averages.")
    
    print ("\n\n[C] Based on the data from the TRACEROUTE SUBPROCESS, these are the results:")
    print ("[C] Average TIME per hop: %2.10f s" % mean(time_per_hop))
    print ("[C] TOTAL communication time: %2.10f s" % sum(time_per_hop))


    return hops

#################################################
#################################################

def Averages (num_of_hops, client_time_avg):
    time = client_time_avg / num_of_hops
    #Distance from the 2 coordenates is hard coded
    distance = <"KNOWN DISTANCE BETWEEN SERVER1 AND SERVER2"> / num_of_hops
    speed = <"KNOWN DISTANCE BETWEEN SERVER1 AND SERVER2"> / client_time_avg

    return time, distance, speed

#################################################
#################################################

def New_Server(distance_per_hop, conn_speed):
    #Set new PORT
    NEW_PORT = 50042

    # Creating socket 
    New_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		 
    print ("\n\n-----------------------------------------------------")
    print ("[S] Server Socket Successfully Created.")				

    # Next bind to the port 
    New_Socket.bind(("", NEW_PORT))		 
    print ("[S] Socket binded to new port 50042.") 

    # put the socket into listening mode 
    New_Socket.listen(5)	 
    print ("[S] Server Socket is waiting for connections.")			

    # Establish connection with client. 
    conn, addr = New_Socket.accept()	 
    print ("[S] Got connection from", addr)

    # Inform user and Define Time list #
    client_to_server_time_diff = []
    i = 0
    print ("\n\n[S] Averaging the time difference of 100 communications with client...\nThis might take a few seconds")

    # Communicating
    while i < 101:
        # Receive message
        sent_time = float(conn.recv(1024))

        # Find time difference
        client_to_server_time_diff.append(time.time() - sent_time)

        #Send time
        conn.send(bytes(str(time.time()), 'utf-8'))

        i += 1
    print ("[S] Communications performed.")

    # Running traceroute on addr to get number of hops
    # Create command
    print ("\n\n[S] Running traceroute subprocess on %s." % addr[0])
    print ("[S] Client will be put on hold.")
    traceroute = "traceroute " + addr[0] + " > route_to_conn.txt"
    subprocess.run([traceroute], shell=True)
    print ("[S] Subprocess completed. Notifying client.")
    conn.send(bytes("We're good from GVM.", 'utf-8'))

    # Receive client_to_server_hops
    client_to_server_hops = float(conn.recv(1024))

    # Calculate server_to_client hops and send to client
    print ("\n\n[S] Calculating hops from server to client.")
    route, x = Read_Route("route_to_conn.txt")
    conn.send(bytes(str(len(route)), 'utf-8')) #len(route is number of hops)

    # Calculate time per hop
    print ("\n\n[S] Caculating average time per hop.")
    client_to_server_time_diff = mean (client_to_server_time_diff) #Get the mean of the time diff
    client_to_server_time_per_hop = client_to_server_time_diff / client_to_server_hops
    
    # Receive information from client
    print ("[S] Receiving time, hops, and time per hop from client.")
    server_to_client_time_diff = float(conn.recv(1024)) #time
    server_to_client_hops = float(conn.recv(1024)) #hops
    server_to_client_time_per_hop = float(conn.recv(1024)) #time/hops
    
    # Calculate time averages
    print ("[S] Calculating time averages.")
    time_per_hop, hops, time_diff = Client_Averages(server_to_client_time_per_hop, client_to_server_time_per_hop, server_to_client_hops, client_to_server_hops, server_to_client_time_diff, client_to_server_time_diff)

    # Calculate Distance
    print ("\n\n[S] Calculating distance to client.")
    distance = Find_Distance (conn_speed, time_diff)

    # Send results to client
    print ("\n\n[S] Sending distance and latitude to client.")
    conn.send(bytes(str(distance), 'utf-8')) #distance
    time.sleep(2)
    conn.send(bytes(str(latitude), 'utf-8')) #lat
    time.sleep(2)
    conn.send(bytes(str(longitude), 'utf-8')) #long

    print ("\n\n\n-----------------------------------------------------")
    print ("[S] All information sent to client.")
    print ("[S] Check client for estimated coordinates.")

    return
#################################################
#################################################

def Client_Averages(server_to_client_time_per_hop, client_to_server_time_per_hop, server_to_client_hops, client_to_server_hops, server_to_client_time_diff, client_to_server_time_diff):
    time_per_hop = mean([server_to_client_time_per_hop, client_to_server_time_per_hop])
    hops = mean ([server_to_client_hops, client_to_server_hops])
    time_diff = mean([server_to_client_time_diff, client_to_server_time_diff])
    return time_per_hop, hops, time_diff

#################################################
#################################################

def Find_Distance (conn_speed, time_diff):
    raw_distance = conn_speed * time_diff

    print ("[S] Based on the conn speed and time difference, distance is: %5.10f km" % raw_distance)
    
    return raw_distance

#################################################
#################################################
# Calling the main function first #
if __name__ == "__main__":
    main ()
#####################
