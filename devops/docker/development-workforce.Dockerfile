FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y nginx build-essential cmake

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Configure Nginx
COPY devops/docker/nginx.conf /etc/nginx/nginx.conf

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "development_workforce.wsgi:application", "--bind", "0.0.0.0:8000"]