#!/bin/bash

echo "We will start Demo in few seconds"

echo "Scale Jmeter Master"

desiredReplicas=1

kubectl scale deployment jmeter-master -n jmeter --replicas=$desiredReplicas
echo "Scaling jmeter-master to $desiredReplicas replicas..."

while true; do
    sleep 2
    
    readyReplicas=$(kubectl get deployment jmeter-master -n jmeter -o json | jq -r '.status.readyReplicas // 0')
    
    echo "Ready replicas: $readyReplicas / $desiredReplicas"
    
    if [ "$readyReplicas" -ge "$desiredReplicas" ]; then
        break
    fi
done

echo -e "\033[32mAll Jmeter Master replicas are ready!\033[0m"

echo "Scale Jmeter Slave"

desiredReplicas=4

kubectl scale deployment jmeter-slave -n jmeter --replicas=$desiredReplicas
echo "Scaling jmeter-slave to $desiredReplicas replicas..."

while true; do
    sleep 2
    
    readyReplicas=$(kubectl get deployment jmeter-slave -n jmeter -o json | jq -r '.status.readyReplicas // 0')
    
    echo "Ready replicas: $readyReplicas / $desiredReplicas"
    
    if [ "$readyReplicas" -ge "$desiredReplicas" ]; then
        break
    fi
done

echo -e "\033[32mAll Jmeter slave replicas are ready!\033[0m"

echo "Test Start Time"
testStartTime=$(date)
testStartTimeGrafanaLink=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
testStartTimeJmeterList=$(date -u)

echo "Run Test"
ips=$(kubectl get pods -n jmeter -l app=jmeter-slave -o jsonpath="{range .items[*]}{.status.podIP}{'\n'}{end}" | tr '\n' ',' | sed 's/,$//')
JMETER_MASTER_POD=$(kubectl get po -n jmeter -l app=jmeter-master -o jsonpath="{.items[0].metadata.name}")
kubectl -n jmeter exec -it $JMETER_MASTER_POD -- jmeter -n -t ./test/test.jmx -R $ips

echo "Test End Time"
testEndTime=$(date)
testEndTimeGrafanaLink=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
testEndTimeJmeterList=$(date -u)

# Base URL pattern
baseUrl="http://localhost:3000/d/3e682b4e-3144-4434-9c30-4bc0c856b26f/jmeter-dashboard"
staticParams="?orgId=1&timezone=browser&var-data_source=beq056f1s8lq8a&var-application=test&var-transaction=Created%20User&refresh=5s"

# Build full URL
grafanaUrlFirst="$baseUrl$staticParams&from=$testStartTimeGrafanaLink&to=$testEndTimeGrafanaLink"

# Output result
echo -e "\033[36mGrafana URL:\033[0m"
echo "$grafanaUrlFirst"

# Calculate duration
start_epoch=$(date -d "$testStartTime" +%s)
end_epoch=$(date -d "$testEndTime" +%s)
duration=$(echo "scale=2; $end_epoch - $start_epoch" | bc)

# Format time for Influx query
testStartTimeInflux=$(date -d "$testStartTime" -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
testEndTimeInflux=$(date -d "$testEndTime" -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# Build Grafana URL
grafanaUrlSecond="http://localhost:3000/d/3e682b4e-3144-4434-9c30-4bc0c856b26f/jmeter-dashboard"\
"?orgId=1&timezone=browser&var-data_source=beq056f1s8lq8a&var-application=test"\
"&var-transaction=Created%20User&refresh=5s"\
"&from=$testStartTimeInflux&to=$testEndTimeInflux"

# Get InfluxDB pod name
influxPod=$(kubectl get po -n jmeter -l app=influxdb -o jsonpath="{.items[0].metadata.name}")

# Write test result data to Influx
writeLine="test_results,app=jmeter AppVersion=1,Test_Duration=$duration,Time_Frame=time > '$testStartTimeGrafanaLink' AND time < '$testEndTimeGrafanaLink',GrafanaLink=\"$grafanaUrlSecond\""
kubectl exec -n jmeter $influxPod -- curl -i -XPOST "http://localhost:8086/write?db=jmeter_list" --data-binary "$writeLine"

# Show what was written
echo -e "\nGrafana dashboard link:"
echo -e "\033[36m$grafanaUrlSecond\033[0m"
echo "Test duration: $duration seconds"
