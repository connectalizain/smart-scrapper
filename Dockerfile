# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install uv
RUN pip install uv

# Install dependencies using uv from pyproject.toml
RUN uv pip install --system chainlit python-dotenv playwright openai agents

# Install Playwright browsers
RUN playwright install

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["chainlit", "run", "app.py", "-w"]
