# Jenkins CI/CD Integration for Automated JMeter Testing

This directory demonstrates how to integrate Jenkins with Kubernetes to automate distributed JMeter testing. Jenkins provides a robust CI/CD platform for scheduling, executing, and monitoring performance tests with full integration to your Kubernetes cluster.

## What You'll Learn

- **Jenkins Installation**: Setting up Jenkins in Kubernetes or standalone
- **Kubernetes Integration**: Connecting Jenkins to your K8s cluster
- **Automated Test Execution**: Scheduling and running JMeter tests
- **Dynamic Scaling**: Automatic pod scaling based on test requirements
- **Result Management**: Automated result collection and reporting
- **Cross-Platform Scripting**: Bash and PowerShell automation scripts
- **CI/CD Pipeline**: Integration with development workflows

## Quick Start

### Prerequisites

- **Kubernetes Cluster**: Running k3d or any K8s cluster
- **kubectl**: Configured to access your cluster
- **Docker**: For Jenkins container deployment
- **JMeter Infrastructure**: Deployed from `04_Kubernetes/` directory

## Jenkins Installation Options

### Option 1: Jenkins in Kubernetes (Recommended)

Deploy Jenkins directly in your Kubernetes cluster for seamless integration.

#### Step 1: Create Jenkins Namespace

```bash
# Create dedicated namespace for Jenkins
kubectl create namespace jenkins
```

#### Step 2: Deploy Jenkins with Persistent Storage

```yaml
# jenkins-deployment.yml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins-admin
  namespace: jenkins
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: jenkins-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: jenkins-admin
  namespace: jenkins
---
apiVersion: v1
kind: Service
metadata:
  name: jenkins
  namespace: jenkins
spec:
  type: NodePort
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080
  selector:
    app: jenkins
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      serviceAccountName: jenkins-admin
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
        - name: docker-sock
          mountPath: /var/run/docker.sock
      volumes:
      - name: jenkins-home
        persistentVolumeClaim:
          claimName: jenkins-pvc
      - name: docker-sock
        hostPath:
          path: /var/run/docker.sock
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Deploy Jenkins:

```bash
# Apply Jenkins deployment
kubectl apply -f jenkins-deployment.yml

# Check deployment status
kubectl get pods -n jenkins
kubectl get svc -n jenkins
```

#### Step 3: Access Jenkins

```bash
# Port forward to access Jenkins
kubectl port-forward -n jenkins svc/jenkins 8080:8080
```

Access Jenkins at http://localhost:8080

### Option 2: Standalone Jenkins Installation

Install Jenkins on your local machine or server.

#### Windows Installation

```powershell
# Using Chocolatey
choco install jenkins

# Or download from https://jenkins.io/download/
# Run as Windows service
```

#### macOS Installation

```bash
# Using Homebrew
brew install jenkins

# Start Jenkins service
brew services start jenkins
```

#### Linux Installation

```bash
# Ubuntu/Debian
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins

# Start Jenkins service
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

## Jenkins Configuration

### Step 1: Initial Setup

1. **Access Jenkins**: Open http://localhost:8080
2. **Get Initial Password**:
   ```bash
   # Kubernetes deployment
   kubectl exec -n jenkins $(kubectl get pods -n jenkins -l app=jenkins -o jsonpath='{.items[0].metadata.name}') -- cat /var/jenkins_home/secrets/initialAdminPassword
   
   # Standalone installation
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```

3. **Install Suggested Plugins**
4. **Create Admin User**

### Step 2: Install Required Plugins

Navigate to **Manage Jenkins** → **Manage Plugins** → **Available** and install:

- **Kubernetes Plugin**: For K8s integration
- **Pipeline**: For declarative pipelines
- **Git**: For source code integration
- **Credentials Binding**: For secure credential management
- **Workspace Cleanup**: For cleanup after builds

### Step 3: Configure Kubernetes Cloud

1. **Navigate to**: Manage Jenkins → Manage Nodes and Clouds → Configure Clouds
2. **Add Cloud**: Select "Kubernetes"
3. **Configure Connection**:
   - **Kubernetes URL**: `https://kubernetes.default.svc`
   - **Jenkins URL**: `http://jenkins.jenkins.svc.cluster.local:8080`
   - **Jenkins tunnel**: `jenkins.jenkins.svc.cluster.local:50000`

