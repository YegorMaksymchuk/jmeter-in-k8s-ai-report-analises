echo "We will start Demo in few seconds"

echo "Scale Jmete Master"

$desiredReplicas=1

kubectl scale deployment jmeter-master -n jmeter --replicas=$desiredReplicas
Write-Host "Scaling jmeter-master to $desiredReplicas replicas..."

do {
    Start-Sleep -Seconds 2

    $status = kubectl get deployment jmeter-master -n jmeter -o json | ConvertFrom-Json
    $readyReplicas = $status.status.readyReplicas
    $readyReplicas = if ($readyReplicas) { [int]$readyReplicas } else { 0 }

    Write-Host "Ready replicas: $readyReplicas / $desiredReplicas"
}
while ($readyReplicas -lt $desiredReplicas)

Write-Host "All Jmeter Master replicas are ready!" -ForegroundColor Green


echo "Scale Jmete Slave"

$desiredReplicas=4

kubectl scale deployment jmeter-slave -n jmeter --replicas=$desiredReplicas
Write-Host "Scaling jmeter-slave to $desiredReplicas replicas..."

do {
    Start-Sleep -Seconds 2

    $status = kubectl get deployment jmeter-slave -n jmeter -o json | ConvertFrom-Json
    $readyReplicas = $status.status.readyReplicas
    $readyReplicas = if ($readyReplicas) { [int]$readyReplicas } else { 0 }

    Write-Host "Ready replicas: $readyReplicas / $desiredReplicas"
}
while ($readyReplicas -lt $desiredReplicas)

Write-Host "All Jmeter slave replicas are ready!" -ForegroundColor Green



echo "Test Start Time"
$testStartTime = Get-Date
$testStartTimeGrafanaLink = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$testStartTimeJmeterList = (Get-Date).ToUniversalTime()


echo "Run Test"
$ips = kubectl get pods -n jmeter -l app=jmeter-slave -o jsonpath="{range .items[*]}{.status.podIP}`n{end}"
$joined = ($ips -split "`n" | Where-Object { $_ -ne "" }) -join ","
$JMETER_MASTER_POD = kubectl get po -n jmeter -l app=jmeter-master -o jsonpath="{.items[0].metadata.name}"
kubectl -n jmeter exec -it $JMETER_MASTER_POD -- jmeter -n -t ./test/test.jmx -R $IPS

echo "Test End Time"
$testEndTime = Get-Date
$testEndTimeGrafanaLink = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$testEndTimeJmeterList = (Get-Date).ToUniversalTime()



# Base URL pattern
$baseUrl = "http://localhost:3000/d/3e682b4e-3144-4434-9c30-4bc0c856b26f/jmeter-dashboard"
$staticParams = "?orgId=1&timezone=browser&var-data_source=beq056f1s8lq8a&var-application=test&var-transaction=Created%20User&refresh=5s"

# Build full URL
$grafanaUrlFirst = "$baseUrl$staticParams&from=$testStartTimeGrafanaLink&to=$testEndTimeGrafanaLink"

# Output result
Write-Host "Grafana URL:" -ForegroundColor Cyan
Write-Host $grafanaUrlFirst


$duration = [math]::Round(($testEndTime - $testStartTime).TotalSeconds, 2)

# 3. Format time for Influx query
$testStartTimeInflux = $testStartTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$testEndTimeInflux = $testEndTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")

# 4. Build Grafana URL
$grafanaUrlSecond = "http://localhost:3000/d/3e682b4e-3144-4434-9c30-4bc0c856b26f/jmeter-dashboard" +
        "?orgId=1&timezone=browser&var-data_source=beq056f1s8lq8a&var-application=test" +
        "&var-transaction=Created%20User&refresh=5s" +
        "&from=$($testStartTimeInflux)&to=$($testEndTimeInflux)"

# 5. Get InfluxDB pod name
$influxPod = kubectl get po -n jmeter -l app=influxdb -o jsonpath="{.items[0].metadata.name}"

# 7. Write test result data to Influx
$writeLine = "test_results,app=jmeter AppVersion=1,Test_Duration=$duration,Time_Frame=time > '$testStartTimeGrafanaLink' AND time < '$testEndTimeGrafanaLink',GrafanaLink=`"$grafanaUrlSecond`""
kubectl exec -n jmeter $influxPod -- curl -i -XPOST "http://localhost:8086/write?db=jmeter_list" --data-binary "$writeLine"

# 8. Show what was written
Write-Host "`nGrafana dashboard link:"
Write-Host $grafanaUrl -ForegroundColor Cyan
Write-Host "Test duration: $duration seconds"






