#!/bin/bash

set -e

export birchrest_log_level='test'

PYTHONPATH=. python3 example/main.py &
SERVER_PID=$!

sleep 3

URL="http://127.0.0.1:13337/health"

echo "Running ApacheBench load test on $URL"
ab -n 10000 -c 100 $URL > load_test_result.txt
TEST_RESULT=$?

kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

if [ $TEST_RESULT -ne 0 ]; then
    echo "Load test failed with exit code $TEST_RESULT"
    cat load_test_result.txt
    exit $TEST_RESULT
fi

FAILED_REQUESTS=$(grep "Failed requests:" load_test_result.txt | awk '{print $3}')
if [ -z "$FAILED_REQUESTS" ] || [ "$FAILED_REQUESTS" -ne 0 ]; then
    echo "Failed requests found: $FAILED_REQUESTS"
    cat load_test_result.txt
    exit 1
fi

NON_2XX_RESPONSES=$(grep "Non-2xx responses:" load_test_result.txt | awk '{print $3}' || echo "0")
if [ -z "$NON_2XX_RESPONSES" ]; then
    NON_2XX_RESPONSES=0
fi
if [ "$NON_2XX_RESPONSES" -ne 0 ]; then
    echo "Non-2xx responses found: $NON_2XX_RESPONSES"
    cat load_test_result.txt
    exit 1
else
    echo "No non-2xx responses found."
fi

REQS_PER_SEC=$(grep "Requests per second:" load_test_result.txt | awk '{print $4}')
if [ -z "$REQS_PER_SEC" ]; then
    echo "Error: Could not retrieve requests per second."
    exit 1
fi
if (( $(echo "$REQS_PER_SEC < 4000" | bc -l) )); then
    echo "Requests per second ($REQS_PER_SEC) below threshold (4000)"
    cat load_test_result.txt
    exit 1
fi

PERCENTILE_95=$(grep "  95% " load_test_result.txt | awk '{print $2}')
if [ -z "$PERCENTILE_95" ]; then
    echo "Error: Could not retrieve 95th percentile response time."
    cat load_test_result.txt
    exit 1
fi
if (( $(echo "$PERCENTILE_95 > 1120" | bc -l) )); then
    echo "95th percentile response time ($PERCENTILE_95 ms) exceeds 1120 ms"
    cat load_test_result.txt
    exit 1
fi

echo "Load test passed successfully"
cat load_test_result.txt

echo "Server process killed"
