#!/bin/bash

# Create HTTPS and HTTP Proxy configuration and exceptions

if [ "$1" -ne 1 ]
then
  echo "Proxy address was not supplied"
  exit 1
else


sudo tee /etc/systemd/system/docker.service.d/https-proxy.conf >/dev/null << EOF
[Service]
Environment="HTTPS_PROXY=$1" "NO_PROXY=localhost,127.0.0.1"
EOF

sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf >/dev/null << EOF
[Service]
Environment="HTTP_PROXY=$1 "NO_PROXY=localhost,127.0.0.1"
EOF

# Restart Docker daemon
sudo systemctl daemon-reload
sudo systemctl restart docker
fi

