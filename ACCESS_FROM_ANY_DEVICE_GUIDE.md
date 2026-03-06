# Access PackOptima from Any Device on Your Network

Complete guide to access your PackOptima platform from phones, tablets, and other computers on your local network.

---

## Current Situation

Right now, you can only access PackOptima from:
- `http://localhost:3000` (only on the computer running Docker)

## What You Want

Access PackOptima from:
- ✅ Your phone (same WiFi)
- ✅ Your tablet (same WiFi)
- ✅ Other computers (same network)
- ✅ Any device on your local network

---

## Quick Setup (3 Steps)

### Step 1: Find Your Computer's IP Address

Your computer has an IP address on your local network (like 192.168.1.100).

**Windows (PowerShell or CMD):**
```powershell
ipconfig
```

Look for "IPv4 Address" under your WiFi or Ethernet adapter:
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

**Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Linux:**
```bash
hostname -I
# or
ip addr show
```

**Example IP addresses:**
- `192.168.1.100` (most common)
- `192.168.0.100`
- `10.0.0.100`
- `172.16.0.100`

**Write down your IP address:** `_________________`

---

### Step 2: Update Docker Compose (Already Done!)

Your `docker-compose.yml` is already configured correctly:

```yaml
frontend:
  ports:
    - "8080:80"  # ✅ Exposes on all network interfaces

backend:
  ports:
    - "8000:8000"  # ✅ Exposes on all network interfaces
```

This means Docker is listening on `0.0.0.0:8080` (all network interfaces), not just `127.0.0.1:8080` (localhost only).

---

### Step 3: Update Backend CORS Settings

The backend needs to allow requests from your IP address.

**Edit `backend/.env`:**

Find this line:
```bash
ALLOWED_ORIGINS='["http://localhost","http://localhost:8080","http://localhost:8000"]'
```

Change to (replace `192.168.1.100` with YOUR IP):
```bash
ALLOWED_ORIGINS='["http://localhost","http://localhost:8080","http://localhost:8000","http://192.168.1.100:8080","http://192.168.1.100:8000"]'
```

**Or allow all local network IPs (easier but less secure):**
```bash
ALLOWED_ORIGINS='["http://localhost","http://localhost:8080","http://localhost:8000","http://192.168.1.*","http://10.0.0.*"]'
```

---

### Step 4: Restart Docker Containers

```bash
docker-compose down
docker-compose up -d
```

---

### Step 5: Access from Any Device

On your phone, tablet, or other computer (connected to same WiFi):

