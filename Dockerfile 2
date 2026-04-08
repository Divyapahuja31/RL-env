# Use Python 3.10 slim image for a minimal footprint
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose port for HF Spaces (port 7860 is the HF standard)
EXPOSE 7860

# Run the FastAPI server (HF Spaces needs a running web server)
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
