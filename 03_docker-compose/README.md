# Docker Compose Orchestration for Distributed JMeter Testing

This directory demonstrates how to simplify distributed JMeter testing using Docker Compose. Instead of manually managing individual containers, Docker Compose provides a declarative way to define and run multi-container applications with a single command.

## What You'll Learn

- **Docker Compose Fundamentals**: Declarative container orchestration
- **Service Dependencies**: Managing container startup order
- **Environment Configuration**: Centralized configuration management
- **Simplified Deployment**: Single command to start all services
- **Service Discovery**: Automatic container networking and naming
- **Volume Management**: Persistent data and test file sharing

## Quick Start

### Prerequisites

- **Docker**: Installed and running
- **Docker Compose**: Version 3.8 or higher
- **Custom JMeter Image**: Built from `02_docker/` directory
- **Basic Docker Compose knowledge**: Understanding services, networks, and volumes

### Step 1: Build the Custom JMeter Image

First, ensure you have the custom JMeter image built from the previous directory:

```bash
# Navigate to the docker directory and build the image
cd ../02_docker
docker build -t jmeter-custom .
docker tag jmeter-custom demo/jmeter-custom:1.0.0

# Return to docker-compose directory
cd ../03_docker-compose
```

### Step 2: Start All Services

Launch the entire distributed testing environment with a single command:

```bash
# Start all services defined in docker-compose.yml
docker-compose up -d
```

**What this does:**
- Creates the `jmeter-net` network automatically
- Starts InfluxDB container for metrics storage
- Starts Grafana container for visualization
- Starts JMeter master container with test execution
- All containers are connected to the same network
- Services can communicate using container names as hostnames

### Step 3: Monitor Test Execution

Check the status of all services:

```bash
# View running containers
docker-compose ps

# View logs from all services
docker-compose logs

# View logs from specific service
docker-compose logs jmeter-master
docker-compose logs influxdb
docker-compose logs grafana

# Follow logs in real-time
docker-compose logs -f jmeter-master
```

## Docker Compose Configuration

### Service Overview

The `docker-compose.yml` file defines four main services:

#### 1. InfluxDB Service
```yaml
influxdb:
  image: influxdb:1.8
  container_name: influxdb
  ports:
    - "8086:8086"
  networks:
    - jmeter-net
```

**Configuration Details:**
- Uses InfluxDB version 1.8 (compatible with JMeter plugins)
- Exposes port 8086 for metrics collection
- Connected to the `jmeter-net` network
- Automatically creates the database when first accessed

#### 2. Grafana Service
```yaml
grafana:
  image: grafana/grafana
  container_name: grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  networks:
    - jmeter-net
```

**Configuration Details:**
- Uses official Grafana image
- Exposes port 3000 for web interface
- Sets admin password to "admin"
- Connected to the `jmeter-net` network

#### 3. JMeter Master Service
```yaml
jmeter-master:
  image: demo/jmeter-custom:1.0.0
  container_name: jmeter-master
  volumes:
    - ./test:/opt/apache-jmeter-5.5/test
  command: >
    jmeter -n -t /opt/apache-jmeter-5.5/test/test.jmx 
           -R jmeter-slave-1,jmeter-slave-2 
           -l /opt/apache-jmeter-5.5/test/results.jtl
  networks:
    - jmeter-net
```

**Configuration Details:**
- Uses custom JMeter image with plugins
- Mounts test files from host to container
- Executes test plan automatically on startup
- Connects to slave containers for distributed testing
- Saves results to mounted volume

#### 4. JMeter Slave Services (Commented Out)
```yaml
# jmeter-slave-1:
#   image: demo/jmeter-custom:1.0.0
#   container_name: jmeter-slave-1
#   command: server
#   volumes:
#     - ./test:/opt/apache-jmeter-5.5/test
#   networks:
#     - jmeter-net
```

**Note:** Slave services are commented out in this example. Uncomment them for true distributed testing.

### Network Configuration
```yaml
networks:
  jmeter-net:
    driver: bridge
```

**What this does:**
- Creates a custom bridge network
- Enables container-to-container communication
- Provides network isolation
- Allows service discovery by container name

## Service Management

### Starting Services

```bash
# Start all services in background
docker-compose up -d

# Start specific service
docker-compose up -d influxdb
docker-compose up -d grafana

# Start with custom configuration
docker-compose -f docker-compose.yml up -d
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop jmeter-master
```

### Scaling Services

```bash
# Scale JMeter slaves (when uncommented)
docker-compose up -d --scale jmeter-slave=3

# Scale with custom configuration
docker-compose -f docker-compose.yml up -d --scale jmeter-slave=5
```

### Viewing Service Information

```bash
# List all services and their status
docker-compose ps

# Show service configuration
docker-compose config

# View service logs
docker-compose logs [service-name]

# Execute commands in running containers
docker-compose exec jmeter-master /bin/bash
docker-compose exec influxdb /bin/bash
```

## Configuration Customization

