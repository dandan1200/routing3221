#!/bin/bash

LETTERS=("A" "B" "C" "D" "E" "F" "G" "H" "I" "J")
PORTS=("6001" "6002" "6003" "6004" "6005" "6006" "6007" "6008" "6009" "6010")


for i in "${!LETTERS[@]}"
do
    COMMAND="python3 COMP3221_A1_Routing.py ${LETTERS[$i]} ${PORTS[$i]} ${LETTERS[$i]}.txt"
    DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    osascript -e "tell application \"Terminal\" to do script \"cd '$DIR'; $COMMAND\""
done