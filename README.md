# JMeter in Kubernetes - Complete Distributed Load Testing Solution

This project provides a comprehensive solution for running Apache JMeter load tests in distributed environments with full observability and automation. It demonstrates how to set up distributed JMeter testing with InfluxDB for metrics storage, Grafana for visualization, and Jenkins for CI/CD automation.

##  Project Overview

This is a complete example demonstrating how to:
- Run JMeter tests locally and in distributed mode
- Set up distributed JMeter testing with Docker networks
- Orchestrate distributed testing with Docker Compose
- Deploy and run distributed JMeter tests in Kubernetes
- Integrate with InfluxDB for metrics collection and Grafana for visualization
- Automate test execution with Jenkins CI/CD
- Generate automated reports using Grafana MCP and Playwright MCP with Cursor IDE
- Leverage AI for automated performance test report generation

## 📁 Project Structure

```
jmeter-in-k8s/
├── 01_jmeter_local/           # Local JMeter setup and execution
│   ├── JMETER_HOME/          # JMeter installation and configuration
│   ├── test/                 # Sample test files
│   ├── run_jmeter.sh         # Script to run JMeter locally
│   └── run_jmeter_gui.sh     # Script to run JMeter GUI
├── 02_docker/                # Docker-based distributed testing
│   ├── Dockerfile            # Custom JMeter Docker image
│   ├── config/               # JMeter configuration files
│   ├── plugins/              # Custom JMeter plugins
│   ├── scripts/              # Docker utility scripts
│   ├── test/                 # Test files for Docker environment
│   └── README.md             # Detailed Docker setup instructions
├── 03_docker-compose/        # Docker Compose orchestration
│   ├── docker-compose.yml    # Multi-container setup
│   └── test/                 # Test files for Docker Compose
├── 04_Kubernetes/            # Kubernetes deployment
│   ├── deployment/           # K8s manifests (namespace, InfluxDB, Grafana)
│   ├── docker/               # Docker files for K8s deployment
│   └── README.md             # Kubernetes setup instructions
├── 05_Jenkins/               # Jenkins CI/CD integration
│   ├── jenkins_job.sh        # Shell script for Jenkins pipeline
│   └── jenkins_job.ps1       # PowerShell script for Jenkins pipeline
└── 06_AI_report_generation/  # AI-powered automated reporting
    └── report-prompt.md      # AI prompt for automated report generation
```

##  Quick Start Guide

### Prerequisites

- **Docker & Docker Compose**: For containerized testing
- **Kubernetes**: k3d for local development or any K8s cluster
- **Jenkins**: For CI/CD automation (optional)
- **JMeter Test Scripts**: Your .jmx test files

### 1. Local JMeter Setup (`01_jmeter_local/`)

Start with local JMeter testing to understand the basics:

```bash
cd 01_jmeter_local
./run_jmeter_gui.sh    # Run JMeter GUI
./run_jmeter.sh        # Run JMeter in non-GUI mode
```

**What you'll learn:**
- Basic JMeter setup and configuration
- How to create and run test plans
- Understanding JMeter test structure

### 2. Docker Distributed Testing (`02_docker/`)

Learn distributed testing using Docker networks:

```bash
cd 02_docker
./build_custom_docker_image.sh
```

**Key Features:**
- Custom JMeter Docker image with plugins
- Distributed testing with master-slave architecture
- Network isolation using Docker networks
- Integration with InfluxDB and Grafana

**What you'll learn:**
- How to create custom JMeter Docker images
- Setting up distributed testing with Docker networks
- Configuring JMeter for metrics collection
- Basic observability with InfluxDB and Grafana

### 3. Docker Compose Orchestration (`03_docker-compose/`)

Simplify distributed testing with Docker Compose:

```bash
cd 03_docker-compose
docker-compose up -d
```

**Key Features:**
- Single command deployment
- Pre-configured networking
- Integrated InfluxDB and Grafana
- Easy scaling of JMeter slaves

**What you'll learn:**
- Container orchestration with Docker Compose
- Service discovery and networking
- Environment variable management
- Simplified distributed testing setup

### 4. Kubernetes Deployment (`04_Kubernetes/`)

Deploy distributed JMeter testing in Kubernetes:

```bash
# Create local cluster with k3d
k3d cluster create jmeter-cluster -p "3000:3000@loadbalancer"

# Deploy components
kubectl apply -f 04_Kubernetes/deployment/01_namespace.yml
kubectl apply -f 04_Kubernetes/deployment/02_influxdb.yml
kubectl apply -f 04_Kubernetes/deployment/03_grafana.yml
```

**Key Features:**
- Production-ready Kubernetes manifests
- Persistent storage for metrics
- Horizontal scaling of JMeter slaves
- Load balancing and service discovery

**What you'll learn:**
- Kubernetes deployment strategies
- ConfigMap and Secret management
- Service and ingress configuration
- Scaling and resource management

