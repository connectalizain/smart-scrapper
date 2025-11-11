# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Copy the rest of the project files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["chainlit", "run", "app.py", "-w"]