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
# We explicitly set the host to 0.0.0.0 and port to 8000 so the app is accessible 
# from the host environment (like Hugging Face Spaces).
# We also add -h (headless) to prevent a browser from opening server-side.
CMD ["chainlit", "run", "app.py", "-w", "--host", "0.0.0.0", "--port", "8000", "-h"]