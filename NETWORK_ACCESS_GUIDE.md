# Access PackOptima from Any Device on Your Network

## What You Want

Access your PackOptima frontend from:
- Your phone
- Your tablet  
- Other computers on the same WiFi/network
- Any device connected to your local network

Instead of just: `http://localhost:3000`

---

## Quick Solution

### Step 1: Find Your Computer's IP Address

**Windows:**
```powershell
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually starts with 192.168.x.x or 10.0.x.x)

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```

Example output:
```
IPv4 Address: 192.168.1.100
```

### Step 2: Update Docker Compose

<function_calls>
<invoke name="readFile">
<parameter name="explanation">Reading docker-compose.yml to show how to expose ports for network access