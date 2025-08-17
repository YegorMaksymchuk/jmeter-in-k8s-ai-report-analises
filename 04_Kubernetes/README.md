# Kubernetes Deployment for Distributed JMeter Testing

This directory demonstrates how to deploy distributed JMeter testing in a Kubernetes cluster. Kubernetes provides production-grade orchestration with automatic scaling, load balancing, and high availability for your JMeter testing infrastructure.

## What You'll Learn

- **Kubernetes Fundamentals**: Pods, Services, Deployments, and Namespaces
- **Local Cluster Setup**: Using k3d for development and testing
- **Production Deployment**: Scalable and resilient JMeter infrastructure
- **Service Discovery**: Automatic container networking and load balancing
- **Horizontal Scaling**: Dynamic scaling of JMeter slave pods
- **Persistent Storage**: Managing test data and metrics storage
- **Monitoring Integration**: InfluxDB and Grafana in Kubernetes

## Quick Start

### Prerequisites

- **Docker**: Installed and running
- **kubectl**: Kubernetes command-line tool
- **k3d**: Lightweight Kubernetes cluster for local development
- **Custom JMeter Image**: Built and pushed to a registry

### Step 1: Install k3d (Lightweight Kubernetes)

k3d is a lightweight wrapper to run k3s (Rancher Lab's minimal Kubernetes distribution) in Docker. It's perfect for local development and testing.

#### Windows Installation
```powershell
# Using Chocolatey package manager
choco install k3d
```

#### macOS Installation
```bash
# Using Homebrew package manager
brew install k3d
```

#### Linux Installation
```bash
# Using the official installation script
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

**What this does:**
- Installs k3d CLI tool for managing local Kubernetes clusters
- Provides a lightweight alternative to minikube or kind
- Enables local Kubernetes development without heavy resource requirements

### Step 2: Create a Local Kubernetes Cluster

Create a k3d cluster with port forwarding for external access:

```bash
# Create a new cluster with port forwarding for Grafana
k3d cluster create jmeter-cluster -p "3000:3000@loadbalancer"
```

**What this does:**
- Creates a new Kubernetes cluster named "jmeter-cluster"
- Sets up port forwarding for port 3000 (Grafana web interface)
- Uses loadbalancer for external access to services
- Provides a local development environment for testing

### Step 3: Navigate to Kubernetes Deployment Directory

```bash
# Navigate to the deployment directory
cd deployment
```

## Kubernetes Deployment Steps

### Step 4: Create a Namespace

Namespaces provide a way to divide cluster resources between multiple users, teams, or applications.

```bash
# Create a dedicated namespace for JMeter components
kubectl apply -f 01_namespace.yml
```

**What this does:**
- Creates a namespace called "jmeter" to isolate all JMeter-related resources
- Provides logical separation from other applications in the cluster
- Enables better resource management and access control

### Step 5: Deploy InfluxDB

Deploy InfluxDB for metrics storage with persistent volume support.

```bash
# Deploy InfluxDB service and deployment
kubectl apply -f 02_influxdb.yml
```

**What this does:**
- Creates an InfluxDB service for internal cluster communication
- Deploys InfluxDB container with persistent storage
- Exposes port 8086 for metrics collection
- Enables JMeter to send metrics to InfluxDB

### Step 6: Create JMeter Database

After InfluxDB is running, create the database for storing JMeter metrics.

```bash
# Get the InfluxDB pod name
INFLUX_POD=$(kubectl get po -n jmeter -l app=influxdb -o jsonpath='{.items[0].metadata.name}')

# Create the JMeter database
kubectl exec -it $INFLUX_POD -n jmeter -- \
  curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE jmeter"
```

**What this does:**
- Retrieves the InfluxDB pod name using label selectors
- Executes a command inside the InfluxDB container
- Creates a database named "jmeter" for storing test metrics
- Required before JMeter can send metrics to InfluxDB

### Step 7: Deploy Grafana

Deploy Grafana for metrics visualization with NodePort service for external access.

```bash
# Deploy Grafana service and deployment
kubectl apply -f 03_grafana.yml
```

**What this does:**
- Creates a Grafana service with NodePort type for external access
- Deploys Grafana container with admin password configuration
- Exposes port 3000 for web interface access
- Enables visualization of JMeter test metrics

### Step 8: Verify Grafana Deployment

Check that Grafana is running and accessible.

```bash
# Get the Grafana pod name
GRAFANA_POD=$(kubectl get po -n jmeter -l app=grafana -o jsonpath='{.items[0].metadata.name}')

# Check if Grafana is listening on port 3000
kubectl exec -n jmeter -it $GRAFANA_POD -- netstat -tuln
```

**Expected Output:**
```
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 :::3000                 :::*                    LISTEN
```

**What this does:**
- Verifies that Grafana pod is running correctly
- Confirms that Grafana is listening on the expected port
- Ensures the service is ready for external access

### Step 9: Access Grafana Web Interface

Set up port forwarding to access Grafana from your local machine.

```bash
# Forward local port 3000 to Grafana service
kubectl port-forward -n jmeter svc/grafana 3000:3000
```

**What this does:**
- Creates a tunnel between your local machine and the Grafana service
- Allows you to access Grafana at http://127.0.0.1:3000
- Maintains the connection until you stop the port-forward command

**Next Steps:**
1. Open http://127.0.0.1:3000 in your browser
2. Login with username: `admin` and password: `admin`
3. Add InfluxDB as a data source (URL: `http://influxdb:8086`, Database: `jmeter`)
4. Import JMeter dashboard (ID: 4026)

## JMeter Image Management

### Step 10: Build and Push Custom JMeter Image

Create a custom JMeter image with plugins and push it to a registry.

```bash
# Navigate to the docker directory
cd docker

# Build the custom JMeter image
docker build -t jmeter-custom .

# Tag the image for registry
docker tag jmeter-custom yemax/jmeter-custom:1.0.1

# Push to Docker Hub (or your preferred registry)
docker push yemax/jmeter-custom:1.0.1
```

**What this does:**
- Builds a custom JMeter image with pre-installed plugins
- Tags the image with a version for better management
- Pushes the image to a registry for Kubernetes to pull
- Ensures all JMeter pods use the same image version

### Step 11: Import Image to k3d Registry (Optional)

For local development, you can import the image directly to the k3d cluster.

```bash
# Import the image to the k3d cluster registry
k3d image import demo/jmeter-custom:1.0.1 --cluster jmeter-cluster
```

**What this does:**
- Imports the Docker image directly into the k3d cluster
- Avoids the need to push to an external registry
- Useful for local development and testing
- Ensures the image is available for pod deployment

## Running Distributed JMeter Tests

### Step 12: Deploy JMeter Components

Deploy JMeter master and slave pods for distributed testing.

```bash
# Deploy JMeter slave pods (start with 0 replicas)
kubectl apply -f 04_jmeter_slave.yml

# Deploy JMeter master pod (start with 0 replicas)
kubectl apply -f 05_jmeter_master.yml
```

**What this does:**
- Creates deployments for JMeter master and slave components
- Starts with 0 replicas to avoid automatic test execution
- Enables manual scaling and control over test execution
- Provides the infrastructure for distributed testing

### Step 13: Scale JMeter Slaves

Scale the number of JMeter slave pods based on your load requirements.

```bash
# Scale to 2 JMeter slave pods
kubectl scale deployment jmeter-slave -n jmeter --replicas=2

# Scale to 4 JMeter slave pods for higher load
kubectl scale deployment jmeter-slave -n jmeter --replicas=4

# Scale to 10 JMeter slave pods for maximum load
kubectl scale deployment jmeter-slave -n jmeter --replicas=10
```

**What this does:**
- Dynamically scales the number of JMeter slave pods
- Enables horizontal scaling based on load requirements
- Provides flexibility to adjust capacity without rebuilding
- Demonstrates Kubernetes auto-scaling capabilities

### Step 14: Execute JMeter Test

Run the JMeter test using the master pod to coordinate with slave pods.

#### Shell (Linux/macOS)
```bash
# Get the JMeter master pod name
JMETER_MASTER_POD=$(kubectl get po -n jmeter -l app=jmeter-master -o jsonpath='{.items[0].metadata.name}')

# Get all JMeter slave pod IPs
IPS=$(kubectl get pods -n jmeter -l app=jmeter-slave -o jsonpath='{range .items[*]}{.status.podIP}{","}{end}' | sed 's/,$//')

# Execute the JMeter test
kubectl -n jmeter exec -it $JMETER_MASTER_POD -- jmeter -n -t ./test/test.jmx -R $IPS
```

#### PowerShell (Windows)
```powershell
# Get all JMeter slave pod IPs
$ips = kubectl get pods -n jmeter -l app=jmeter-slave -o jsonpath="{range .items[*]}{.status.podIP}`n{end}"
$joined = ($ips -split "`n" | Where-Object { $_ -ne "" }) -join ","

# Get the JMeter master pod name
$JMETER_MASTER_POD = kubectl get po -n jmeter -l app=jmeter-master -o jsonpath="{.items[0].metadata.name}"

# Execute the JMeter test
kubectl -n jmeter exec -it $JMETER_MASTER_POD -- jmeter -n -t ./test/test.jmx -R $joined
```

**What this does:**
- Retrieves the JMeter master pod name using label selectors
- Collects all JMeter slave pod IP addresses
- Executes the JMeter test plan on the master pod
- Distributes the load across all slave pods
- Coordinates test execution and result collection

## Advanced Features

### Grafana MCP Integration

Deploy Grafana MCP (Model Context Protocol) for automated reporting.

```bash
# Deploy Grafana MCP service
kubectl apply -f 06_grafana_mcp.yml
```

**What this does:**
- Deploys Grafana MCP service for automated reporting
- Provides API access to Grafana dashboards
- Enables integration with AI-powered report generation
- Supports automated screenshot capture and analysis

### Service Account Token

For MCP integration, you'll need a service account token:

```
Service account token: Your Service Account Token
```

**What this does:**
- Provides authentication for MCP services
- Enables secure communication between components
- Required for automated report generation
- Supports AI integration features

## Monitoring and Management

### Check Pod Status

```bash
# View all pods in the jmeter namespace
kubectl get pods -n jmeter

# View detailed pod information
kubectl describe pods -n jmeter

# View pod logs
kubectl logs -n jmeter <pod-name>
```

### Scale Load Dynamically

```bash
# Scale JMeter slaves based on load requirements
kubectl scale deployment jmeter-slave -n jmeter --replicas=4

# Monitor scaling progress
kubectl get pods -n jmeter -l app=jmeter-slave

# Check resource usage
kubectl top pods -n jmeter
```

### Access Services

- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB**: Internal cluster access only
- **JMeter Master**: Interactive terminal session
- **JMeter Slaves**: Background processes

## Troubleshooting

### Common Issues

1. **Pods Not Starting**
   ```bash
   # Check pod status
   kubectl get pods -n jmeter
   
   # View pod events
   kubectl describe pod <pod-name> -n jmeter
   
   # Check pod logs
   kubectl logs <pod-name> -n jmeter
   ```

2. **Image Pull Issues**
   ```bash
   # Check if image exists in cluster
   k3d image list --cluster jmeter-cluster
   
   # Import image if needed
   k3d image import demo/jmeter-custom:1.0.1 --cluster jmeter-cluster
   ```

3. **Network Connectivity**
   ```bash
   # Test connectivity between pods
   kubectl exec -n jmeter <pod-name> -- ping <target-pod-ip>
   
   # Check service endpoints
   kubectl get endpoints -n jmeter
   ```

4. **Port Forwarding Issues**
   ```bash
   # Check if port is already in use
   netstat -tulpn | grep :3000
   
   # Use different local port
   kubectl port-forward -n jmeter svc/grafana 3001:3000
   ```

### Debug Commands

```bash
# Get detailed cluster information
kubectl cluster-info

# Check namespace resources
kubectl get all -n jmeter

# View service configuration
kubectl get svc -n jmeter

# Check persistent volumes
kubectl get pv,pvc -n jmeter
```

## Cleanup

### Remove All Resources

```bash
# Delete all resources in the jmeter namespace
kubectl delete namespace jmeter

# Delete the k3d cluster
k3d cluster delete jmeter-cluster

# Remove local images
docker rmi jmeter-custom yemax/jmeter-custom:1.0.1
```

### Clean Up Docker Resources

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused networks
docker network prune
```

## Next Steps

After mastering Kubernetes deployment, explore:

1. **05_Jenkins/**: Automated test execution with CI/CD
2. **06_AI_report_generation/**: Automated reporting with AI
3. **Production Deployment**: Multi-node clusters and high availability
4. **Advanced Monitoring**: Prometheus, AlertManager, and custom dashboards

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [k3d Documentation](https://k3d.io/)
- [JMeter Distributed Testing Guide](https://jmeter.apache.org/usermanual/remote-test.html)
- [InfluxDB Kubernetes Operator](https://github.com/influxdata/influxdb-operator)
- [Grafana Kubernetes Deployment](https://grafana.com/docs/grafana/latest/installation/kubernetes/)

---

**Note**: This Kubernetes setup provides production-grade orchestration for distributed JMeter testing. For production environments, consider using managed Kubernetes services like EKS, GKE, or AKS for better reliability and scalability.
