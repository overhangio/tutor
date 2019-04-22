#! /bin/bash -e
# Provision an AWS cloud instance with tutor.
# Run with: curl -sSL https://raw.githubusercontent.com/regisb/tutor/master/cloud/aws.sh | bash -e

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
sudo usermod -aG docker $USER
sudo su - $USER

echo "=============== Run local docker registry on port 5000"
docker run -d -p 5000:5000 --restart=always --name docker_registry registry:2.7.1

echo "=============== Installing docker-compose"
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "=============== Installing tutor"
export TUTOR_VERSION="$(curl -sSL https://api.github.com/repos/regisb/tutor/releases/latest | grep tag_name | sed "s/.*tag_name\": \"\(.*\)\",/\1/g")"
sudo curl -L "https://github.com/regisb/tutor/releases/download/$TUTOR_VERSION/tutor-$(uname -s)_$(uname -m)" -o /usr/local/bin/tutor
sudo chmod +x /usr/local/bin/tutor

echo "=============== Pulling vendor docker images"
tutor config save --yes
tutor images pull elasticsearch
tutor images pull memcached
tutor images pull mongodb
tutor images pull mysql
tutor images pull nginx
tutor images pull rabbitmq
tutor images pull smtp

echo "=============== Tagging vendor docker images"
docker tag $(tutor config printvalue DOCKER_IMAGE_ELASTICSEARCH) localhost:5000/$(tutor config printvalue DOCKER_IMAGE_ELASTICSEARCH)
docker tag $(tutor config printvalue DOCKER_IMAGE_MEMCACHED) localhost:5000/$(tutor config printvalue DOCKER_IMAGE_MEMCACHED)
docker tag $(tutor config printvalue DOCKER_IMAGE_MONGODB) localhost:5000/$(tutor config printvalue DOCKER_IMAGE_MONGODB)
docker tag $(tutor config printvalue DOCKER_IMAGE_MYSQL) localhost:5000/$(tutor config printvalue DOCKER_IMAGE_MYSQL)
docker tag $(tutor config printvalue DOCKER_IMAGE_SMTP) localhost:5000/$(tutor config printvalue DOCKER_IMAGE_SMTP)
docker tag $(tutor config printvalue DOCKER_IMAGE_NGINX) localhost:5000/$(tutor config printvalue DOCKER_IMAGE_NGINX)
docker tag $(tutor config printvalue DOCKER_IMAGE_RABBITMQ) localhost:5000/$(tutor config printvalue DOCKER_IMAGE_RABBITMQ)

echo "=============== Pushing vendor docker images to the local registry"
docker push localhost:5000/$(tutor config printvalue DOCKER_IMAGE_ELASTICSEARCH)
docker push localhost:5000/$(tutor config printvalue DOCKER_IMAGE_MEMCACHED)
docker push localhost:5000/$(tutor config printvalue DOCKER_IMAGE_MONGODB)
docker push localhost:5000/$(tutor config printvalue DOCKER_IMAGE_MYSQL)
docker push localhost:5000/$(tutor config printvalue DOCKER_IMAGE_SMTP)
docker push localhost:5000/$(tutor config printvalue DOCKER_IMAGE_NGINX)
docker push localhost:5000/$(tutor config printvalue DOCKER_IMAGE_RABBITMQ)

echo "=============== Building openedx docker images"
tutor config save --yes --set ACTIVATE_NOTES=true --set ACTIVATE_XQUEUE=true --set DOCKER_REGISTRY=localhost:5000/
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
User=$USER
WorkingDirectory=/home/$USER
Environment=HOME=/home/$USER
Environment=TUTOR_DOCKER_REGISTRY=localhost:5000/
ExecStart=/usr/local/bin/tutor-webui
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/tutor-webui.service
sudo systemctl enable tutor-webui

echo "=============== Clean tutor environment, configuration and data"
sudo rm -rf $(tutor config printroot)

echo "=============== Clean authorized keys"
sudo find / -name "authorized_keys" -exec rm -f {} \;

echo "=============== Clean history"
sudo find /root/.*history /home/*/.*history -exec rm -f {} \;
