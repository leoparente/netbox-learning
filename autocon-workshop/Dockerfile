# Use an appropriate base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install git
RUN apt-get update && apt-get install -y git

# Copy the rest of the application code
COPY . .

# Define the entry point and default command for the container
ENTRYPOINT ["python", "main.py"]
CMD ["fiber", "plane"]