# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Metadata
LABEL maintainer="benedikt.budig@uni-wuerzburg.de"
LABEL org.opencontainers.image.source="https://github.com/jsbien/glyph-miner"

# Environment setup to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    g++ git make mysql-server nginx \
    python3 python3-dev python3-pip python3-numpy \
    python3-mysqldb python3-pil \
    libpq-dev libjpeg-dev libfreetype6-dev zlib1g-dev \
    libxml2-dev libxslt-dev build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install uwsgi web.py

# Clean any old glyph-miner data
WORKDIR /opt/
RUN rm -rf /opt/glyph-miner

# Clone your updated glyph-miner repository
RUN git clone https://github.com/jsbien/glyph-miner.git glyph-miner

# Set working directory to the app
WORKDIR /opt/glyph-miner

# Expose the HTTP port (uWSGI will serve on this)
EXPOSE 9090

# Start uWSGI pointing to the correct WSGI app
CMD ["uwsgi", "--http", ":9090", "--wsgi-file", "server/web/wsgi.py", "--callable", "app"]
