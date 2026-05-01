FROM python:3.11-slim

WORKDIR /app

# 🔹 Install system dependencies for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 🔹 Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 Copy application code
COPY . .

# 🔹 Expose port
EXPOSE 8000

# 🔹 Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
