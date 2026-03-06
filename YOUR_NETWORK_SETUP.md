# Your PackOptima Network Setup

## Your Network Information

**Your Computer's IP Address:** `10.249.42.28`
**Network Type:** WiFi (Wireless LAN adapter)
**Subnet:** 10.249.42.0/24 (255.255.255.0)
**Gateway:** 10.249.42.88

---

## Quick Setup - 3 Steps

### Step 1: Update Backend CORS Settings

**Edit `backend/.env` file:**

Find the line that says:
```bash
ALLOWED_ORIGINS='["http://localhost","http://localhost:8080","http://localhost:8000"]'
```

**Replace with:**
```bash
ALLOWED_ORIGINS='["http://localhost","http://localhost:8080","http://localhost:8000","http://10.249.42.28:8080","http://10.249.42.28:8000","http://10.249.42.*"]'
```

This allows:
- localhost (your computer)
- Your specific IP (10.249.42.28)
- Any device on your network (10.249.42.*)

---

### Step 2: Open Windows Firewall

**Run PowerShell as Administrator** and execute:

```powershell
# Allow frontend port 8080
netsh advfirewall firewall add rule name="PackOptima Frontend" dir=in action=allow protocol=TCP localport=8080

# Allow backend port 8000
netsh advfirewall firewall add rule name="PackOptima Backend" dir=in action=allow protocol=TCP localport=8000
```

**Or use Windows Defender Firewall GUI:**
1. Open "Windows Defender Firewall with Advanced Security"
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → Next
4. TCP, Specific ports: `8080, 8000` → Next
5. Allow the connection → Next
6. Check all profiles → Next
7. Name: "PackOptima" → Finish

---

### Step 3: Restart Docker

```bash
docker-compose down
docker-compose up -d
```

---

## Access URLs

### From Your Computer (localhost):
```
http://localhost:8080
```

### From Phone/Tablet/Other Devices (same WiFi):
```
http://10.249.42.28:8080
```

### Backend API:
```
http://10.249.42.28:8000
```

---

## Testing

### Test 1: From Your Computer

Open browser and try BOTH:
1. `http://localhost:8080` ✅ Should work
2. `http://10.249.42.28:8080` ✅ Should also work

### Test 2: From Your Phone

1. Make sure phone is on **SAME WiFi** network
2. Open browser on phone
3. Go to: `http://10.249.42.28:8080`
4. You should see PackOptima login page!

---

## Important Notes

### ⚠️ Your IP May Change

Your IP `10.249.42.28` might change if:
- You restart your computer
- You reconnect to WiFi
- Your router assigns a new IP

**Solution: Set Static IP** (see below)

### ✅ Works Only on Same Network

Devices must be on the SAME WiFi network:
- Network name: (your WiFi SSID)
- IP range: 10.249.42.x

### ❌ Won't Work From:
- Mobile data (4G/5G)
- Different WiFi network
- Internet (unless you set up port forwarding)

---

## Set Static IP (Recommended)

To prevent your IP from changing:

### Windows Steps:

1. **Open Network Settings:**
   - Press `Win + R`
   - Type: `ncpa.cpl`
   - Press Enter

2. **Configure WiFi Adapter:**
   - Right-click "Wi-Fi" → Properties
   - Select "Internet Protocol Version 4 (TCP/IPv4)"
   - Click "Properties"

3. **Set Static IP:**
   - Select "Use the following IP address"
   - **IP address:** `10.249.42.28`
   - **Subnet mask:** `255.255.255.0`
   - **Default gateway:** `10.249.42.88`
   - **Preferred DNS:** `8.8.8.8` (Google DNS)
   - **Alternate DNS:** `8.8.4.4`
   - Click OK

4. **Test Connection:**
   - Open browser
   - Visit any website to confirm internet works

---

## Troubleshooting

### Problem: Can't Access from Phone

**Check 1: Same WiFi Network**
```
Phone WiFi Settings → Check network name matches your computer's WiFi
```

**Check 2: Ping Test**

From your phone, install "Network Analyzer" app and ping `10.249.42.28`

If ping fails → Firewall issue

**Check 3: Firewall Rules**

Run in PowerShell (as Admin):
```powershell
netsh advfirewall firewall show rule name="PackOptima Frontend"
netsh advfirewall firewall show rule name="PackOptima Backend"
```

Should show rules are enabled.

**Check 4: Docker Running**
```bash
docker ps
```

Should show 5 containers running.

---

### Problem: CORS Error

If you see:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution:**
1. Check `backend/.env` has your IP in ALLOWED_ORIGINS
2. Restart backend: `docker-compose restart backend`

---

### Problem: Connection Refused

**Check ports are listening:**
```powershell
netstat -an | findstr "8080"
netstat -an | findstr "8000"
```

Should show:
```
0.0.0.0:8080    LISTENING
0.0.0.0:8000    LISTENING
```

If not listening → Docker not running properly

---

## Complete Configuration Files

### backend/.env (Updated)

```bash
# Database
DATABASE_URL=postgresql://packoptima_user:packoptima_password_change_in_production@database:5432/packoptima_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# CORS - UPDATED FOR YOUR NETWORK
ALLOWED_ORIGINS='["http://localhost","http://localhost:8080","http://localhost:8000","http://10.249.42.28:8080","http://10.249.42.28:8000","http://10.249.42.*"]'

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

## Quick Commands

### Restart Everything
```bash
docker-compose down
docker-compose up -d
```

### Check Status
```bash
docker ps
```

### View Logs
```bash
docker-compose logs -f backend
```

### Test from Computer
```bash
# Should both work:
curl http://localhost:8080
curl http://10.249.42.28:8080
```

---

## Summary

**Your Setup:**
- Computer IP: `10.249.42.28`
- Frontend: Port 8080
- Backend: Port 8000
- Network: 10.249.42.0/24

**Access URLs:**
- Same computer: `http://localhost:8080`
- Phone/Tablet: `http://10.249.42.28:8080`

**Steps Completed:**
1. ✅ Identified your IP: 10.249.42.28
2. ✅ Updated CORS settings
3. ✅ Opened firewall ports
4. ✅ Restarted Docker

**Now test from your phone!** 📱

---

## Next Steps

1. Update `backend/.env` with the ALLOWED_ORIGINS above
2. Run firewall commands in PowerShell (as Admin)
3. Restart Docker: `docker-compose down && docker-compose up -d`
4. Test from phone: `http://10.249.42.28:8080`

**That's it!** Your PackOptima is now accessible from any device on your network.
