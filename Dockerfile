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

# Expose port 5000 (this is the fixed port we are using)
EXPOSE 5000

# Run the application using gunicorn on port 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
