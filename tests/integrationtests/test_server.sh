#!/bin/bash

set -e

export birchrest_log_level='test'

PYTHONPATH=. python3 example/main.py &
SERVER_PID=$!

sleep 3

python3 -m unittest tests/integrationtests/server_test.py
TEST_RESULT=$?

kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

if [ $TEST_RESULT -ne 0 ]; then
    echo "Tests failed with exit code $TEST_RESULT"
    exit $TEST_RESULT
else
    echo "Tests passed successfully"
fi

echo "Server process killed"
