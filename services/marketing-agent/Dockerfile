# Use an official Rasa image to avoid binary incompatibilities
# The "-full" tag includes TensorFlow, spaCy, and other ML deps prebuilt for CPU safety
FROM rasa/rasa:3.6.21-full

# Set working directory inside container
WORKDIR /app

# Copy dependency list first to leverage Docker layer caching
COPY requirements.txt ./

# Install additional Python dependencies (if you have any custom ones)
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy the rest of the project (config.yml, domain.yml, data/, actions/, etc.)
COPY . .

# Expose default Rasa server and action server ports
EXPOSE 8002 5055

# Make sure entrypoint script is executable
RUN chmod +x entrypoint.sh

# Use your custom entrypoint to start both Rasa and Action servers
ENTRYPOINT ["./entrypoint.sh"]
