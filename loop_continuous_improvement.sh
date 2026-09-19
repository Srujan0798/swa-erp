#!/bin/bash
# Continuous Improvement Loop for swa-erp
# Runs every 5 minutes: runs all gates, commits if all pass

PURPOSE="continuous-improvement"
INTERVAL=300  # 5 minutes in seconds
SENTINEL="AGENT_LOOP_TICK_${PURPOSE}"

echo "Starting continuous improvement loop for ${PURPOSE} every ${INTERVAL}s"
echo "Sentinel: ${SENTINEL}"

# Run once immediately
echo "Running initial gate check..."
/Users/srujansai/Desktop/swa-erp/run_gates.sh

while true; do
    sleep ${INTERVAL}
    echo "${SENTINEL} {\"prompt\":\"Run all gates and commit if green\"}"
done
