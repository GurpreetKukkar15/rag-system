# Use a lightweight Python base image
FROM python:3.10-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and the data (including the FAISS index)
COPY src/ ./src/
COPY data/ ./data/
COPY production_api.py .

# Create a simple .env file for the container
RUN echo "FAISS_INDEX_PATH=data/faiss_index" > .env && \
    echo "LLM_MODEL=llama3" >> .env

# Expose the port that FastAPI runs on
EXPOSE 8000

# Define the command to run the application
CMD ["python", "production_api.py"]
