FROM python:3.10

# Install Python and pip
RUN apt-get update && apt-get install -y nginx build-essential cmake

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Set the working directory
WORKDIR /workspace

# Copy the requirements file and the project code from your host to the container
COPY requirements.txt .
# make build context find the venv first, equivalent to activating and install Python dependencies
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables (these should be set securely in real deployments)
ENV GITHUB_TOKEN=replace-with-your-token
ENV OPENAI_API_KEY=replace-with-your-token
ENV OPENAI_ORG_ID=replace-with-your-token
ENV OPENAI_PROJECT_ID=replace-with-your-token
ENV DJANGO_SECRET=replace-with-your-token
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS="None"


# Collect static files
RUN python manage.py collectstatic --noinput

# Configure Nginx
COPY devops/docker/nginx.conf /etc/nginx/nginx.conf

# Start the server
CMD ["bash", "-c", "gunicorn development_workforce.wsgi:application --bind 0.0.0.0:8000"]

EXPOSE 8000