4. **Add Pod Template**:
   - **Name**: `jmeter-slave`
   - **Labels**: `jmeter-slave`
   - **Containers**:
     - **Name**: `jmeter`
     - **Docker image**: `yemax/jmeter-custom:1.0.1`
     - **Command**: `/docker-entrypoint.sh`
     - **Args**: `server`

## Creating Jenkins Jobs

### Option 1: Freestyle Project

#### Step 1: Create New Job

1. **Click**: "New Item"
2. **Enter name**: `JMeter-Performance-Test`
3. **Select**: "Freestyle project"
4. **Click**: "OK"

#### Step 2: Configure Job

**General Settings:**
- **Description**: "Automated JMeter performance testing with Kubernetes"
- **Discard old builds**: Keep last 10 builds

**Build Triggers:**
- **Poll SCM**: `H/15 * * * *` (every 15 minutes)
- **Build periodically**: `0 2 * * *` (daily at 2 AM)

**Build Environment:**
- **Delete workspace before build starts**
- **Add timestamps to console output**

**Build Steps:**

**Step 1: Scale JMeter Master**
```bash
# Scale JMeter master to 1 replica
kubectl scale deployment jmeter-master -n jmeter --replicas=1
echo "Scaling jmeter-master to 1 replica..."

# Wait for pod to be ready
while true; do
    sleep 2
    readyReplicas=$(kubectl get deployment jmeter-master -n jmeter -o json | jq -r '.status.readyReplicas // 0')
    echo "Ready replicas: $readyReplicas / 1"
    if [ "$readyReplicas" -ge "1" ]; then
        break
    fi
done
echo "JMeter master is ready!"
```

**Step 2: Scale JMeter Slaves**
```bash
# Scale JMeter slaves to 4 replicas
kubectl scale deployment jmeter-slave -n jmeter --replicas=4
echo "Scaling jmeter-slave to 4 replicas..."

# Wait for pods to be ready
while true; do
    sleep 2
    readyReplicas=$(kubectl get deployment jmeter-slave -n jmeter -o json | jq -r '.status.readyReplicas // 0')
    echo "Ready replicas: $readyReplicas / 4"
    if [ "$readyReplicas" -ge "4" ]; then
        break
    fi
done
echo "JMeter slaves are ready!"
```

**Step 3: Execute JMeter Test**
```bash
# Record test start time
testStartTime=$(date)
testStartTimeGrafanaLink=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# Get slave pod IPs
ips=$(kubectl get pods -n jmeter -l app=jmeter-slave -o jsonpath="{range .items[*]}{.status.podIP}{'\n'}{end}" | tr '\n' ',' | sed 's/,$//')

# Get master pod name
JMETER_MASTER_POD=$(kubectl get po -n jmeter -l app=jmeter-master -o jsonpath="{.items[0].metadata.name}")

# Execute test
kubectl -n jmeter exec -it $JMETER_MASTER_POD -- jmeter -n -t ./test/test.jmx -R $ips

# Record test end time
testEndTime=$(date)
testEndTimeGrafanaLink=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# Calculate duration
start_epoch=$(date -d "$testStartTime" +%s)
end_epoch=$(date -d "$testEndTime" +%s)
duration=$(echo "scale=2; $end_epoch - $start_epoch" | bc)

# Generate Grafana URL
grafanaUrl="http://localhost:3000/d/3e682b4e-3144-4434-9c30-4bc0c856b26f/jmeter-dashboard?orgId=1&timezone=browser&var-data_source=beq056f1s8lq8a&var-application=test&var-transaction=Created%20User&refresh=5s&from=$testStartTimeGrafanaLink&to=$testEndTimeGrafanaLink"

echo "Test completed in $duration seconds"
echo "Grafana Dashboard: $grafanaUrl"
```

**Post-build Actions:**
- **Archive the artifacts**: `**/*.jtl`
- **Publish JUnit test result report**: `**/test-results/*.xml`
- **Send email notification** (configure recipients)

### Option 2: Using Provided Scripts

#### Using Bash Script (Linux/macOS)

1. **Upload Script**: Copy `jenkins_job.sh` to Jenkins workspace
2. **Make Executable**: `chmod +x jenkins_job.sh`
3. **Execute Script**: Add build step to run `./jenkins_job.sh`

#### Using PowerShell Script (Windows)

1. **Upload Script**: Copy `jenkins_job.ps1` to Jenkins workspace
2. **Execute Script**: Add PowerShell build step to run `.\jenkins_job.ps1`

