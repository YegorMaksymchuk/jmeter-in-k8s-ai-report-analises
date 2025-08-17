# Docker-Based Distributed JMeter Testing

This directory demonstrates how to set up distributed JMeter testing using Docker containers with InfluxDB for metrics storage and Grafana for visualization.

##  What You'll Learn

- **Distributed Testing**: Master-slave architecture for load distribution
- **Docker Networking**: Container communication and isolation
- **Custom Docker Images**: Building JMeter images with plugins
- **Metrics Collection**: Integration with InfluxDB and Grafana
- **Container Orchestration**: Manual container management

##  Quick Start

### Prerequisites

- **Docker**: Installed and running
- **Docker Compose**: For easier orchestration (optional)
- **Basic Docker knowledge**: Understanding containers, networks, and volumes

### Step 1: Build and Tag Custom JMeter Image

First, build the custom JMeter Docker image with pre-installed plugins:

```sh
# Build the custom JMeter image from Dockerfile
docker build -t jmeter-custom .

# Tag the image for better organization
docker tag jmeter-custom demo/jmeter-custom:1.0.0
```

**What this does:**
- `docker build -t jmeter-custom .`: Builds a Docker image from the Dockerfile in current directory
- `docker tag jmeter-custom demo/jmeter-custom:1.0.0`: Tags the image with a version for better management
### Step 2: Create Docker Network

Create a custom network for container communication:

```sh
# Create a custom bridge network for JMeter components
docker network create jmeter-net 
```

**What this does:**
- Creates an isolated network for all JMeter components
- Enables container-to-container communication
- Provides network isolation from other Docker networks
- Allows containers to communicate using container names as hostnames
### Step 3: Run InfluxDB Container

Start InfluxDB for metrics storage:

```sh
# Run InfluxDB container in detached mode
docker run -d --name influxdb \
  --network jmeter-net \
  -p 8086:8086 \
  influxdb:1.8 
```

**What this does:**
- `-d`: Runs container in detached mode (background)
- `--name influxdb`: Names the container for easy reference
- `--network jmeter-net`: Connects to our custom network
- `-p 8086:8086`: Maps container port 8086 to host port 8086
- `influxdb:1.8`: Uses InfluxDB version 1.8 (compatible with JMeter plugins)
### Step 4: Create JMeter Database

Create the database for storing JMeter metrics:

```sh
# Create JMeter database in InfluxDB
curl -i -XPOST http://127.0.0.1:8086/query --data-urlencode "q=CREATE DATABASE jmeter"
```

**What this does:**
- Creates a database named "jmeter" in InfluxDB
- This database will store all JMeter test metrics
- Required before JMeter can send metrics to InfluxDB
- You should see a success response with HTTP 200
### Step 5: Run Grafana Container

Start Grafana for metrics visualization:

```sh
# Run Grafana container in detached mode
docker run -d --name grafana \
  --network jmeter-net \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana 
```

**What this does:**
- `-d`: Runs container in detached mode (background)
- `--name grafana`: Names the container for easy reference
- `--network jmeter-net`: Connects to our custom network
- `-p 3000:3000`: Maps container port 3000 to host port 3000
- `-e GF_SECURITY_ADMIN_PASSWORD=admin`: Sets admin password to "admin"
- `grafana/grafana`: Uses official Grafana image
### Step 6: Configure Grafana

Set up Grafana to visualize JMeter metrics:

1. **Access Grafana**: Open http://localhost:3000 in your browser
2. **Login**: Use username `admin` and password `admin`
3. **Add InfluxDB Data Source**:
   - Go to Configuration → Data Sources
   - Click "Add data source"
   - Select "InfluxDB"
   - Set URL to `http://influxdb:8086` (container name)
   - Set Database to `jmeter`
   - Click "Save & Test"

