# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Run the required updates
RUN apt-get update && apt-get install -y \
    curl \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python primary dependencies with pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install psycopg2

# Install Playwright and its dependencies
RUN playwright install && playwright install-deps

# Copy the rest of the application code into the container
COPY . .

# ARG EXPOSE_PORT
# Expose the port the app runs on
EXPOSE ${EXPOSE_PORT}

# ARG HOST
# ARG PORT
# Set environment variables for flexibility
ENV HOST=${HOST}
ENV PORT=${PORT}

# Command to run the application
CMD ["sh", "-c", "date && python app.py --host=${HOST} --port=${PORT}"]