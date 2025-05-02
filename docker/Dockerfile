FROM ubuntu:20.04

LABEL maintainer="benedikt.budig@uni-wuerzburg.de"
LABEL org.opencontainers.image.source="https://github.com/jsbien/glyph-miner"

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    g++ git make mysql-server nginx \
    python3 python3-dev python3-pip python3-numpy \
    python3-mysqldb python3-pil \
    libpq-dev libjpeg-dev libfreetype6-dev zlib1g-dev \
    libxml2-dev libxslt-dev build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip3 install uwsgi

# Fix nginx config
COPY docker/default /etc/nginx/sites-enabled/default
RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf

# Cleaning old files
RUN rm -rf /opt/glyph-miner/*

# Start script
COPY docker/start-container.sh /opt/glyph-miner/start-container.sh
RUN chmod +x /opt/glyph-miner/start-container.sh

# Working dir
WORKDIR /opt/glyph-miner

# Copy application
COPY . /opt/glyph-miner

EXPOSE 9090

# Start services
CMD ["/opt/glyph-miner/start-container.sh"]