### 5. Jenkins CI/CD Integration (`05_Jenkins/`)

Automate test execution with Jenkins:

```bash
# Use the provided Jenkins job scripts
# jenkins_job.sh (Linux/Mac) or jenkins_job.ps1 (Windows)
```

**Key Features:**
- Automated test execution
- Parameterized builds
- Test result collection
- Integration with existing CI/CD pipelines

**What you'll learn:**
- Jenkins pipeline configuration
- Parameterized test execution
- Integration with distributed testing
- Automated reporting

##  Advanced Integrations

### Grafana MCP Integration with Cursor IDE

This project demonstrates how to integrate Grafana MCP (Model Context Protocol) with Cursor IDE for automated reporting:

**Features:**
- Automated dashboard creation
- Real-time metrics visualization
- Custom report generation
- Integration with Playwright MCP for screenshot capture

**Setup:**
1. Install Grafana MCP in Cursor IDE
2. Configure connection to your Grafana instance
3. Use the provided scripts to generate automated reports

### Playwright MCP Integration

Combine Playwright MCP with Grafana MCP for comprehensive reporting:

**Features:**
- Automated screenshot capture of Grafana dashboards
- PDF report generation
- Email distribution of test results
- Integration with CI/CD pipelines

### AI-Powered Automated Reporting (`06_AI_report_generation/`)

Leverage AI to automatically generate comprehensive performance test reports:

**Features:**
- AI-driven report generation using performance test analyst expertise
- Automated Grafana dashboard analysis
- Screenshot capture of all dashboard widgets
- Structured report generation with predefined templates
- Integration with Grafana MCP and Playwright MCP

**Report Structure:**
- Performance Test Summary Report
- Test Scenario Description and Objectives
- Toolchain and Thread Groups Overview
- Load Calculations and Metrics
- Response Time Analysis
- Error Analysis and Bottlenecks
- Performance Recommendations

**Setup:**
1. Use the provided AI prompt in `report-prompt.md`
2. Configure Grafana dashboard URL and credentials
3. Run the AI agent to generate automated reports
4. Integrate with CI/CD pipelines for continuous reporting

##  Monitoring and Observability

### InfluxDB Integration
- **Purpose**: Store JMeter metrics and test results
- **Features**: Time-series database for performance metrics
- **Configuration**: Pre-configured for JMeter metrics collection

### Grafana Dashboards
- **Purpose**: Visualize test results and performance metrics
- **Features**: Real-time dashboards, alerting, custom queries
- **Setup**: Import JMeter dashboard (ID: 4026) or use custom dashboards

### Metrics Collected
- Response times and throughput
- Error rates and status codes
- Resource utilization
- Custom JMeter metrics

##  Configuration and Customization

### JMeter Configuration
- Custom plugins in `*/plugins/` directories
- Configuration files in `*/config/` directories
- Test scripts in `*/test/` directories

### Environment Variables
- `JMETER_MASTER_HOST`: Master node hostname
- `JMETER_SLAVE_COUNT`: Number of slave nodes
- `INFLUXDB_HOST`: InfluxDB connection details
- `GRAFANA_HOST`: Grafana connection details

### Scaling Options
- **Docker**: Scale containers with `docker-compose scale`
- **Kubernetes**: Scale deployments with `kubectl scale`
- **Jenkins**: Parameterized builds for different test scenarios

##  Troubleshooting

### Common Issues
1. **Network Connectivity**: Ensure proper network configuration
2. **Resource Limits**: Monitor CPU and memory usage
3. **Storage**: Check persistent volume claims in Kubernetes
4. **Authentication**: Verify InfluxDB and Grafana credentials

### Debug Commands
```bash
# Docker
docker logs <container-name>
docker exec -it <container-name> /bin/bash

# Kubernetes
kubectl logs <pod-name> -n jmeter
kubectl exec -it <pod-name> -n jmeter -- /bin/bash

# JMeter
jmeter -n -t test.jmx -l results.jtl -e -o report/
```

##  Learning Path

1. **Beginner**: Start with `01_jmeter_local/` to understand JMeter basics
2. **Intermediate**: Move to `02_docker/` for distributed testing concepts
3. **Advanced**: Use `03_docker-compose/` for orchestrated testing
4. **Expert**: Deploy with `04_Kubernetes/` for production environments
5. **Automation**: Integrate with `05_Jenkins/` for CI/CD workflows
6. **AI Integration**: Use `06_AI_report_generation/` for automated reporting

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Apache JMeter community
- InfluxData for InfluxDB
- Grafana Labs for Grafana
- Docker and Kubernetes communities
- Jenkins community for CI/CD automation tools

---

**Note**: This project serves as a comprehensive example and learning resource. Adapt the configurations and scripts according to your specific requirements and infrastructure setup. 