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

# Clone your glyph-miner repository (your fixed version!)
WORKDIR /opt/
# RUN git clone https://github.com/jsbien/glyph-miner.git glyph-miner

# Copy start script
COPY docker/start-container.sh /opt/glyph-miner/start-container.sh

# Make script executable
RUN chmod +x /opt/glyph-miner/start-container.sh    

# Set working directory
WORKDIR /opt/glyph-miner

# 🧹 Clean old files before copying fresh code
RUN rm -rf /opt/glyph-miner/*

COPY docker/start-container.sh /opt/glyph-miner/start-container.sh
COPY . /opt/glyph-miner
# Expose uwsgi port
EXPOSE 9090

# Start mysql, nginx and uwsgi
CMD ["/opt/glyph-miner/start-container.sh"]
