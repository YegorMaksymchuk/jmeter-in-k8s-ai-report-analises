# AI-Powered Automated Report Generation with Grafana MCP and Playwright MCP

This directory demonstrates how to integrate Grafana MCP (Model Context Protocol) and Playwright MCP with Cursor IDE to automatically access JMeter test dashboards, capture screenshots, and generate comprehensive performance test reports using AI.

## What You'll Learn

- **MCP Integration**: Understanding Model Context Protocol with Cursor IDE
- **Grafana MCP**: Automated dashboard access and data extraction
- **Playwright MCP**: Automated screenshot capture and browser automation
- **AI Report Generation**: Using AI to analyze and generate test reports
- **Automated Workflows**: End-to-end report generation pipeline
- **Cursor IDE Integration**: Leveraging AI capabilities for testing automation

## Quick Start

### Prerequisites

- **Cursor IDE**: Latest version with MCP support
- **Grafana Instance**: Running with JMeter dashboard
- **InfluxDB**: Populated with JMeter test data
- **Kubernetes Cluster**: Running JMeter infrastructure
- **Python**: For MCP server implementations
- **Node.js**: For Playwright automation

## MCP (Model Context Protocol) Overview

MCP is a protocol that enables AI assistants to interact with external data sources and tools. In this setup, we use:

- **Grafana MCP**: Connects to Grafana dashboards to extract metrics and data
- **Playwright MCP**: Automates browser interactions and screenshot capture
- **Cursor IDE**: Provides the AI interface and orchestrates the workflow

## Installation and Setup

### Step 1: Install Cursor IDE

Download and install Cursor IDE from [cursor.sh](https://cursor.sh/):

```bash
# macOS
brew install --cask cursor

# Windows
# Download from https://cursor.sh/

# Linux
# Download from https://cursor.sh/
```

### Step 2: Install MCP Servers

#### Install Grafana MCP Server

```bash
# Clone the Grafana MCP server repository
git clone https://github.com/grafana/grafana-mcp-server.git
cd grafana-mcp-server

# Install dependencies
npm install

# Build the server
npm run build

# Install globally
npm install -g .
```

#### Install Playwright MCP Server

```bash
# Install Playwright MCP server
npm install -g @modelcontextprotocol/server-playwright

# Install Playwright browsers
npx playwright install
```

### Step 3: Configure MCP in Cursor IDE

1. **Open Cursor IDE**
2. **Navigate to Settings**: `Cmd/Ctrl + ,`
3. **Search for "MCP"**
4. **Add MCP Servers**:

### Step 4: Run Agent with prompt
1. **Modify text from ./report-prompt.md
2. **Ask agent to generate report and past prompt to chat 
3. **Enjoy result
