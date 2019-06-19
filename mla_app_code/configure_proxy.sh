#!/bin/bash

# Create HTTPS and HTTP Proxy configuration and exceptions

if [ "$1" -ne 1 ]
then
  echo "Proxy address was not supplied"
  exit 1
else

# System 
echo "https_proxy=$1" | sudo tee -a /etc/environment >/dev/null
#echo "http_proxy=$1" | sudo tee -a /etc/environment >/dev/null
echo "no_proxy=localhost,127.0.0.1" | sudo tee -a /etc/environment >/dev/null

# apt-get 

sudo touch /etc/apt/apt.conf.d/proxy.conf

sudo tee /etc/apt/apt.conf.d/proxy.conf >/dev/null << EOF
Acquire {
  HTTPS::proxy "$1";
}
EOF



# Docker service 
sudo tee /etc/systemd/system/docker.service.d/https-proxy.conf >/dev/null << EOF
[Service]
Environment="HTTPS_PROXY=$1" "NO_PROXY=localhost,127.0.0.1"
EOF

#sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf >/dev/null << EOF
#[Service]
#Environment="HTTP_PROXY=$1 "NO_PROXY=localhost,127.0.0.1"
#EOF

# Restart Docker daemon
sudo systemctl daemon-reload
sudo systemctl restart docker
fi



# wget 

#sed -i "s,#http_proxy = http://proxy.yoyodyne.com:18023/,http_proxy=$1,g" /etc/wgetrc 
sed -i "s,#https_proxy = http://proxy.yoyodyne.com:18023/,https_proxy=$1,g" /etc/wgetrc 

