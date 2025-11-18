# Use lightweight Python image
FROM python:3.10-slim

# Set /app as working directory
WORKDIR /app

# Copy only requirements first (better build caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose Flask port
EXPOSE 5000

# Set environment for production
ENV FLASK_ENV=production

# Run the Flask application
CMD ["python", "app.py"]

