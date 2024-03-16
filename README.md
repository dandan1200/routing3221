STARTING THE PROGRAM:

You start the program with the following command:
python3 COMP3221_A1_Routing.py nodeiD port configfilepath

For example: 
python3 COMP3221_A1_Routing.py A 6001 A.txt

To run the program using the provided network topology:
1. Ensure that all files (A.txt - J.txt) are located in the same directory as the start.bash file as well as the python program
2. Run bash start.bash

All 10 terminal windows will be opened with the program running. 
NOTE: this bash file will only work on MAC OS running the latest software VENTURA. If you don't have this then you will need to start up the app one node at a time.

CONFIG FILES:
Provided in the TestConfigs folder are two sets of test config files.
'Large' includes the config files used in the start.bash script mentioned above which corresponds to the provided 10-node network topology in the report.
'Small' include the config files used in the simulation section of the report corresponding to a 4-node network topology shown also in the report.
Make sure you copy and move these files to the working directory to use the program.

CHANGING LINK COST:

To change link cost you will be prompted first to enter a node to change.
A list of the neighbours will be printed for you to choose from.
Nodes are case sensitive so ensure you are entering the node correctly.
When you press enter you will then be prompted to enter a new weight.
Ensure the new weight is a float number and is positive. For example enter '1.0'. Do not enter just '1' ensure that a decimal place is provided.


CLIENT FAILURE:

Client failure occurs when the port is unreachable, so to fail a client, simply quit the program of that node either by closing the window or using 'ctrl + c' to kill the program.
You can bring the client back online by restarting the node as is explained above. The client will then reconnect with its neighbours and reestablish itself in the network.

ROUTING ALGORITHM:

The routing algorithm will run everytime a link cost is changed, however, it will only print out the costs of each route throughout the network when there is a change to the routes or costs. This runs on a constant cycle, so it may take a few seconds for the new routes to be printed on all nodes after making a link cost change.
