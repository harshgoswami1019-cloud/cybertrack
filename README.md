# 🛰️ CyberTrack

### Consent-Based Live Location Intelligence Platform

CyberTrack is a Flask-based web application that allows a user to **voluntarily share their device location** and lets an authorized monitoring session view the shared location on a live map.

The project is designed as a **cybersecurity and web-development portfolio project** demonstrating real-time location sharing, APIs, databases, session tokens, interactive maps, and data export.

> ⚠️ **Privacy Notice:** CyberTrack does not secretly track people. The person sharing their location must explicitly grant browser location permission and can stop sharing at any time.

---

## 🚀 Features

### 📍 Location Sharing

* Browser GPS location
* Explicit location permission
* Start location sharing
* Stop location sharing
* Live latitude and longitude
* GPS accuracy
* Last location update
* Session expiration

### 🗺️ Live Monitoring

* Interactive live map
* OpenStreetMap integration
* Live location marker
* GPS accuracy circle
* Movement path
* Connection status
* Tracking status

### 📊 Location Analytics

* Location history
* Timestamp for each location
* Distance between location points
* Total distance travelled
* Tracking duration
* Number of recorded points

### 🔐 Session Security

* Random share token
* Random monitor token
* Separate share and monitoring links
* Temporary sessions
* Session expiration
* Input validation
* Monitoring token should remain private

### 📁 Data Management

* CSV location-history export
* Delete location history
* SQLite database
* Health-check endpoint

### 💻 Interface

* Dark cybersecurity-style design
* Terminal-inspired interface
* Live system indicators
* Responsive desktop layout
* Mobile-friendly design

---

# 🛠️ Technologies

| Technology      | Purpose                         |
| --------------- | ------------------------------- |
| Python          | Backend                         |
| Flask           | Web framework                   |
| JavaScript      | Frontend logic and live updates |
| HTML5           | Page structure                  |
| CSS3            | User interface                  |
| SQLite          | Database                        |
| Leaflet.js      | Interactive maps                |
| OpenStreetMap   | Map data                        |
| Geolocation API | Device location                 |

---

# 📂 Project Structure

```text
cybertrack/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── monitor.html
│   └── share.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        ├── share.js
        └── monitor.js
```

---

# ⚙️ Run Locally

## Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/cybertrack.git
```

Enter the project:

```bash
cd cybertrack
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python3 app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🔄 How It Works

```text
                    CYBERTRACK
                        │
                        ▼
                 CREATE SESSION
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
         SHARE LINK          MONITOR LINK
              │                   │
              ▼                   ▼
       User opens page      Authorized monitor
              │                   │
              ▼                   │
      Browser asks for GPS        │
              │                   │
              ▼                   │
      User grants permission      │
              │                   │
              ▼                   │
       Location is sent ──────────┤
                                  │
                                  ▼
                            LIVE DASHBOARD
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                 ▼
               MAP             HISTORY           ANALYTICS
                                  │
                                  ▼
                             CSV EXPORT
```

---

# 🔗 Main Application Routes

### Home

```text
/
```

Creates a new tracking session.

### Share Page

```text
/share/<share_token>
```

Allows the user to voluntarily share their device location.

### Monitor Page

```text
/monitor/<monitor_token>
```

Displays the authorized monitoring dashboard.

---

# 🔌 API Endpoints

### Create a Session

```http
POST /api/session/create
```

Creates separate sharing and monitoring tokens.

### Start Location Sharing

```http
POST /api/session/<share_token>/start
```

Starts a session.

### Stop Location Sharing

```http
POST /api/session/<share_token>/stop
```

Stops a session.

### Save Location

```http
POST /api/location
```

Stores an authorized GPS location.

### Get Current Location

```http
GET /api/monitor/<monitor_token>/location
```

Returns the latest location.

### Get Location History

```http
GET /api/monitor/<monitor_token>/history
```

Returns recorded location points.

### Session Information

```http
GET /api/monitor/<monitor_token>/info
```

Returns session status and expiration information.

### Export CSV

```http
GET /api/monitor/<monitor_token>/export.csv
```

Downloads location history as CSV.

### Delete History

```http
DELETE /api/monitor/<monitor_token>/history
```

Deletes stored location history.

### Health Check

```http
GET /health
```

Returns the application status.

---

# 🔐 Privacy & Security

CyberTrack is designed for **authorized and consent-based location sharing**.

The application does not:

* secretly activate GPS
* bypass browser permissions
* track someone using only a phone number
* attempt to bypass device security
* collect location without browser permission

The user must explicitly grant browser location permission before GPS data is shared.

The **monitor token is sensitive** because anyone who possesses it may be able to access the corresponding session's location information. Keep it private.

---

# 🌐 Deployment

CyberTrack is a **Flask/Python application**, so GitHub Pages is not suitable for running the backend.

For deployment, use a service that supports Python web applications, such as:

* Render
* Railway
* PythonAnywhere
* VPS/cloud hosting

### Production start command

```bash
gunicorn app:app
```

### Build command

```bash
pip install -r requirements.txt
```

Make sure `requirements.txt` contains:

```text
Flask==3.1.2
gunicorn
```

For public deployment, use **HTTPS** so browser geolocation can operate in a secure browser context.

---

# 🧪 Testing Checklist

### Home Page

```text
✓ Website loads
✓ Session can be created
✓ Share link is generated
✓ Monitor link is generated
```

### Share Page

```text
✓ Location permission request appears
✓ Start sharing works
✓ GPS coordinates appear
✓ Location updates are sent
✓ Stop sharing works
✓ Session expiration is displayed
```

### Monitor Page

```text
✓ Map loads
✓ Current location appears
✓ Marker updates
✓ Accuracy circle updates
✓ Movement path appears
✓ Location history appears
✓ Distance is calculated
✓ Tracking duration appears
✓ CSV export works
✓ History deletion works
```

---

# 🎓 Learning Objectives

This project demonstrates practical experience with:

* Python
* Flask
* REST APIs
* JavaScript
* HTML and CSS
* Browser Geolocation API
* SQLite
* Database operations
* JSON
* Session/token generation
* Interactive maps
* CSV generation
* Frontend/backend communication
* Basic web security
* Git and GitHub
* Web deployment

---

# 🔮 Future Improvements

Potential future versions could include:

* User authentication
* Admin dashboard
* PostgreSQL
* WebSockets for real-time communication
* Role-based access control
* Two-factor authentication
* QR-code sharing
* Geofencing
* Location notifications
* Automatic session cleanup
* Audit logs
* Better access control
* Docker deployment
* Cloud database
* Production monitoring

---

# 👨‍💻 Author

## Harsh Goswami

CyberTrack is a learning and portfolio project created to explore:

**Python • Flask • JavaScript • Cybersecurity • APIs • Databases • Maps • Web Development**

---

# ⚠️ Disclaimer

CyberTrack is intended for:

**Educational purposes, authorized testing, and consent-based location sharing.**

Do not use the application to monitor or track another person without their knowledge and permission.

Always respect applicable privacy laws, regulations, and organizational policies.

---

# ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.

**CyberTrack — Built with code, security, and consent.**
