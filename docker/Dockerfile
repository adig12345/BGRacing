# Shared image for both containers (publisher and processor).
# The two services differ only by the `command:` set in docker-compose.yml.
FROM ros:jazzy

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MPLBACKEND=Agg

# Slow layer first, so Docker can cache it: Python libraries for the processor.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-numpy \
        python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Fast-changing layers last: our code, data and config.
COPY src/ ./src/
COPY data/ ./data/
COPY config/ ./config/

# /ros_entrypoint.sh (from the base image) sources ROS, then runs our command.
CMD ["python3", "-c", "print('Set a command: in docker-compose.yml')"]
