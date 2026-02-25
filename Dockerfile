FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py .
COPY templates/ templates/

# Expose Flask port
EXPOSE 5000

# Set environment variables (can be overridden at runtime)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run Flask development server (replace with gunicorn for production)
CMD ["flask", "run", "--host=0.0.0.0"]