**Open browser and go to:**
```
http://192.168.1.100:8080
```
(Replace `192.168.1.100` with YOUR computer's IP address)

**That's it!** You should see the PackOptima login page.

---

## Troubleshooting

### Problem 1: Can't Access from Phone

**Check 1: Same Network**
- Make sure your phone is on the SAME WiFi network as your computer
- Not on mobile data
- Not on guest WiFi

**Check 2: Firewall**

**Windows Firewall:**
```powershell
# Allow port 8080
netsh advfirewall firewall add rule name="PackOptima Frontend" dir=in action=allow protocol=TCP localport=8080

# Allow port 8000
netsh advfirewall firewall add rule name="PackOptima Backend" dir=in action=allow protocol=TCP localport=8000
```

**Mac Firewall:**
```bash
# System Preferences → Security & Privacy → Firewall
# Click "Firewall Options"
# Add Docker to allowed apps
```

**Linux (UFW):**
```bash
sudo ufw allow 8080/tcp
sudo ufw allow 8000/tcp
```

**Check 3: Ping Test**

From your phone/tablet, try pinging your computer:
- Install a network tool app (like "Network Analyzer" or "Fing")
- Ping your computer's IP: `192.168.1.100`
- If ping fails, there's a network/firewall issue

---

### Problem 2: CORS Error

If you see errors like:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution:**

1. Update `backend/.env` with your IP in ALLOWED_ORIGINS
2. Restart containers: `docker-compose restart backend`

---

### Problem 3: Connection Refused

**Check Docker is running:**
```bash
docker ps
```

You should see:
- packoptima-frontend
- packoptima-backend
- packoptima-db
- packoptima-redis

**Check ports are listening:**

**Windows:**
```powershell
netstat -an | findstr "8080"
netstat -an | findstr "8000"
```

**Mac/Linux:**
```bash
netstat -an | grep 8080
netstat -an | grep 8000
```

Should show:
```
0.0.0.0:8080    LISTENING
0.0.0.0:8000    LISTENING
```

---

## Advanced: Use a Custom Domain (Optional)

Instead of `http://192.168.1.100:8080`, use `http://packoptima.local:8080`

### Option 1: Edit Hosts File (Each Device)

**On each device you want to access from:**

**Windows:** Edit `C:\Windows\System32\drivers\etc\hosts`
**Mac/Linux:** Edit `/etc/hosts`

Add this line:
```
192.168.1.100    packoptima.local
```

Now access via: `http://packoptima.local:8080`

### Option 2: Set Up Local DNS (Advanced)

Use your router's DNS settings or set up a local DNS server (Pi-hole, dnsmasq).

---

## Security Considerations

### For Local Network Only (Current Setup)

✅ **Safe for:**
- Home network
- Office network (trusted)
- Development/testing

❌ **NOT safe for:**
- Public WiFi
- Internet access
- Production use

### For Internet Access (Requires More Setup)

If you want to access from ANYWHERE (not just local network):

1. **Use a VPN** (recommended)
   - Set up WireGuard or OpenVPN
   - Access your home network securely

2. **Port Forwarding + HTTPS** (advanced)
   - Set up port forwarding on your router
   - Get SSL certificate (Let's Encrypt)
   - Set up reverse proxy (Nginx)
   - Use strong authentication

3. **Use a Hosting Service** (easiest)
   - See `24_7_HOSTING_GUIDE.md`
   - Deploy to DigitalOcean, Render, etc.

---

## Quick Reference Card

### Access URLs

| Device | URL |
|--------|-----|
| Same computer | `http://localhost:8080` |
| Phone/Tablet (same WiFi) | `http://192.168.1.100:8080` |
| Other computer (same network) | `http://192.168.1.100:8080` |

### Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 8080 | `http://YOUR_IP:8080` |
| Backend API | 8000 | `http://YOUR_IP:8000` |
| Database | 5432 | (internal only) |
| Redis | 6379 | (internal only) |

### Common IP Ranges

| Range | Common For |
|-------|------------|
| 192.168.1.x | Home routers |
| 192.168.0.x | Home routers |
| 10.0.0.x | Corporate networks |
| 172.16.x.x | Corporate networks |

---

## Testing Checklist

- [ ] Found your computer's IP address
- [ ] Updated ALLOWED_ORIGINS in backend/.env
- [ ] Restarted Docker containers
- [ ] Opened firewall ports (8080, 8000)
- [ ] Phone/tablet on same WiFi
- [ ] Accessed `http://YOUR_IP:8080` from phone
- [ ] Can see login page
- [ ] Can login successfully
- [ ] All features work

---

## Example: Complete Setup

**Your computer IP:** `192.168.1.100`

**1. Update backend/.env:**
```bash
ALLOWED_ORIGINS='["http://localhost","http://localhost:8080","http://192.168.1.100:8080"]'
```

**2. Restart Docker:**
```bash
docker-compose down
docker-compose up -d
```

**3. Open firewall (Windows):**
```powershell
netsh advfirewall firewall add rule name="PackOptima" dir=in action=allow protocol=TCP localport=8080
```

**4. On your phone:**
- Connect to same WiFi
- Open browser
- Go to: `http://192.168.1.100:8080`
- Login and use PackOptima!

---

## Summary

**What you need:**
1. Your computer's IP address (e.g., 192.168.1.100)
2. Update ALLOWED_ORIGINS in backend/.env
3. Restart Docker containers
4. Open firewall ports

**Then access from any device:**
```
http://YOUR_IP:8080
```

**That's it!** Your PackOptima is now accessible from any device on your network.

---

## Need Help?

### Check Your Setup

**1. Verify IP address:**
```bash
ipconfig  # Windows
ifconfig  # Mac/Linux
```

**2. Verify Docker is running:**
```bash
docker ps
```

**3. Verify ports are open:**
```bash
netstat -an | findstr "8080"  # Windows
netstat -an | grep 8080       # Mac/Linux
```

**4. Test from same computer first:**
```
http://localhost:8080  # Should work
http://192.168.1.100:8080  # Should also work
```

**5. Then test from phone/tablet**

---

## Pro Tips

1. **Bookmark the URL** on your phone for easy access
2. **Add to home screen** (iOS/Android) for app-like experience
3. **Use WiFi only** - don't expose to internet without proper security
4. **Static IP** - Set a static IP on your computer so it doesn't change
5. **Wake-on-LAN** - Enable to wake your computer remotely

---

## Next Steps

Once you have local network access working:

1. ✅ Test on all your devices
2. ✅ Set up static IP for your computer
3. ✅ Consider VPN for remote access
4. ✅ Or deploy to cloud for internet access (see `24_7_HOSTING_GUIDE.md`)

**Your PackOptima is now accessible from any device on your network!** 🎉
