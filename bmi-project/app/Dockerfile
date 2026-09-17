# --- Stage 1: base image ---
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first (Docker layer caching: only re-installs
# dependencies if requirements.txt changes, not on every code change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Container listens on port 5000
EXPOSE 5000

# Run as non-root user for security
RUN useradd -m appuser
USER appuser

CMD ["python", "app.py"]
