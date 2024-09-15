# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to ensure Python output is sent directly to the terminal without buffering
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on (note: Railway will automatically bind a dynamic port)
EXPOSE 5000

# Define environment variable to ensure the correct Flask app is used
ENV FLASK_APP=app.py

# Ensure the app runs on the port provided by Railway dynamically
CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "app:app"]