## Script Analysis

### Bash Script (`jenkins_job.sh`)

The script performs the following automated steps:

1. **Scale JMeter Master**: Scales master deployment to 1 replica
2. **Wait for Master**: Polls until master pod is ready
3. **Scale JMeter Slaves**: Scales slave deployment to 4 replicas
4. **Wait for Slaves**: Polls until all slave pods are ready
5. **Execute Test**: Runs JMeter test with distributed slaves
6. **Generate Reports**: Creates Grafana URLs and stores results in InfluxDB

**Key Features:**
- **Dynamic Scaling**: Automatically scales pods based on requirements
- **Health Checks**: Waits for pods to be ready before proceeding
- **Result Tracking**: Records test timing and generates Grafana links
- **Data Persistence**: Stores test results in InfluxDB for historical analysis

### PowerShell Script (`jenkins_job.ps1`)

The PowerShell version provides the same functionality with Windows-specific syntax:

1. **PowerShell Loops**: Uses `do-while` loops for polling
2. **JSON Parsing**: Uses `ConvertFrom-Json` for status checking
3. **Date Handling**: Uses PowerShell date formatting
4. **String Manipulation**: Uses PowerShell string operations

## Advanced Configuration

### Parameterized Builds

Configure Jenkins job to accept parameters:

1. **Check**: "This project is parameterized"
2. **Add Parameters**:
   - **String Parameter**: `SLAVE_COUNT` (default: 4)
   - **String Parameter**: `TEST_DURATION` (default: 3600)
   - **String Parameter**: `THREAD_COUNT` (default: 100)
   - **Choice Parameter**: `TEST_ENVIRONMENT` (choices: dev, staging, prod)

3. **Update Scripts**: Use parameters in your build scripts:
   ```bash
   kubectl scale deployment jmeter-slave -n jmeter --replicas=$SLAVE_COUNT
   ```

### Pipeline as Code

Create a `Jenkinsfile` for declarative pipeline:

```groovy
pipeline {
    agent any
    
    parameters {
        string(name: 'SLAVE_COUNT', defaultValue: '4', description: 'Number of JMeter slave pods')
        string(name: 'TEST_DURATION', defaultValue: '3600', description: 'Test duration in seconds')
        string(name: 'THREAD_COUNT', defaultValue: '100', description: 'Number of threads')
    }
    
    stages {
        stage('Scale Infrastructure') {
            steps {
                script {
                    // Scale JMeter master
                    sh 'kubectl scale deployment jmeter-master -n jmeter --replicas=1'
                    
                    // Wait for master
                    sh '''
                        while true; do
                            sleep 2
                            readyReplicas=$(kubectl get deployment jmeter-master -n jmeter -o json | jq -r '.status.readyReplicas // 0')
                            echo "Ready replicas: $readyReplicas / 1"
                            if [ "$readyReplicas" -ge "1" ]; then
                                break
                            fi
                        done
                    '''
                    
                    // Scale JMeter slaves
                    sh "kubectl scale deployment jmeter-slave -n jmeter --replicas=${params.SLAVE_COUNT}"
                    
                    // Wait for slaves
                    sh '''
                        while true; do
                            sleep 2
                            readyReplicas=$(kubectl get deployment jmeter-slave -n jmeter -o json | jq -r '.status.readyReplicas // 0')
                            echo "Ready replicas: $readyReplicas / $SLAVE_COUNT"
                            if [ "$readyReplicas" -ge "$SLAVE_COUNT" ]; then
                                break
                            fi
                        done
                    '''
                }
            }
        }
        
        stage('Execute Test') {
            steps {
                script {
                    // Execute JMeter test
                    sh '''
                        ips=$(kubectl get pods -n jmeter -l app=jmeter-slave -o jsonpath="{range .items[*]}{.status.podIP}{'\n'}{end}" | tr '\n' ',' | sed 's/,$//')
                        JMETER_MASTER_POD=$(kubectl get po -n jmeter -l app=jmeter-master -o jsonpath="{.items[0].metadata.name}")
                        kubectl -n jmeter exec -it $JMETER_MASTER_POD -- jmeter -n -t ./test/test.jmx -R $ips -Jthreads=$THREAD_COUNT -Jduration=$TEST_DURATION
                    '''
                }
            }
        }
        
        stage('Generate Report') {
            steps {
                script {
                    // Generate Grafana URL and store results
                    sh './jenkins_job.sh'
                }
            }
        }
    }
    
    post {
        always {
            // Cleanup
            sh 'kubectl scale deployment jmeter-master -n jmeter --replicas=0'
            sh 'kubectl scale deployment jmeter-slave -n jmeter --replicas=0'
        }
        success {
            echo 'Performance test completed successfully!'
        }
        failure {
            echo 'Performance test failed!'
        }
    }
}
```

