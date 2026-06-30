# VulnBot MCP Tool Deployment Guide

## Overview

VulnBot ships with 4 MCP services: 2 local implementations that work out of the box, and 2 that require deploying an external service.

| Service | Mode | Status | Purpose |
|---|---|---|---|
| fetch | Local (httpx) | Works out of the box | HTTP requests / API testing |
| memory | Local (JSON) | Works out of the box | Cross-session memory persistence |
| chrome-devtools | stdio MCP | Requires deployment | Browser automation / JS execution / screenshots |
| burp | stdio MCP | Requires deployment | Traffic capture / replay / HTTP interception (replaces Yakit) |

---

## 1. Chrome DevTools MCP

### Repository
https://github.com/ChromeDevTools/chrome-devtools-mcp

### Prerequisites
- Node.js LTS (v20+)
- Chrome browser (Stable or Chrome for Testing)
- ffmpeg (optional, required for the screencast feature)

### Installation
No manual installation required — VulnBot's configuration already uses `npx -y chrome-devtools-mcp@latest` to fetch it automatically.

### Start Chrome remote debugging
```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\tmp\chrome-debug

# Linux/Mac
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

### VulnBot Configuration
Edit `~/.vulnbot/config.yaml`:
```yaml
mcp:
  servers:
    chrome-devtools:
      enabled: true
      transport:
        type: stdio
        command: npx
        args:
          - "-y"
          - "chrome-devtools-mcp@latest"
          - "--browser-url=http://127.0.0.1:9222"
```

Or via the CLI:
```bash
vulnbot config set mcp.servers.chrome-devtools.enabled true
```

### Capabilities Provided (31+ tools)
- **Input automation**: clicks, drag-and-drop, form filling, dialog handling
- **Navigation**: page management, URL navigation, element waiting
- **Performance analysis**: trace recording, Google CrUX integration
- **Network**: request monitoring, network interception
- **Debugging**: screenshots, console logs, Lighthouse audits
- **Memory**: heap snapshot analysis
- **Emulation**: device/viewport emulation

### Penetration Testing Scenarios
- Visit target pages and capture screenshots as evidence
- Execute JS to detect DOM XSS
- Monitor network requests to discover API endpoints
- Automate form interactions to test CSRF / auth bypass

---

## 2. Burp Suite MCP (replaces Yakit)

### Repository
https://github.com/PortSwigger/mcp-server

### Prerequisites
- Java (available on PATH, verify with `java --version`)
- Burp Suite Professional (the Community edition has limited functionality)
- `jar` command available

### Installation Steps

#### Step 1: Clone and build
```bash
git clone https://github.com/PortSwigger/mcp-server.git burp-mcp
cd burp-mcp
./gradlew embedProxyJar
# On Windows: gradlew.bat embedProxyJar
# Output: build/libs/burp-mcp-all.jar
```

#### Step 2: Load into Burp Suite
1. Open Burp Suite → the Extensions tab
2. Click Add → select Type: Java
3. Select `build/libs/burp-mcp-all.jar`
4. Click Next to finish loading

#### Step 3: Enable the MCP Server
1. Find the MCP tab in Burp
2. Check "Enabled"
3. Listens on `http://127.0.0.1:9876` by default
4. Optional: change the Host/Port

### VulnBot Configuration

Copy the built JAR to a fixed location:
```bash
# Recommended: place it in VulnBot's tools directory
mkdir -p ~/.vulnbot/tools
cp build/libs/burp-mcp-all.jar ~/.vulnbot/tools/
```

Edit `~/.vulnbot/config.yaml`:
```yaml
mcp:
  servers:
    burp:
      enabled: true
      transport:
        type: stdio
        command: java
        args:
          - "-jar"
          - "~/.vulnbot/tools/burp-mcp-all.jar"
          - "--sse-url"
          - "http://127.0.0.1:9876"
```

### Capabilities Provided
- **Traffic capture**: view requests/responses in the Proxy History
- **Replay**: construct and send custom HTTP requests
- **Interception**: modify requests/responses in real time
- **Scanning**: invoke the Burp Scanner (Pro edition)
- **Intruder**: parameterized attacks

### Comparison with Yakit
| Feature | Yakit | Burp MCP |
|---|---|---|
| MITM capture | MITM hijacking | Proxy History |
| Request replay | Web Fuzzer | send_http1_request |
| Traffic analysis | Traffic analysis | get_proxy_history |
| Vulnerability scanning | Plugin-based scanning | Burp Scanner |
| MCP integration | Not implemented (Issue #2703) | Officially supported in v1.3.0 |

---

## Quick Verification

### Verify Chrome DevTools MCP
```bash
# 1. Start Chrome in debug mode
# 2. Start VulnBot
vulnbot repl

# 3. Enter a test command
> Open http://example.com and take a screenshot
```

### Verify Burp MCP
```bash
# 1. Start Burp Suite and enable the MCP extension
# 2. Start VulnBot
vulnbot repl

# 3. Enter a test command
> View Burp proxy history
```

---

## Troubleshooting

### Can't connect to Chrome DevTools
1. Confirm Chrome remote debugging is running: `curl http://127.0.0.1:9222/json`
2. Confirm Node.js is installed: `node --version`
3. Try running it manually: `npx -y chrome-devtools-mcp@latest --browser-url=http://127.0.0.1:9222`

### Can't connect to Burp MCP
1. Confirm the MCP tab in Burp shows "Enabled"
2. Confirm the port is reachable: `curl http://127.0.0.1:9876`
3. Confirm the Java version: `java --version` (Java 11+ required)
4. Check that the JAR path is correct
