# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (if needed - minimal for now)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual app code
COPY app/ ./app
# COPY .env .env

# Expose port 8000
EXPOSE 8000

# Run the FastAPI server using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
