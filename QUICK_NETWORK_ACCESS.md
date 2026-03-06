# 🚀 Quick Network Access Setup

## Your IP: `10.249.42.28`

---

## 3 Steps to Access from Any Device

### 1️⃣ Run Setup Script (as Administrator)

```powershell
.\setup_network_access.ps1
```

### 2️⃣ Test from Computer

```
http://10.249.42.28:8080
```

### 3️⃣ Test from Phone

Connect phone to SAME WiFi, then open:
```
http://10.249.42.28:8080
```

---

## Done! ✅

**Your PackOptima is now accessible from:**
- ✅ Your computer
- ✅ Your phone
- ✅ Your tablet
- ✅ Any device on same WiFi

---

## Manual Commands (if needed)

### Open Firewall:
```powershell
netsh advfirewall firewall add rule name="PackOptima Frontend" dir=in action=allow protocol=TCP localport=8080
netsh advfirewall firewall add rule name="PackOptima Backend" dir=in action=allow protocol=TCP localport=8000
```

### Restart Docker:
```bash
docker-compose down
docker-compose up -d
```

---

## Access URLs

| From | URL |
|------|-----|
| Computer | `http://localhost:8080` |
| Phone | `http://10.249.42.28:8080` |
| Tablet | `http://10.249.42.28:8080` |

---

**Need more help?** See `NETWORK_ACCESS_COMPLETE.md`
