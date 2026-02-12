# 🐳 How to Launch TalentTree in Docker Desktop (Windows)

**Simple 5-Step Guide with Screenshots**

---

## 📋 Prerequisites

✅ Docker Desktop installed (if not, download from https://www.docker.com/products/docker-desktop)

---

## 🚀 Step-by-Step Guide

### **Step 1: Start Docker Desktop**

1. Press **Windows Key**
2. Type **"Docker Desktop"**
3. Click on **Docker Desktop** app
4. Wait for Docker to start (whale icon appears in system tray)

**Visual Check:** 
- Look at Windows system tray (bottom-right)
- You should see a **whale icon** 🐳
- When it's ready, the whale will be steady (not animating)

---

### **Step 2: Open PowerShell in Project Folder**

**Method A: Using File Explorer**
1. Open File Explorer
2. Navigate to: `C:\Users\MAI\Talentree-Admin-Dashboard`
3. In the address bar, type `powershell` and press **Enter**
4. PowerShell opens in that folder

**Method B: Using PowerShell**
1. Press **Windows Key + X**
2. Click **"Windows PowerShell"** or **"Terminal"**
3. Type: `cd C:\Users\MAI\Talentree-Admin-Dashboard`
4. Press **Enter**

**Verify:** Your prompt should show:
```
PS C:\Users\MAI\Talentree-Admin-Dashboard>
```

---

### **Step 3: Start All Services**

In PowerShell, type this command:

```powershell
docker-compose up -d
```

Press **Enter**

**What happens:**
```
[+] Running 5/5
 ✔ Container talentree-db      Started    (10s)
 ✔ Container talentree-redis   Started    (5s)
 ✔ Container talentree-api     Started    (15s)
 ✔ Container talentree-jupyter Started    (8s)
 ✔ Container talentree-nginx   Started    (6s)
```

**Wait time:** 30-60 seconds for first-time startup

---

### **Step 4: Open Docker Desktop Dashboard**

1. Click the **whale icon** 🐳 in system tray
2. Click **"Dashboard"**

**You should see 5 containers running:**

| Container Name | Status | Port |
|----------------|--------|------|
| talentree-db | Running ✅ | 5432 |
| talentree-redis | Running ✅ | 6379 |
| talentree-api | Running ✅ | 8000 |
| talentree-jupyter | Running ✅ | 8888 |
| talentree-nginx | Running ✅ | 80 |

**Visual Layout:**
```
┌─────────────────────────────────────────┐
│  Docker Desktop                         │
├─────────────────────────────────────────┤
│  Containers (5)                         │
│                                         │
│  ● talentree-api        🟢 Running     │  ← Click for logs
│  ● talentree-db         🟢 Running     │
│  ● talentree-jupyter    🟢 Running     │
│  ● talentree-nginx      🟢 Running     │
│  ● talentree-redis      🟢 Running     │
└─────────────────────────────────────────┘
```

---

### **Step 5: Access Your Application**

Click on any container name to see options, or use these direct links:

#### **Option A: Click Links in Docker Desktop**

1. Click **"talentree-api"** container
2. Look for **"Open in Browser"** button with port **8000**
3. Click it → Opens Swagger UI

#### **Option B: Use Direct URLs**

Open your browser and go to:

**Main API (Swagger UI):**
```
http://localhost:8000/docs
```
👉 This is your **interactive API documentation**

**Jupyter Notebooks:**
```
http://localhost:8888
```
👉 Your **11 analytics notebooks**

**API Endpoints (Examples):**
```
http://localhost:8000/api/dashboard/overview
http://localhost:8000/api/brands
http://localhost:8000/api/products
```

**Via Nginx Proxy:**
```
http://localhost/docs
http://localhost/jupyter/
```

---

## 🎯 Using Docker Desktop Dashboard

### **View Logs:**
1. Click on container name (e.g., **talentree-api**)
2. Click **"Logs"** tab
3. See real-time application logs

### **Stop Services:**
1. In Docker Desktop, click **"Stop"** button next to running containers
   
**Or in PowerShell:**
```powershell
docker-compose stop
```

### **Start Services Again:**
```powershell
docker-compose start
```

### **Restart Single Service:**
1. In Docker Desktop, click container name
2. Click **"Restart"** button

**Or in PowerShell:**
```powershell
docker-compose restart api
```

### **View Container Details:**
1. Click container name
2. See:
   - **Stats** (CPU, Memory usage)
   - **Logs** (Application output)
   - **Inspect** (Configuration)
   - **Terminal** (Execute commands inside container)

---

## 🔧 Common Commands

### **Check if Everything is Running:**
```powershell
docker-compose ps
```

**Expected output:**
```
NAME                    STATUS      PORTS
talentree-api          Up          0.0.0.0:8000->8000/tcp
talentree-db           Up (healthy) 0.0.0.0:5432->5432/tcp
talentree-jupyter      Up          0.0.0.0:8888->8888/tcp
talentree-nginx        Up          0.0.0.0:80->80/tcp
talentree-redis        Up (healthy) 0.0.0.0:6379->6379/tcp
```

### **View Logs:**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
```

### **Stop Everything:**
```powershell
docker-compose down
```

### **Stop and Delete Everything (including data):**
```powershell
docker-compose down -v
```
⚠️ **Warning:** This deletes the database!

---

## 🎨 Visual Guide - Docker Desktop Interface

### **Main Dashboard:**
```
┌────────────────────────────────────────────────┐
│  Docker Desktop                          [□][X]│
├────────────────────────────────────────────────┤
│  🏠 Containers  📦 Images  🌐 Volumes  ⚙️      │
├────────────────────────────────────────────────┤
│                                                │
│  ▶ talentree-admin-dashboard (5)              │
│                                                │
│    📦 talentree-api                [⏸][♻][🗑]│
│       Status: Running                          │
│       Ports: 8000:8000                         │
│       [Open in Browser] [View Logs]            │
│                                                │
│    📦 talentree-db                 [⏸][♻][🗑]│
│       Status: Running (healthy)                │
│       Ports: 5432:5432                         │
│                                                │
│    📦 talentree-jupyter            [⏸][♻][🗑]│
│       Status: Running                          │
│       Ports: 8888:8888                         │
│       [Open in Browser] [View Logs]            │
│                                                │
│    📦 talentree-nginx              [⏸][♻][🗑]│
│       Status: Running                          │
│       Ports: 80:80                             │
│                                                │
│    📦 talentree-redis              [⏸][♻][🗑]│
│       Status: Running (healthy)                │
│       Ports: 6379:6379                         │
│                                                │
└────────────────────────────────────────────────┘
```

### **Container Details View:**
```
┌────────────────────────────────────────────────┐
│  talentree-api                           [Back]│
├────────────────────────────────────────────────┤
│  Logs | Stats | Inspect | Terminal | Files    │
├────────────────────────────────────────────────┤
│                                                │
│  📊 STATS                                      │
│  CPU:  2.5%  ████░░░░░░░░░░░░░░░░              │
│  MEM:  145MB ████░░░░░░░░░░░░░░░░              │
│  NET I/O: 1.2MB / 850KB                        │
│  DISK: 2.1GB                                   │
│                                                │
│  🖥️ LOGS                                       │
│  INFO:     Started server process [1]          │
│  INFO:     Waiting for application startup.    │
│  INFO:     Application startup complete.       │
│  INFO:     Uvicorn running on 0.0.0.0:8000     │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting

### **Problem: Docker Desktop won't start**

**Solution:**
1. Restart your computer
2. Open Docker Desktop again
3. Wait 2-3 minutes

### **Problem: "docker-compose: command not found"**

**Solution:**
```powershell
# Use docker compose (with space, no hyphen)
docker compose up -d
```

### **Problem: Port 8000 already in use**

**Solution:**
1. Stop other applications using port 8000
   
**Or change port in docker-compose.yml:**
```yaml
api:
  ports:
    - "8001:8000"  # Use 8001 instead
```

### **Problem: Containers keep restarting**

**Solution:**
1. Click container in Docker Desktop
2. Click **"Logs"** tab
3. Look for error messages
4. Common fixes:
   - Wait longer for database to start
   - Check if .env file exists
   - Restart Docker Desktop

### **Problem: Can't access http://localhost:8000**

**Check:**
1. Is container running? (Green dot in Docker Desktop)
2. Try: `docker-compose ps`
3. Try: `docker-compose logs api`
4. Try: `curl http://localhost:8000/docs`

---

## ✅ Success Checklist

After starting, you should be able to:

- [ ] See 5 green containers in Docker Desktop
- [ ] Open http://localhost:8000/docs (Swagger UI)
- [ ] Open http://localhost:8888 (Jupyter)
- [ ] See API response at http://localhost:8000/api/dashboard/overview
- [ ] View logs in Docker Desktop
- [ ] No error messages in logs

---

## 🎯 Quick Reference

### **Start Everything:**
```powershell
docker-compose up -d
```

### **Stop Everything:**
```powershell
docker-compose down
```

### **Restart Everything:**
```powershell
docker-compose restart
```

### **View Logs:**
```powershell
docker-compose logs -f
```

### **Check Status:**
```powershell
docker-compose ps
```

---

## 🌐 Access URLs Summary

| Service | URL | Description |
|---------|-----|-------------|
| **Swagger UI** | http://localhost:8000/docs | Interactive API docs |
| **ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| **Jupyter** | http://localhost:8888 | Notebooks interface |
| **Dashboard API** | http://localhost:8000/api/dashboard/overview | JSON response |
| **Nginx** | http://localhost | Reverse proxy |
| **Health Check** | http://localhost/health | System health |

---

## 📹 Video Guide Steps:

1. **Start Docker Desktop** → Wait for whale icon
2. **Open PowerShell** in project folder
3. **Run:** `docker-compose up -d`
4. **Wait:** 30-60 seconds
5. **Open:** http://localhost:8000/docs
6. **Success!** 🎉

---

## 💡 Pro Tips

1. **Keep Docker Desktop open** while working
2. **Use Docker Desktop Dashboard** to monitor containers
3. **Check logs** if something doesn't work
4. **Bookmark** http://localhost:8000/docs for quick access
5. **Use** `docker-compose restart api` after code changes

---

**🎉 You're ready to use your TalentTree Dashboard with Docker Desktop!**

**Questions? Check the logs in Docker Desktop or run `docker-compose logs -f`**
