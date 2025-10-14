# 1. Base Image
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# 2. Set Environment Variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# 3. Set Working Directory
# Set the working directory in the container to /app
WORKDIR /app

# 4. Install Dependencies
# Copy the requirements file into the container at /app
COPY requirements.txt .
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 5. Copy Application Code
# Copy the rest of the application's code into the container at /app
COPY . .

# 6. Expose Port
# Make port 8000 available to the world outside this container
EXPOSE 8000

# 7. Run Application
# Run uvicorn server
# Use 0.0.0.0 to make it accessible from outside the container
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