4. **Import JMeter Dashboard**:
   - Go to Dashboards → Import
   - Enter Dashboard ID: `4026`
   - Or use direct link: [JMeter Dashboard](https://grafana.com/grafana/dashboards/4026-jmeter-dashboard/)
   - Select the InfluxDB data source
   - Click "Import"

**What this does:**
- Connects Grafana to InfluxDB for data visualization
- Imports a pre-configured JMeter dashboard with key metrics
- Enables real-time monitoring of test execution

### Step 7: Create JMeter Slave Containers

Start JMeter slave containers for distributed testing:

#### First Slave Container

**Shell (Linux/Mac):**
```sh
# Create first JMeter slave container
docker run -d --name jmeter-slave-1 \
  --network jmeter-net \
  -p 1099 -p 50000 \
  -v $(pwd)/test:/opt/apache-jmeter-5.5/test \
  demo/jmeter-custom:1.0.0 server 
```

**PowerShell (Windows):**
```ps1
# Create first JMeter slave container
docker run -d --name jmeter-slave-1 `
  --network jmeter-net `
  -p 1099 -p 50000 `
  -v ${pwd}/test:/opt/apache-jmeter-5.5/test `
  demo/jmeter-custom:1.0.0 server 
```

**What this does:**
- `-d`: Runs container in detached mode (background)
- `--name jmeter-slave-1`: Names the container for identification
- `--network jmeter-net`: Connects to our custom network
- `-p 1099 -p 50000`: Exposes JMeter RMI ports (random host ports)
- `-v $(pwd)/test:/opt/apache-jmeter-5.5/test`: Mounts test files from host to container
- `demo/jmeter-custom:1.0.0 server`: Runs the container in slave mode
#### Second Slave Container

**Shell (Linux/Mac):**
```sh
# Create second JMeter slave container
docker run -d --name jmeter-slave-2 \
  --network jmeter-net \
  -p 1099 -p 50000 \
  -v $(pwd)/test:/opt/apache-jmeter-5.5/test \
  demo/jmeter-custom:1.0.0 server
```

**PowerShell (Windows):**
```ps1
# Create second JMeter slave container
docker run -d --name jmeter-slave-2 `
  --network jmeter-net `
  -p 1099 -p 50000 `
  -v ${pwd}/test:/opt/apache-jmeter-5.5/test `
  demo/jmeter-custom:1.0.0 server 
```

**What this does:**
- Creates a second slave container for load distribution
- Same configuration as first slave but with different name
- Enables horizontal scaling of test execution
- Both slaves will be controlled by the master container
### Step 8: Create JMeter Master and Run Test

Start the JMeter master container to orchestrate and execute the test:

**Shell (Linux/Mac):**
```sh
# Create JMeter master container and run test
docker run -it --rm --name jmeter-master \
  --network jmeter-net \
  -v $(pwd)/test:/opt/apache-jmeter-5.5/test \
  demo/jmeter-custom:1.0.0 master
```

**PowerShell (Windows):**
```ps1
# Create JMeter master container and run test
docker run -it --rm --name jmeter-master `
  --network jmeter-net `
  -v ${pwd}/test:/opt/apache-jmeter-5.5/test `
  demo/jmeter-custom:1.0.0 master
```

**What this does:**
- `-it`: Runs container in interactive mode with terminal
- `--rm`: Automatically removes container when it exits
- `--name jmeter-master`: Names the container for identification
- `--network jmeter-net`: Connects to our custom network
- `-v $(pwd)/test:/opt/apache-jmeter-5.5/test`: Mounts test files from host to container
- `demo/jmeter-custom:1.0.0 master`: Runs the container in master mode

**Expected Behavior:**
- The master will discover and connect to slave containers
- Test execution will be distributed across all slaves
- Real-time metrics will be sent to InfluxDB
- You can monitor progress in Grafana dashboard  

##  Cleanup

When you're done testing, clean up all containers and networks:

### Shell (Linux/Mac)
```sh
# Stop all running containers
docker stop jmeter-master jmeter-slave-1 jmeter-slave-2 influxdb grafana

# Remove all containers
docker rm jmeter-master jmeter-slave-1 jmeter-slave-2 influxdb grafana

# Remove the custom network
docker network rm jmeter-net

# Optional: Remove the custom image
docker rmi demo/jmeter-custom:1.0.0
```

### PowerShell (Windows)
```ps1
# Stop all running containers
docker stop jmeter-master, jmeter-slave-1, jmeter-slave-2, influxdb, grafana

# Remove all containers
docker rm jmeter-master, jmeter-slave-1, jmeter-slave-2, influxdb, grafana

# Remove the custom network
docker network rm jmeter-net

# Optional: Remove the custom image
docker rmi demo/jmeter-custom:1.0.0
```

**What this does:**
- Stops all running containers gracefully
- Removes containers to free up disk space
- Removes the custom network
- Optionally removes the custom Docker image

##  Monitoring and Verification

### Check Container Status
```sh
# List all running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Check container logs
docker logs jmeter-slave-1
docker logs jmeter-slave-2
docker logs influxdb
docker logs grafana
```

### Verify Network Connectivity
```sh
# List networks
docker network ls

# Inspect the jmeter-net
docker network inspect jmeter-net

# Test connectivity between containers
docker exec jmeter-master ping jmeter-slave-1
docker exec jmeter-master ping influxdb
```

### Access Services
- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB**: http://localhost:8086
- **JMeter Master**: Interactive terminal session
- **JMeter Slaves**: Background processes

##  Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```sh
   # Check container logs
   docker logs <container-name>
   
   # Check if ports are already in use
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :8086
   ```

2. **Network Connectivity Issues**
   ```sh
   # Verify network exists
   docker network ls | grep jmeter-net
   
   # Recreate network if needed
   docker network rm jmeter-net
   docker network create jmeter-net
   ```

3. **Volume Mount Issues**
   ```sh
   # Check if test directory exists
   ls -la test/
   
   # Verify file permissions
   chmod -R 755 test/
   ```

4. **InfluxDB Connection Issues**
   ```sh
   # Test InfluxDB connectivity
   curl -i http://localhost:8086/ping
   
   # Check if database exists
   curl -i -XPOST http://127.0.0.1:8086/query --data-urlencode "q=SHOW DATABASES"
   ```

### Debug Commands

```sh
# Get container IP addresses
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' jmeter-slave-1
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' jmeter-slave-2

# Execute commands in running containers
docker exec -it jmeter-slave-1 /bin/bash
docker exec -it influxdb /bin/bash

# Check resource usage
docker stats
```

##  Scaling Options

### Add More Slave Containers
```sh
# Create additional slave containers
docker run -d --name jmeter-slave-3 \
  --network jmeter-net \
  -p 1099 -p 50000 \
  -v $(pwd)/test:/opt/apache-jmeter-5.5/test \
  demo/jmeter-custom:1.0.0 server

docker run -d --name jmeter-slave-4 \
  --network jmeter-net \
  -p 1099 -p 50000 \
  -v $(pwd)/test:/opt/apache-jmeter-5.5/test \
  demo/jmeter-custom:1.0.0 server
```

### Custom Test Parameters
```sh
# Run master with custom parameters
docker run -it --rm --name jmeter-master \
  --network jmeter-net \
  -v $(pwd)/test:/opt/apache-jmeter-5.5/test \
  -e JMETER_ARGS="-Jthreads=200 -Jrampup=60 -Jduration=1800" \
  demo/jmeter-custom:1.0.0 master
```

##  Next Steps

After mastering this Docker setup, explore:

1. **03_docker-compose/**: Simplified orchestration with Docker Compose
2. **04_Kubernetes/**: Production deployment with Kubernetes
3. **05_Jenkins/**: Automated test execution with CI/CD
4. **06_AI_report_generation/**: Automated reporting with AI

##  Additional Resources

- [JMeter Distributed Testing Guide](https://jmeter.apache.org/usermanual/remote-test.html)
- [Docker Networking Documentation](https://docs.docker.com/network/)
- [InfluxDB JMeter Integration](https://github.com/novoda/jmeter-influxdb-backend-listener)
- [Grafana JMeter Dashboard](https://grafana.com/grafana/dashboards/4026-jmeter-dashboard/)

---

**Note**: This setup demonstrates manual Docker container orchestration. For production environments, consider using Docker Compose or Kubernetes for better automation and scalability.