### Environment Variables

Create a `.env` file for environment-specific configuration:

```bash
# .env file
INFLUXDB_VERSION=1.8
GRAFANA_PASSWORD=admin
JMETER_THREADS=100
JMETER_RAMPUP=10
JMETER_DURATION=3600
```

Update `docker-compose.yml` to use these variables:

```yaml
influxdb:
  image: influxdb:${INFLUXDB_VERSION}

grafana:
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

jmeter-master:
  environment:
    - JMETER_THREADS=${JMETER_THREADS}
    - JMETER_RAMPUP=${JMETER_RAMPUP}
    - JMETER_DURATION=${JMETER_DURATION}
```

### Custom Test Parameters

Modify the JMeter command in `docker-compose.yml`:

```yaml
jmeter-master:
  command: >
    jmeter -n 
           -t /opt/apache-jmeter-5.5/test/test.jmx 
           -R jmeter-slave-1,jmeter-slave-2 
           -l /opt/apache-jmeter-5.5/test/results.jtl
           -Jthreads=${JMETER_THREADS:-100}
           -Jrampup=${JMETER_RAMPUP:-10}
           -Jduration=${JMETER_DURATION:-3600}
```

### Volume Mounts

Add persistent volumes for data storage:

```yaml
influxdb:
  volumes:
    - influxdb_data:/var/lib/influxdb

grafana:
  volumes:
    - grafana_data:/var/lib/grafana

volumes:
  influxdb_data:
  grafana_data:
```

## Monitoring and Verification

### Service Health Checks

```bash
# Check if all services are running
docker-compose ps

# Verify network connectivity
docker-compose exec jmeter-master ping influxdb
docker-compose exec jmeter-master ping grafana

# Check service logs for errors
docker-compose logs --tail=50
```

### Access Services

- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB**: http://localhost:8086
- **JMeter Results**: `./test/results.jtl`

### Database Setup

After starting services, create the JMeter database:

```bash
# Create JMeter database in InfluxDB
curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE jmeter"

# Verify database creation
curl -i -XPOST http://localhost:8086/query --data-urlencode "q=SHOW DATABASES"
```

## Troubleshooting

### Common Issues

1. **Services Won't Start**
   ```bash
   # Check Docker Compose syntax
   docker-compose config
   
   # View detailed error logs
   docker-compose logs
   
   # Check if ports are already in use
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :8086
   ```

2. **Network Connectivity Issues**
   ```bash
   # Inspect network configuration
   docker network ls
   docker network inspect 03_docker-compose_jmeter-net
   
   # Test connectivity between services
   docker-compose exec jmeter-master ping influxdb
   ```

3. **Volume Mount Issues**
   ```bash
   # Check if test directory exists
   ls -la test/
   
   # Verify file permissions
   chmod -R 755 test/
   
   # Check volume mounts
   docker-compose exec jmeter-master ls -la /opt/apache-jmeter-5.5/test/
   ```

4. **Image Not Found**
   ```bash
   # Verify custom image exists
   docker images | grep jmeter-custom
   
   # Rebuild image if needed
   cd ../02_docker
   docker build -t jmeter-custom .
   docker tag jmeter-custom demo/jmeter-custom:1.0.0
   cd ../03_docker-compose
   ```

### Debug Commands

```bash
# Get detailed service information
docker-compose ps -a

# View service configuration
docker-compose config

# Execute commands in running containers
docker-compose exec jmeter-master /bin/bash
docker-compose exec influxdb /bin/bash

# Check resource usage
docker stats $(docker-compose ps -q)
```

## Advanced Configuration

### Multiple Environments

Create environment-specific compose files:

```bash
# Development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Service Dependencies

Add dependency management:

```yaml
jmeter-master:
  depends_on:
    - influxdb
    - grafana
  restart: unless-stopped
```

### Resource Limits

Add resource constraints:

```yaml
jmeter-master:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

## Cleanup

### Stop and Remove Services

```bash
# Stop all services and remove containers
docker-compose down

# Stop and remove containers, networks, and volumes
docker-compose down -v

# Remove images as well
docker-compose down --rmi all
```

### Clean Up Resources

```bash
# Remove unused networks
docker network prune

# Remove unused volumes
docker volume prune

# Remove unused images
docker image prune
```

## Next Steps

After mastering Docker Compose orchestration, explore:

1. **04_Kubernetes/**: Production deployment with Kubernetes
2. **05_Jenkins/**: Automated test execution with CI/CD
3. **06_AI_report_generation/**: Automated reporting with AI

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [JMeter Distributed Testing Guide](https://jmeter.apache.org/usermanual/remote-test.html)
- [InfluxDB Docker Documentation](https://hub.docker.com/_/influxdb)
- [Grafana Docker Documentation](https://hub.docker.com/r/grafana/grafana)

---

**Note**: Docker Compose simplifies container orchestration compared to manual Docker commands. For production environments with complex requirements, consider using Kubernetes for better scalability and management.
