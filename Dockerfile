# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to ensure output is sent straight to the terminal (important for logs)
ENV PYTHONUNBUFFERED 1

# Create and set the working directory for your app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire content of your application into the container
COPY . /app/

# Expose the port that the app will run on
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]