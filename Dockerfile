# Use official Python 3.10 image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Set environment variable to avoid Python buffering
ENV PYTHONUNBUFFERED=1

# Expose the port your app listens on (default Flask port)
EXPOSE 5000

# Run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app", "--workers", "3", "--timeout", "60"]
