#! /bin/bash
# Clean an AWS instance so that it becomes ready for creating an AMI
# See https://aws.amazon.com/articles/how-to-share-and-use-public-amis-in-a-secure-manner/
# Run with: curl -sSL https://raw.githubusercontent.com/regisb/tutor/master/cloud/clean.sh | bash -e
echo "=============== Clean authorized keys"
sudo find / -name "authorized_keys" -exec rm -f {} \;

echo "=============== Clean history"
sudo find /root/.*history /home/*/.*history -exec rm -f {} \;
