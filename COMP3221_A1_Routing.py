import json
import signal
import sys
import threading
import socket
import time
import heapq
import traceback

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def new_node(self, node):
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = {}
        
    def new_edge(self, node1, node2, w):
        self.new_node(node1)
        self.new_node(node2)
        
        self.edges[node1][node2] = (float(w[0]),w[1])
        self.edges[node2][node1] = (float(w[0]),w[1])
        
    
    def update_edge(self, node1, node2, new_weight,time):
        if node1 in self.edges:
            if node2 in self.edges[node1]:
                self.edges[node1][node2] = (float(new_weight),time)
                self.edges[node2][node1] = (float(new_weight),time)

    def neighbors(self, node):
        return self.edges[node]
    
    def get_weight(self, node1, node2):
        if node1 in self.nodes and node2 in self.neighbors(node1):
            return self.edges[node1][node2][0]
        else:
            return -1
    
    def get_port(self, node1, node2):
        if node1 in self.nodes and node2 in self.neighbors(node1):
            return self.edges[node1][node2][1]
        else:
            return -1
    

HOST = "127.0.0.1"
lock = threading.Lock()

neighbours = {}
network = Graph()
recalculate_routes = True
filepath = "";
previous = ({},{})
threads = []

def main(args):
    node_id = args[1]
    port_no = int(args[2])
    node_config_file = args[3]
    global filepath
    filepath = node_config_file
    #Open config file
    f = open(node_config_file, "r")
    no_neighbours = f.readline()
    lines = f.readlines()
    f.close()

    #Add neighbours to dictionary
    for x in lines:
        line = x.strip("\n").split(" ")
        neighbours[line[0]] = (line[1], line[2])
        network.new_edge(node_id,line[0],(line[1],time.time()))

    #Create threads 3/4
    listening = MyThread(0,port_no,node_id)
    sending = MyThread(1,port_no,node_id)
    changes = MyThread(3,port_no, node_id)

    threads.append(listening)
    threads.append(sending)
    threads.append(changes)

    listening.start()
    sending.start()
    changes.start()
    
    #Wait 60 seconds until starting routing calculations
    time.sleep(60)

    #Start routing calculation thread
    calculate_routes = MyThread(2,port_no,node_id)
    threads.append(calculate_routes)
    calculate_routes.start()

    return

def update_network(updates, node_id):
    try:
        lock.acquire()
        #Store neighbours state before update to check for changes.
        old_neighbours = neighbours.copy()
        
        #Iterate through each edge in the updates
        for node in updates.keys():
            for node2 in updates[node].keys():

                #Checking edge exists already
                if node in network.edges and node2 in network.edges[node]:  

                    #Checking time is more recent
                    if float(updates[node][node2][1]) > network.edges[node][node2][1]:

                        #Checking new weight is different
                        if network.get_weight(node,node2) != updates[node][node2][0]:
                            
                            #Update network
                            network.update_edge(node,node2,updates[node][node2][0],float(updates[node][node2][1]))
                            
                            #Update neighbours
                            if node_id == node:
                                neighbours[node2] = (updates[node][node2][0], neighbours[node2][1])
                            elif node_id == node2:
                                neighbours[node] = (updates[node2][node][0], neighbours[node][1])
                            
                else:
                    #Add new edge
                    network.new_edge(node,node2,updates[node][node2])

        
        global recalculate_routes
        recalculate_routes = True

        #Save to file if neighbours have changed weight
        if old_neighbours != neighbours:
            save_to_file()
        
    except Exception as e:
        print(e)

    finally:
        lock.release()
    
def save_to_file():

    global filepath
    f = open(filepath, "w")

    lines = []
    lines.append(str(len(neighbours))+"\n")

    for x in neighbours.keys():
        lines.append(x + " " + str(neighbours[x][0]) + " " + str(neighbours[x][1]) +"\n")

    lines[-1] = lines[-1].strip("\n")
    f.writelines(lines)
        
def listening(port, node_id):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, port))
            s.listen()

            while(1):
                c, addr = s.accept()
                msg_in = c.recv(100000)

                if msg_in:
                    message = json.loads(msg_in)
                    updates = message["edges"]
                    update_network(updates,node_id)

                
    except Exception as e:
        print("EXCEPTION: " + str(e) + "\n")
        traceback.print_exc()
        
def sending(node_id):
    visited = set()
    lock.acquire()

    for node in neighbours.keys():
        if node not in visited:
            try: 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, int(neighbours[node][1])))
                    message = {'edges':network.edges, 'from': node_id}
                    s.sendall((json.dumps(message)).encode())
                        
            except Exception as e:
                network.update_edge(node_id,node,float('inf'),time.time())
                global recalculate_routes
                recalculate_routes = True
                
            visited.add(node)
    lock.release()

def routing_calculations(node_id):
    distances = {node: float('inf') for node in network.nodes}
    distances[node_id] = 0

    q = [(0,node_id)]

    shortest_routes = {node_id : node_id}
    
    while q:
        current_distance, current_node = heapq.heappop(q)
        if current_distance > distances[current_node]:
            continue

        for neighbour in network.neighbors(current_node):
            
            new_dist = distances[current_node] + float(network.get_weight(neighbour, current_node))

            if new_dist < distances[neighbour]:
                distances[neighbour] = new_dist
                shortest_routes[neighbour] = shortest_routes[current_node] + neighbour
                heapq.heappush(q,(new_dist,neighbour))
    
    global previous
    if previous != (shortest_routes,distances):
        print("I am node " + node_id)
        for dest in shortest_routes.keys():
            if distances[dest] != float('inf') and dest != node_id:
                print("Least cost path from " + node_id + " to " + dest + ": " + shortest_routes[dest] + ", link cost: " + str(distances[dest]))

    lock.acquire()
    previous = (shortest_routes,distances)
    lock.release()

class MyThread(threading.Thread):
    def __init__(self,threadID,port, node_id):
        threading.Thread.__init__(self)
        self._stop = threading.Event() 
        self.threadID = threadID
        self.port = port
        self.node_id = node_id
    def run(self):
        global recalculate_routes
        if self.threadID == 0:
            listening(self.port,self.node_id)
        elif self.threadID == 1:
            while (1):
                sending(self.node_id)
                time.sleep(10)
        elif self.threadID == 2:
            
            while(1):
                if recalculate_routes == True:
                    # print("Calculating routes.....\n")
                    routing_calculations(self.node_id)
                    lock.acquire()
                    recalculate_routes = False
                    lock.release()
                
                time.sleep(2)
        elif self.threadID == 3:
            while(1):
                neighbour = input("Choose a neighbour to change their weight " + str(list(neighbours.keys()))+ ": ")
                if neighbour in neighbours:
                    
                    try:
                        weight = input("Enter new weight: ")
                        if '.' in weight:
                            weight = float(weight)
                        else:
                            raise Exception
                        lock.acquire()

                        neighbours[neighbour] = (str(weight),neighbours[neighbour][1])
                        network.update_edge(self.node_id,neighbour,str(weight),time.time())
                        recalculate_routes = True
                    except:
                        print("Invalid weight\n")
                    finally:
                        try:
                            lock.release()
                        except:
                            1
                else:
                    print("Invalid neighbour\n")
                save_to_file()


    def stop(self): 
        self._stop.set()
    def stopped(self): 
        return self._stop.isSet() 
      
if __name__ == "__main__":
    main(sys.argv)