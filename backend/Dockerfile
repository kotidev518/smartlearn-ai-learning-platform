<<<<<<< HEAD
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download SBERT model during build to save startup time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

# Expose port 7860 for HF
EXPOSE 7860

# Default command (will be overridden in docker-compose.yml)
=======
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to keep image size smaller
# Installing CPU-only PyTorch to drastically reduce image size
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Hugging Face Spaces expects port 7860
ENV PORT=7860
EXPOSE 7860

# Start the FastAPI server via uvicorn
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
