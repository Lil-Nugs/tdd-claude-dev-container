# docker/claude-cli/Dockerfile
# Base image for Claude CLI development environment
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI (placeholder - actual install method TBD)
# RUN npm install -g @anthropic-ai/claude-cli

# Create non-root user for security
RUN groupadd -r claude && useradd -r -g claude -m -s /bin/bash claude

# Working directory
WORKDIR /workspace

# Change ownership of workspace
RUN chown -R claude:claude /workspace

# Copy entrypoint script
COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh

# Switch to non-root user
USER claude

# Default command
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
