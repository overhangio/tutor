#! /bin/bash -e
# Provision an AWS cloud instance with tutor.
# Run with: curl -sSL https://raw.githubusercontent.com/regisb/tutor/master/cloud/ubuntu.sh | sudo bash -e

export TUTOR_VERSION="v3.0.4"
export USER="$SUDO_USER"
export DEBIAN_FRONTEND=noninteractive 

echo "=============== Installing system dependencies"
apt update \
    && apt upgrade -y \
    && apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common \
        supervisor

echo "=============== Installing docker"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt update
apt install -y docker-ce docker-ce-cli containerd.io
docker run hello-world
usermod -aG docker $USER

echo "=============== Installing docker-compose"
curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo "=============== Installing tutor"
curl -L "https://github.com/regisb/tutor/releases/download/$TUTOR_VERSION/tutor-linux" -o /usr/local/bin/tutor
chmod +x /usr/local/bin/tutor

echo "=============== Configuring supervisor"
echo "[program:tutor]
command=/usr/local/bin/tutor webui start
environment=HOME=/home/$USER
autorestart=true
user=$USER" > /etc/supervisor/conf.d/tutor.conf
supervisorctl update
