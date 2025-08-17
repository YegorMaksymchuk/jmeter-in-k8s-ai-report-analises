# Local JMeter Setup and Testing

This directory contains a complete local JMeter setup for learning and testing Apache JMeter fundamentals. It provides a ready-to-use environment with pre-configured test plans and sample data.

##  Directory Structure

```
01_jmeter_local/
├── JMETER_HOME/          # Complete JMeter installation (v5.6.3)
│   ├── bin/              # JMeter executables and scripts
│   ├── lib/              # JMeter libraries and dependencies
│   ├── docs/             # JMeter documentation
│   ├── extras/           # Additional tools and utilities
│   └── licenses/         # License files
├── test/                 # Test files and data
│   ├── test.jmx          # Sample JMeter test plan
│   └── user.csv          # Test data for user creation
├── run_jmeter.sh         # Script to run JMeter in non-GUI mode
├── run_jmeter_gui.sh     # Script to run JMeter GUI
├── jmeter.log            # JMeter execution logs
└── README.md             # This file
```

##  What You'll Learn

This local setup will teach you:
- **Basic JMeter Concepts**: Understanding test plans, thread groups, and samplers
- **Test Data Management**: Using CSV files for parameterized testing
- **HTTP Request Testing**: Making API calls and handling responses
- **Test Execution**: Running tests in both GUI and non-GUI modes
- **Result Analysis**: Understanding JMeter test results and logs

##  Quick Start

### Prerequisites

- **Java 8 or higher** installed on your system
- Basic understanding of HTTP requests and APIs
- No Docker or Kubernetes required (this is purely local)

### Running JMeter

#### Option 1: GUI Mode (Recommended for Learning)

```bash
# Make the script executable
chmod +x run_jmeter_gui.sh

# Run JMeter GUI
./run_jmeter_gui.sh
```

This will open the JMeter GUI where you can:
- View and modify the test plan
- See real-time test execution
- Analyze results visually
- Debug test issues

#### Option 2: Non-GUI Mode (Command Line)

```bash
# Make the script executable
chmod +x run_jmeter.sh

# Run JMeter in non-GUI mode
./run_jmeter.sh
```

This will execute the test plan and generate results without opening the GUI.

##  Test Plan Overview

### Test Scenario: User Creation API

The included test plan (`test.jmx`) demonstrates testing a user creation API endpoint:

- **Target**: PetStore API (`https://petstore.swagger.io/v2/user`)
- **Method**: POST
- **Purpose**: Create users with test data
- **Load Profile**: Configurable thread count, ramp-up, and duration

### Test Components

#### 1. CSV Data Set Config
- **File**: `user.csv`
- **Variables**: username, firstName, lastName, email, password, phone
- **Behavior**: Recycles data for continuous testing

#### 2. HTTP Header Manager
- **Content-Type**: `application/json`
- **Accept**: `application/json`

#### 3. Thread Group
- **Threads**: Configurable via parameter (default: 100)
- **Ramp-up**: Configurable via parameter (default: 10 seconds)
- **Duration**: Configurable via parameter (default: 3600 seconds)
- **Loop Count**: Configurable via parameter (default: infinite)

#### 4. HTTP Request Sampler
- **Name**: "Created User"
- **Protocol**: HTTPS
- **Domain**: petstore.swagger.io
- **Path**: /v2/user
- **Method**: POST
- **Body**: JSON payload with user data from CSV

##  Configuration

### Environment Variables

You can customize the test execution using JMeter properties:

```bash
# Example: Run with custom parameters
java -jar ./JMETER_HOME/bin/ApacheJMeter.jar \
  -n \
  -t ./test/test.jmx \
  -l ./results/test.jtl \
  -Jthreads=50 \
  -Jrampup=30 \
  -Jduration=1800 \
  -Jiterations=10
```

### Available Parameters

- `threads`: Number of concurrent users (default: 100)
- `rampup`: Time to start all threads (default: 10 seconds)
- `duration`: Test duration in seconds (default: 3600)
- `iterations`: Number of iterations per thread (default: -1 for infinite)

### Test Data

The `user.csv` file contains 361 rows of test user data with the following structure:

```csv
username,firstName,lastName,email,password,phone
user_nccqgf,Emily,Miller,emily.miller@yahoo.com,Qd9HASL3tKFm,+13667529404
user_qoqlhj,Robert,Brown,robert.brown@gmail.com,Mbo0TsmaqxNe,+15737769653
...
```

##  Understanding Results

### Test Execution Output

When running in non-GUI mode, you'll see output like:

```
Creating summariser <summary>
Created the tree successfully using ./test/test.jmx
Starting standalone test @ 2025-01-15 10:30:00 UTC
Waiting for possible shutdown message on port 4445
summary +      1 in     0.1s =    7.7/s Avg:   125 Min:   125 Max:   125 Err:     0 (0.00%)
summary +     99 in     9.9s =   10.0/s Avg:   245 Min:   125 Max:   456 Err:     0 (0.00%)
summary =    100 in    10.0s =   10.0/s Avg:   244 Min:   125 Max:   456 Err:     0 (0.00%)
```

### Result Files

- **test.jtl**: JMeter test results in XML format
- **jmeter.log**: Detailed execution logs
- **results/**: Directory for generated reports (if using -e -o flags)

##  Customization

### Adding New Test Cases

1. Open the test plan in GUI mode
2. Add new HTTP Request samplers
3. Configure request parameters
4. Save the test plan

### Modifying Test Data

1. Edit `user.csv` to add/modify test data
2. Update variable names in CSV Data Set Config if needed
3. Ensure data format matches expected structure

### Creating Custom Test Plans

1. Start with the existing test plan as a template
2. Add new thread groups for different scenarios
3. Configure listeners for result collection
4. Save as new `.jmx` file

##  Troubleshooting

### Common Issues

1. **Java Not Found**
   ```bash
   # Check Java installation
   java -version
   
   # Set JAVA_HOME if needed
   export JAVA_HOME=/path/to/java
   ```

2. **Permission Denied**
   ```bash
   # Make scripts executable
   chmod +x run_jmeter.sh run_jmeter_gui.sh
   ```

3. **Test Data Issues**
   - Verify CSV file format
   - Check variable names in CSV Data Set Config
   - Ensure file path is correct

4. **Network Issues**
   - Check internet connectivity
   - Verify target API is accessible
   - Review firewall settings

### Debug Commands

```bash
# Check JMeter version
java -jar ./JMETER_HOME/bin/ApacheJMeter.jar --version

# Run with debug logging
java -jar ./JMETER_HOME/bin/ApacheJMeter.jar -n -t ./test/test.jmx -l ./results/test.jtl -L DEBUG

# Generate HTML report
java -jar ./JMETER_HOME/bin/ApacheJMeter.jar -n -t ./test/test.jmx -l ./results/test.jtl -e -o ./results/report/
```

##  Next Steps

After mastering this local setup, explore:

1. **02_docker/**: Learn distributed testing with Docker
2. **03_docker-compose/**: Understand container orchestration
3. **04_Kubernetes/**: Deploy in production environments
4. **05_Jenkins/**: Automate test execution
5. **06_AI_report_generation/**: Generate automated reports

##  Contributing

Feel free to:
- Add new test scenarios
- Improve test data
- Enhance documentation
- Report issues or suggest improvements


---

**Note**: This local setup is perfect for learning JMeter fundamentals. For production testing, consider using the distributed setups in other directories.
