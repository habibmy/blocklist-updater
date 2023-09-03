# Use a minimal base image like Alpine Linux
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN apk add --no-cache --virtual .build-deps build-base \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps build-base

# Copy the application code to the container
COPY . .

# Expose the port on which the Flask application runs
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--no-reload"]
