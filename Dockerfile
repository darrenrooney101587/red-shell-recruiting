FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        nginx \
        xmlsec1 \
        libxml2 \
        libxmlsec1 \
        libxmlsec1-dev \
        libxmlsec1-openssl \
        pkg-config \
        libssl-dev \
        libxslt1-dev \
        libxml2-dev \
        python3-dev \
        gcc \
        make \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN xmlsec1 --version
RUN pip install --upgrade pip setuptools wheel poetry

COPY . .
RUN poetry install --no-root

COPY ./config/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
