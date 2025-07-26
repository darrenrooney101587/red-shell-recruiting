#!/bin/bash
set -e
CERT_DIR=../nginx_local/certs
DOMAIN=dev.redshellrecruiting.com

mkdir -p $CERT_DIR
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout $CERT_DIR/selfsigned.key \
  -out $CERT_DIR/selfsigned.crt \
  -subj "/CN=$DOMAIN"
