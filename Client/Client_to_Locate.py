import socket as sc		
import time, os
import subprocess
import signal
from statistics import mean

##########################################
#            DRIVER FUNCTION             #
##########################################
def main ():
    # Initialize necessary variables #
    Server2_Coordenates = (0, 0)
    Server2_Distance = 0
    Server1_Coordenates = (0, 0)
    Server1_Distance = 0

    # Welcome Print
    print ("[C] Dev CLient started.")
    print ("[C] Will try to estimate the location of this machine by connecting to Google VM and Compute Market VPS.")

    # Fork Process to perform both connections #
    print ("\n\n[C] Forking process.")
    n = os.fork()

    if n > 0: #PARENT process
        print ("\n\n[C] Parent process separated.\nThe parent pid is: ", os.getpid())
        print ("[C - P] For identification purposes, the parent process will be printed with a P.")
        Target_Server = <"IP ADDRESS OF SERVER2">
        PORT = 50042
        trace_rt = "route_to_Google.txt"

        print ("\n\n[C - P] Parent process runnig bash traceroute subprocess with target <"IP ADDRESS OF SERVER2">.\nThis might take a few seconds please wait...")
        subprocess.run(["./trace_GVM.sh"], shell=True)
        print ("[C - P] Bash subprocess completed.")
        
        print ("\n\n[C - P] The parent process will attempt connection to <"IP ADDRESS OF SERVER2">")
        child_pid = n
        pid = 'P'
        time_diff = []
    
    else:  #CHILD process
        print ("\n\n[C] Child process spawned.\nThe child pid is: ", os.getpid())
        print ("[C - C] For identification purposes, the parent process will be printed with a C.")
        Target_Server = <"IP ADDRESS OF SERVER1"> #Compute Market
        PORT = 50043
        trace_rt = "route_to_cm.txt"

        print ("\n\n[C - C] Child process runnig bash traceroute subprocess with target <"IP ADDRESS OF SERVER1">.\nThis might take a few seconds please wait...")
        subprocess.run(["./trace_CM.sh"], shell=True)
        print ("[C - C] Bash subprocess completed.")

        pid = 'C'
        time_diff = []
        print ("\n\n[C - C] The child process will attempt connection to <"IP ADDRESS OF SERVER1">")


    # Both processes run this
    # Create socket object - AF_INET is IPv4 
    s = sc.socket(sc.AF_INET, sc.SOCK_STREAM) 
    print("[C - %s] Socket successfully created." % pid)

    # Connecting to the server 
    s.connect((Target_Server, PORT)) 
    print("[C - %s] The socket has successfully connected to %s" % (pid, Target_Server))

    # Communicating 200 times
    print ("\n\n[C - %s] Averaging communication 100 times with %s server." % (pid, Target_Server))
    i = 0
    while i < 101:
        #Sending time
        s.send(bytes(str(time.time()), 'utf-8'))

        #Receive message
        sent_time = float(s.recv(1024))

        #Append time difference
        time_diff.append(time.time() - sent_time)

        i += 1
    print ("[C - %s] Communications performed." % pid)


    # Wait for servers to notify traceroute completion
    print ("\n\n[C - %s] Client waiting for server to perform traceroute subprocess." % pid)
    time.sleep(3)
    good = s.recv(1024) #Hold processes until receiving message from server
    if good:
        print ("[C - %s] Server has notified that traceroute was completed." % pid)

    #Calculate and send time hops
    print ("\n\n[C - %s] Exchanging hops information with the server." % pid)
    client_to_server_hops = Calculate_Hops(trace_rt)
    s.send(bytes(str(client_to_server_hops), 'utf-8'))

    #Receive hops and calculate avg time
    server_to_client_avg_time = mean(time_diff)
    server_to_client_hops = float(s.recv(1024))

    #Calculate time per hop
    print ("\n\n[C - %s] Caculating average time per hop." % pid)
    server_to_client_time_per_hop = server_to_client_avg_time / server_to_client_hops
    
    # Send results to client
    print ("[C - %s] Sending time, hops, and time per hop to server." % pid)
    s.send(bytes(str(server_to_client_avg_time), 'utf-8')) #time
    time.sleep(2) #sleep process to avoid overflow
    s.send(bytes(str(server_to_client_hops), 'utf-8')) #hops
    time.sleep(2)
    s.send(bytes(str(server_to_client_time_per_hop), 'utf-8')) #time/hops

    # Receiving distance results
    print ("\n\n[C - %s] Waiting for server to calculate distance..." % pid)
    print ("[C - %s] Receiving distance results from servers." % pid)
    distance = float(s.recv(1024))
    latitude = float(s.recv(1024))
    longitude = float(s.recv(1024))
    print ("[C - %s] Results received." % pid)

    # Update results and kill child
    if pid == 'P': #PARENT
        Server2_Coordenates = (latitude, longitude)   
        Server2_Distance = distance 
        print ("\n\n[C - P] Child process killed")
    
    elif pid == 'C': #CHILD
        Server1_Coordenates = (latitude, longitude)
        Server1_Distance = distance
        exit(0)

    print ("\n\n[C] Calculating coordenates...")
    Coor = Find_Coordenates (Server1_Distance, Server2_Distance, Server1_Coordenates, Server2_Coordenates)


#################################################
#################################################

def Calculate_Hops(path):
    # Open the traceroute log file #
    file_object = open(path, 'r')
    vector_lines = (file_object.readlines()) # Reads all the lines into the vector vector_lines
    file_object.close()

    #Ignore header for vector_lines
    vector_lines = vector_lines[1:]

    #Analyze last line to see if traceroute reached the final destination
    last_line = vector_lines[-1].split()

    if last_line[1] != '*': #This means it reached its final destination
        vector_lines = vector_lines[:-1] #Ignore the last line (target machine)
        #Return vector_lines and true
        return len(vector_lines)

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

        #Return vector_lines and False
        return len(lines)

#################################################
#################################################

def Find_Coordenates (S1_D, S2_D, S1_Coor, S2_Coor):
    print ("[C] The estimated distance from Compute Market server is: ", S1_D)
    print ("[C] The estimated distance from Google VM server is: ", S2_D)


    print ("\n\nDidn't have time to write the equation to find coordinates.")
    return

#################################################
#################################################
# Calling the main function first #
if __name__ == "__main__":
    main ()
#####################
