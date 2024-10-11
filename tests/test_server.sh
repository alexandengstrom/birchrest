#!/bin/bash

PYTHONPATH=. python3 example/main.py &
SERVER_PID=$!


sleep 3

python3 -m unittest tests/server_test.py

kill $SERVER_PID
wait $SERVER_PID 2>/dev/null

echo "Server process killed"
