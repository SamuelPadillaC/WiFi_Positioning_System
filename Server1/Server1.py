###############################################
# A server that handles connections
# by Samuelito Perro
###############################################
# IMPORTS
import socket as sc		
import time
import subprocess
from statistics import mean

PORT = 50069
latitude = 42.5000
longitude = -96.4003

##########################################
#            DRIVER FUNCTION             #
##########################################
def main():
    # Welcome Print
    print ("[S] Server process started.")
    print ("[S] This machine is a VPS from Compute Market hosted in Sioux City, IA.")
    print( "[S] Coordenates of host (Lat, Long): 42.5000, -96.4003")

    # Running traceroute bash script
    print ("\n\n[S] Running bash taceroute subprocess with target 35.194.119.7.\nThis might take a few seconds...\nPlease wait until the process is completed to run the client script")
    subprocess.run(["./trace_Google_VM.sh"], shell=True)
    print ("[S] Bash subprocess completed.")

    # Creating socket 
    s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)		 
    print ("\n\n[S] Server Socket Successfully Created.")				

    # Next bind to the port 
    s.bind(("", PORT))		 
    print ("[S] Socket binded to port 50069.") 

    # put the socket into listening mode 
    s.listen(5)	 
    print ("[S] Socket is listening.")			

    # Establish connection with client. 
    conn, addr = s.accept()	 
    print ("[S] Got connection from", addr) 

    # Inform user and Define Time list #
    server_time_diff = []
    i = 0
    print ("\n\n[S] Averaging the time difference of 500 interactions...\nThis might take a few seconds")

    #Average the time difference between 500 messages
    while i < 501:
        # Receive message
        sent_time = float(conn.recv(1024))

        # Find time difference
        server_time_diff.append(time.time() - sent_time)

        #Send time
        conn.send(bytes(str(time.time()), 'utf-8'))

        i += 1

    # Receive the last average of connection and Defining final average #
    client_avg = float(conn.recv(1024))

    # Print
    print ("[S] Interactions performed")
    print ("\n\n[S] The average time of the total communication from CLIENT - SERVER was: %2.10f s" % mean(server_time_diff))
    final_time_avg = mean([client_avg, mean(server_time_diff)])
    print ("[S] The final average time of the communications (both ways included) was: %2.10f s" % final_time_avg)

    # Calcuate number of hops from Compute Market to Google VM
    route, reached = Read_Route("route_to_Google.txt")
    server_hops = Calculate_Hops(route, reached)

    # Hops are measured from local machine to target.
    # The time diff is measured from target to local.
    # Each machine performs the calculations for the other one
    # Send hops and receive.
    print ("[S] Exchanging hop information with client.")
    conn.send(bytes(str(server_hops), 'utf-8'))
    hops = float(conn.recv(1024))

    # Get Server Averages (based on empirical time)
    print ("\n\n[S] Getting local server averages.")
    server_time_per_hop, server_distance_per_hop, server_conn_speed = Averages(hops, mean(server_time_diff))

    # Receive the client averages #
    print ("[S] Receiving client averages.")
    client_time_per_hop = float(conn.recv(1024))
    client_distance_per_hop = float(conn.recv(1024))
    client_conn_speed = float(conn.recv(1024))

    # Get Final Averages (sorry for the horrible function call :/)
    print ("[S] Calculating final averages.")
    final_time_per_hop, final_distance_per_hop, final_conn_speed = Get_Final_Averages(server_time_per_hop, server_distance_per_hop, server_conn_speed, client_time_per_hop, client_distance_per_hop, client_conn_speed, final_time_avg, hops)
    
    # Sending Results back
    print ("\n\n[S] Sending final averages back to the client.")
    conn.send(bytes(str(final_time_avg), 'utf-8'))
    time.sleep(2)
    conn.send(bytes(str(final_time_per_hop), 'utf-8'))
    time.sleep(2)
    conn.send(bytes(str(final_distance_per_hop), 'utf-8'))
    time.sleep(2)
    conn.send(bytes(str(final_conn_speed), 'utf-8'))
    print ("[S] Results for triangulation sent.")


    # Close the connection with the client 
    print ("\n\n[S] Closing client connection.")
    conn.close()
    
    # New Server for Triangulation #
    print ("[S] Setting up new server for new connections...")
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

        #Return vector_lines and False
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
        print ("\n\n[S] The traceroute process was unable to reach the target machine and determine the exact number of router hops.")
        print ("[S] However, there were at least %d recorded router hops before the process was dropped." % hops)
    else:
        print ("\n\n[S] The traceroute process reached the target machine and recorded %d router hops." % hops)
    
    if errors > 0:
        print ("[S] There were %d hops that did not return any time information." % errors)
        print ("[S] Keep in mind that this might afect the final time averages.")
    
    print ("\n\n[S] Based on the data from the TRACEROUTE SUBPROCESS, these are the results:")
    print ("[S] Average TIME per hop: %2.10f s" % mean(time_per_hop))
    print ("[S] TOTAL communication time: %2.10f s" % sum(time_per_hop))


    return hops

#################################################
#################################################

def Averages(num_of_hops, server_time_avg):
    time = server_time_avg / num_of_hops
    #Distance from the 2 machines is hard coded
    distance = 9643.11 / num_of_hops
    speed = 9643.11 / server_time_avg

    return time, distance, speed

#################################################
#################################################

def Get_Final_Averages (server_time_per_hop, server_distance_per_hop, server_conn_speed, client_time_per_hop, client_distance_per_hop, client_conn_speed, final_time_avg, hops):
    # Calculate final averages including client results
    final_time_per_hop = mean([server_time_per_hop, client_time_per_hop])
    final_distance_per_hop = mean([server_distance_per_hop, client_distance_per_hop])
    final_conn_speed = mean([server_conn_speed, client_conn_speed])

    # Print
    print ("\n\n[S] Based on the MEASURED average communication time, these are the results:")
    print ("[S] Average TOTAL COMMUNICATION TIME: %2.10f s" % final_time_avg)
    print ("[S] Average SPEED of communication: %6.10f km/s" % final_conn_speed)
    print ("[S] Number of recorded HOPS: %d" % hops)
    print ("[S] Average TIME PER HOP: %2.10f s" % final_time_per_hop)
    print ("[S] Average DISTANCE per hop: %5.10f km" % final_distance_per_hop)

    return final_time_per_hop, final_distance_per_hop, final_conn_speed

#################################################
#################################################

def New_Server(distance_per_hop, conn_speed):
    #Set new PORT
    NEW_PORT = 50043

    # Creating socket 
    New_Socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)		 
    print ("\n\n\n-----------------------------------------------------")
    print ("[S] New Server Socket Successfully Created.")				

    # Next bind to the port 
    New_Socket.bind(("", NEW_PORT))		 
    print ("[S] New Socket binded to new port 50043.") 

    # put the socket into listening mode 
    New_Socket.listen(5)	 
    print ("[S] New Server Socket is waiting for connections.")			

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
    conn.send(bytes("We're good from CM.", 'utf-8'))

    # Receive client_to_server_hops
    client_to_server_hops = float(conn.recv(1024))
    
    # Calculate server_to_client hops and send to client
    print ("\n\n[S] Exchanging hops information with client.")
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