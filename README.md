# Chat Server with Docker & MySQL

## Overview

This is a simple chat server built with Flask that stores messages in a MySQL database. The application is packaged as a Docker image and runs alongside MySQL in a docker-compose topology.

**Architecture:**
- **Flask Chat App** (`app.py`) - HTTP server that handles room-based chat; stores/retrieves messages from MySQL
- **MySQL Database** - Persistent data store; holds messages with timestamps, usernames, room names
- **Docker** - Both services run in containers; images are built and orchestrated via docker-compose

---

## File Structure

```
.
├── app.py                          # Flask application (the chat server)
├── templates/
│   └── index.html                  # Frontend HTML (jQuery-based chat UI)
├── requirements.txt                # Python dependencies (Flask, SQLAlchemy, PyMySQL)
├── Dockerfile                      # Instructions to build the chat app Docker image
├── docker-compose.yml              # Orchestrates chat + MySQL containers
├── .devcontainer/
│   ├── devcontainer.json           # GitHub Codespaces devcontainer config
│   └── devcontainer.env.sample     # Sample environment variables (do not commit secrets)
└── README_CODESPACES.md            # Setup guide for GitHub Codespaces
```

---

## How It Works (Operation Flow)

### 1. **Docker Image Build**
When you run `docker-compose up`, Docker reads the `Dockerfile` and builds the chat app image:
- Base: Python 3.12 slim image
- Install dependencies from `requirements.txt`
- Copy `app.py` and `templates/` into the image
- Set Flask environment variables
- Expose port 5000

**Location:** `Dockerfile` (defines the build steps)

### 2. **Container Startup**
`docker-compose` starts two containers based on `docker-compose.yml`:

#### MySQL Container
- **Image:** Official MySQL 8.0
- **Port:** 3306 (internal, mapped to host port 3306)
- **Environment:** Creates database `chat`, user `chatuser`
- **Volume:** `mysql-data` (named Docker volume persists DB files across restarts)
- **Health Check:** Pings MySQL every 10s to ensure readiness

**Location:** `docker-compose.yml` → `services.mysql`

#### Chat App Container
- **Image:** Built from `Dockerfile` (the Flask app)
- **Port:** 5000 (Flask development server, mapped to host port 5000)
- **Environment:** 
  - `MYSQL_URI=mysql+pymysql://chatuser:chatpass@mysql:3306/chat` (connection string to MySQL)
  - `FLASK_ENV=production`
- **Depends On:** Waits for MySQL health check before starting
- **Volumes:** Code and templates are mounted for live editing

**Location:** `docker-compose.yml` → `services.chat`

### 3. **Flask App Initialization** (runs inside `chat` container)
When the Flask container starts, `app.py` is executed:

```python
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('MYSQL_URI')
db = SQLAlchemy(app)
```

- **Database Connection:** Flask reads `MYSQL_URI` environment variable and connects to MySQL
- **Message Model:** Defines a `Message` table (room, timestamp, username, text)
- **Routes:**
  - `GET /` or `GET/<room>` → Returns `templates/index.html` (the chat UI)
  - `GET /api/chat/<room>` → Returns all messages for that room (newline-separated)
  - `POST /api/chat/<room>` → Inserts a new message into the database

**Location:** `app.py` (SQLAlchemy ORM setup, route handlers)

### 4. **Frontend and Chat Flow**
User opens browser to `http://localhost:5000`:

1. Flask serves `templates/index.html` (jQuery-based chat UI)
2. JavaScript calls `GET /api/chat/<room>` every 1.5 seconds to fetch messages
3. User types message and clicks "send"
4. JavaScript calls `POST /api/chat/<room>` with username and message text
5. Flask inserts message into MySQL with timestamp
6. Next fetch displays the new message

**Location:** 
- HTML form & JavaScript logic: `templates/index.html`
- POST/GET handlers: `app.py` → `get_chat()` function

### 5. **Data Persistence**
All chat messages are stored in MySQL, not on disk:
- **Table:** `message` (auto-created by SQLAlchemy)
- **Fields:** id, room, timestamp, username, text
- **Persistence:** The `mysql-data` Docker volume ensures data survives container restarts

**Location:** MySQL container, volume `mysql-data`

---

## Running the Application

### Prerequisites
- Docker and docker-compose installed

### Quick Start (Local)
```bash
cd /home/ic/PY/CHAT
docker-compose up --build
```

This will:
1. Build the Flask image
2. Start MySQL container
3. Start Flask container
4. Expose Flask at `http://localhost:5000`

Open your browser → `http://localhost:5000` → start chatting!

### Running in GitHub Codespaces
When you open this repo in Codespaces:
1. `.devcontainer/devcontainer.json` is detected
2. Codespaces runs `docker-compose.yml` with the configuration
3. MySQL service starts with persistent volume
4. Chat app starts and connects to MySQL
5. Flask is accessible at the forwarded port

Details: See `.devcontainer/devcontainer.json` and `README_CODESPACES.md`

### Stopping the Application
```bash
docker-compose down
```
This stops containers but **preserves the MySQL data volume** (`mysql-data`).

To remove all data:
```bash
docker-compose down -v
```

---

## Database Configuration

The chat app uses environment variable `MYSQL_URI` to connect to MySQL:
```
mysql+pymysql://chatuser:chatpass@mysql:3306/chat
```

**Breakdown:**
- `mysql+pymysql://` — dialect and driver (PyMySQL)
- `chatuser:chatpass` — MySQL user and password
- `@mysql:3306` — host (service name in docker-compose) and port
- `/chat` — database name

This is set in `docker-compose.yml` → `services.chat.environment.MYSQL_URI`

**For Codespaces:** Copy `.devcontainer/devcontainer.env.sample` to `.devcontainer/devcontainer.env` (git-ignored) if you need custom credentials.

---

## Dependencies

See `requirements.txt`:
- **Flask** — Web framework
- **Flask-SQLAlchemy** — ORM for database operations
- **SQLAlchemy** — Database abstraction layer
- **pymysql** — Python MySQL driver

Install locally (if not using Docker):
```bash
pip install -r requirements.txt
```

---

## Development & Customization

### Modify Frontend
Edit `templates/index.html` and refresh browser

### Modify Routes or Database
Edit `app.py` and restart the Flask container:
```bash
docker-compose restart chat
```

### Change MySQL Credentials
Edit `docker-compose.yml` → `services.mysql.environment` and `services.chat.environment.MYSQL_URI`, then:
```bash
docker-compose down -v
docker-compose up --build
```

---

## Next Steps (Upcoming Development Week)

This setup is a **foundation for scaling**:
- Add authentication (user accounts, passwords)
- Implement WebSockets for real-time updates (instead of polling)
- Add room management (create/delete rooms, user roles)
- Containerize the database with proper backups
- Add CI/CD pipelines with Docker registries

---

## Troubleshooting

**Chat app can't connect to MySQL:**
- Check `docker-compose logs chat` for errors
- Ensure `mysql` service is healthy: `docker-compose logs mysql`
- Verify `MYSQL_URI` matches the MySQL configuration

**Port 5000 already in use:**
- Change the port mapping in `docker-compose.yml` → `services.chat.ports`

**Data lost after restart:**
- Confirm the `mysql-data` volume exists: `docker volume ls | grep mysql-data`
- If using `docker-compose down -v`, the volume is intentionally removed

