#! /bin/bash -e
# Provision an AWS cloud instance with tutor.
# Run with: curl -sSL https://raw.githubusercontent.com/regisb/tutor/master/cloud/aws.sh | bash -e

export TUTOR_USER="$USER"
export DEBIAN_FRONTEND=noninteractive 

echo "=============== Installing system dependencies"
sudo apt update \
    && sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common

echo "=============== Installing docker"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $TUTOR_USER
sudo su - $TUTOR_USER
docker run hello-world

echo "=============== Installing docker-compose"
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "=============== Installing tutor"
sudo curl -L "https://github.com/regisb/tutor/releases/download/latest/tutor-$(uname -s)_$(uname -m)" -o /usr/local/bin/tutor
sudo chmod +x /usr/local/bin/tutor

echo "=============== Pulling vendor docker images"
docker pull memcached:1.4.38
docker pull mongo:3.2.16
docker pull mysql:5.6.36
docker pull elasticsearch:1.5.2
docker pull nginx:1.13
docker pull rabbitmq:3.6.10
docker pull namshi/smtp:latest

echo "=============== Building docker images"
tutor config save --silent --set ACTIVATE_NOTES=true --set ACTIVATE_XQUEUE=true
tutor images build all

echo "=============== Create Web UI script"
echo '#! /bin/bash
if [ ! -f $(tutor config printroot)/env/webui/config.yml ]; then
    mkdir -p $(tutor config printroot)/env/webui
    tutor webui configure --user tutor --password "$(curl http://169.254.169.254/latest/meta-data/instance-id)"
fi
tutor webui start' | sudo tee /usr/local/bin/tutor-webui
sudo chmod +x /usr/local/bin/tutor-webui

echo "=============== Configuring systemd"
echo "[Unit]
Description=Tutor web UI
After=network.target

[Service]
User=$TUTOR_USER
WorkingDirectory=/home/$TUTOR_USER
Environment="HOME=/home/$TUTOR_USER"
ExecStart=/usr/local/bin/tutor-webui
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/tutor-webui.service
sudo systemctl enable tutor-webui

echo "=============== Clean authorized keys"
sudo find / -name "authorized_keys" -exec rm -f {} \;

echo "=============== Clean history"
sudo find /root/.*history /home/*/.*history -exec rm -f {} \;
