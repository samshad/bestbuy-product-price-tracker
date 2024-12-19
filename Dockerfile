# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install system dependencies and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    libpq-dev \
    gcc \
    && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install primary Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install psycopg2
RUN pip install psycopg2

# Install Playwright and its dependencies
RUN playwright install && playwright install-deps

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE ${EXPOSE_PORT}

# Set environment variables for flexibility
ENV HOST=${HOST}
ENV PORT=${PORT}

# Required for SSL connection to the database
ENV PGSSLROOTCERT=/etc/ssl/certs/ca-certificates.crt

# Command to run the application
CMD ["sh", "-c", "date && python app.py --host=${HOST} --port=${PORT}"]