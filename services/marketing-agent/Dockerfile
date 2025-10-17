# Use the official Rasa image that already includes TF/spaCy CPU-safe wheels
FROM rasa/rasa:3.6.21-full

# IMPORTANT:
# This base image runs as a non-root user (UID 1001) by default.
# We temporarily switch to root to install extra Python deps and fix file perms.
USER root

# Set working directory
WORKDIR /app

# Copy only the requirements first to leverage Docker layer caching
# TIP: Do NOT pin "rasa" here; the base image already ships the correct version.
COPY requirements.txt ./

# Install additional Python dependencies into the existing venv
# (present at /opt/venv in this image). Using --no-cache-dir keeps the image smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your project (domain, config, data, actions, entrypoint, etc.)
COPY . .

# Make sure the entrypoint script is executable.
# If your Git repo already marks it executable (chmod +x committed),
# this step is not strictly necessary, but it's safe.
RUN chmod +x /app/entrypoint.sh

# Drop privileges back to the default non-root user for safer runtime
USER 1001

# Expose Rasa API and Action Server ports
EXPOSE 8002 5055

# Use your custom entrypoint to start both Rasa and the Action Server
ENTRYPOINT ["./entrypoint.sh"]
