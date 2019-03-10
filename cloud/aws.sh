#! /bin/bash -e
# Provision an AWS cloud instance with tutor.
# Run with: curl -sSL https://raw.githubusercontent.com/regisb/tutor/master/cloud/aws.sh | bash -e

export TUTOR_USER="$USER"
export DEBIAN_FRONTEND=noninteractive 

echo "=============== Installing system dependencies"
sudo apt update \
    && sudo apt upgrade -y \
    && sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common \
        supervisor

echo "=============== Installing docker"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $TUTOR_USER
docker run hello-world

echo "=============== Installing docker-compose"
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "=============== Installing tutor"
sudo curl -L "https://github.com/regisb/tutor/releases/download/latest/tutor-$(uname -s)_$(uname -m)" -o /usr/local/bin/tutor
sudo chmod +x /usr/local/bin/tutor

echo "=============== Building docker images"
tutor images env
tutor images build all

echo "=============== Create Web UI script"
echo '#! /bin/bash
if [ ! -f $(tutor config printroot)/env/webui/config.yml ]; then
    tutor webui configure --user tutor --password "$(curl http://169.254.169.254/latest/meta-data/instance-id)"
fi
tutor webui start' | sudo tee /usr/local/bin/tutor-webui
sudo chmod +x /usr/local/bin/tutor-webui

echo "=============== Configuring supervisor"
echo "[program:tutor]
command=/usr/local/bin/tutor-webui
environment=HOME=/home/$TUTOR_USER
autorestart=true
user=$TUTOR_USER" | sudo tee /etc/supervisor/conf.d/tutor.conf
sudo supervisorctl update
