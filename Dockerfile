# Use slim Python image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies for PyMuPDF (fitz)
# libgl1-mesa-glx is obsolete → replaced with libgl1
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project
COPY . .

# Expose ports for API and Dashboard
# Port 8000: FastAPI
EXPOSE 8000
# Port 8501: Streamlit dashboard
EXPOSE 8501

# Default command — run the API
CMD ["python", "run_api.py"]