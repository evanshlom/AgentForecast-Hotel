FROM python:3.9-slim

WORKDIR /workspace

# Install basic tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    websockets \
    anthropic \
    numpy \
    pandas \
    python-dateutil \
    jupyter \
    matplotlib

CMD ["bash"]