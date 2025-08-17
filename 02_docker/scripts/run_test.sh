#!/bin/bash

# Get test name from JMX file
TEST_NAME=$(basename "$2" .jmx)

# Record start time
START_TIME=$(date +%s)

# Run JMeter test
jmeter -n -t "$2" -R "$3"

# Record end time
END_TIME=$(date +%s)

# Calculate duration
DURATION=$((END_TIME - START_TIME))

# Send data to InfluxDB
curl -i -XPOST "http://influxdb:8086/write?db=jmeter" \
  --data-binary "TestList,test_name=${TEST_NAME} start_time=${START_TIME},end_time=${END_TIME},duration=${DURATION}"

echo "Test completed. Duration: ${DURATION} seconds"
