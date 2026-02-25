Codespaces setup (MySQL + app)
--------------------------------

This repository includes a `docker-compose.yml` and a Codespaces devcontainer that starts a MySQL service for a persistent demo database.

Files added:
- docker-compose.yml: starts `mysql` and a `workspace` container. The `mysql` service uses a named Docker volume `mysql-data` so data persists across container restarts.
- .devcontainer/devcontainer.json: tells Codespaces to bring up the compose services and install Python requirements.
- .devcontainer/devcontainer.env.sample: example environment variables for DB credentials and `MYSQL_URI`.

Step-by-step (what happens and why):
1) Codespace launch: Codespaces reads `.devcontainer/devcontainer.json` and runs `docker-compose.yml`.
   - Outcome: `mysql` service starts and exposes port 3306 internally in the Codespace network.

2) Workspace container: the `workspace` service (a devcontainer Python image) mounts the repo at `/workspace` and is the environment where you run commands.
   - Outcome: `pip install -r requirements.txt` runs automatically (postCreateCommand).

3) Environment variables: set credentials in your Codespace (or copy `.devcontainer/devcontainer.env.sample` to a `.env` or Codespaces secrets).
   - Important: do NOT commit real passwords. Use Codespaces secrets or `.env` ignored by git.

4) App connection: set `MYSQL_URI` in the environment (example):
   `mysql+pymysql://chatuser:chatpass@mysql:3306/chat`
   - Note: hostname is `mysql` (the compose service name) when running inside the Codespace workspace container.

5) Run migration and app inside Codespace:
```bash
export MYSQL_URI='mysql+pymysql://chatuser:chatpass@mysql:3306/chat'
python3 migrate_chats_to_db.py
export FLASK_APP=app.py
flask run --host=0.0.0.0
```

Persistence notes:
- The named volume `mysql-data` stores MySQL files; it survives container restarts. If you delete the Codespace or remove volumes, data will be lost.

Security notes:
- Use Codespaces secrets for real credentials. The sample file is for local demo only.
