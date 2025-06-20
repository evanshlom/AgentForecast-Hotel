FROM python:3.9-slim

# Install basic tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
RUN mkdir -p /workspace

# Set working directory
WORKDIR /workspace

# Keep container running
CMD ["bash"]