## Monitoring and Notifications

### Email Notifications

Configure email notifications in Jenkins:

1. **Manage Jenkins** → **Configure System**
2. **Extended E-mail Notification**:
   - **SMTP server**: Your SMTP server
   - **Default Recipients**: `team@company.com`
   - **Default Subject**: `[Jenkins] ${BUILD_STATUS}: Job '${BUILD_JOB_NAME}' [${BUILD_NUMBER}]`

### Slack Integration

1. **Install**: Slack Notification Plugin
2. **Configure**: Slack workspace and channel
3. **Add**: Post-build action to send Slack notifications

### Grafana Integration

The scripts automatically generate Grafana URLs for test results:

```bash
# Example Grafana URL generated by scripts
http://localhost:3000/d/3e682b4e-3144-4434-9c30-4bc0c856b26f/jmeter-dashboard?orgId=1&timezone=browser&var-data_source=beq056f1s8lq8a&var-application=test&var-transaction=Created%20User&refresh=5s&from=2025-01-15T10:30:00.000Z&to=2025-01-15T10:35:00.000Z
```

## Troubleshooting

### Common Issues

1. **Jenkins Cannot Connect to Kubernetes**
   ```bash
   # Check cluster access
   kubectl cluster-info
   
   # Verify service account
   kubectl get serviceaccount jenkins-admin -n jenkins
   ```

2. **Pods Not Scaling**
   ```bash
   # Check deployment status
   kubectl get deployments -n jmeter
   
   # Check pod events
   kubectl describe pods -n jmeter
   ```

3. **Test Execution Fails**
   ```bash
   # Check JMeter master logs
   kubectl logs -n jmeter $(kubectl get pods -n jmeter -l app=jmeter-master -o jsonpath='{.items[0].metadata.name}')
   
   # Check JMeter slave logs
   kubectl logs -n jmeter $(kubectl get pods -n jmeter -l app=jmeter-slave -o jsonpath='{.items[0].metadata.name}')
   ```

### Debug Commands

```bash
# Check Jenkins pod status
kubectl get pods -n jenkins

# View Jenkins logs
kubectl logs -n jenkins $(kubectl get pods -n jenkins -l app=jenkins -o jsonpath='{.items[0].metadata.name}')

# Check JMeter infrastructure
kubectl get all -n jmeter

# Test Kubernetes connectivity from Jenkins
kubectl exec -n jenkins $(kubectl get pods -n jenkins -l app=jenkins -o jsonpath='{.items[0].metadata.name}') -- kubectl get pods -n jmeter
```

## Cleanup

### Remove Jenkins Resources

```bash
# Delete Jenkins namespace (removes all resources)
kubectl delete namespace jenkins

# Remove Jenkins service (standalone installation)
sudo systemctl stop jenkins
sudo systemctl disable jenkins
sudo apt-get remove jenkins  # Ubuntu/Debian
```

## Next Steps

After mastering Jenkins integration, explore:

1. **06_AI_report_generation/**: Automated reporting with AI
2. **Advanced Pipelines**: Multi-stage CI/CD workflows
3. **Infrastructure as Code**: Terraform/Ansible for infrastructure
4. **Monitoring Stack**: Prometheus, AlertManager, and custom dashboards

## Additional Resources

- [Jenkins Documentation](https://jenkins.io/doc/)
- [Jenkins Kubernetes Plugin](https://github.com/jenkinsci/kubernetes-plugin)
- [Jenkins Pipeline Syntax](https://jenkins.io/doc/book/pipeline/syntax/)
- [JMeter Jenkins Integration](https://jmeter.apache.org/usermanual/jmeter_distributed_testing_step_by_step.html)
- [Kubernetes Jenkins Integration](https://kubernetes.io/docs/tasks/jenkins/)

---

**Note**: This Jenkins setup provides automated CI/CD capabilities for distributed JMeter testing. For production environments, consider using Jenkins X or Tekton for cloud-native CI/CD workflows.
