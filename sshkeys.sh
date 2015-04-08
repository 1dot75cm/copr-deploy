#!/bin/bash
WEB_IP="10.x.x.x"
BUILD_IP="10.8.7.209"

# copr-be(root) -> copr-be(copr)
docker exec copr-be cp /home/copr/.ssh/id_rsa /root/.ssh/

# copr-be(copr) -> builder(root)
scp roles/copr/docker/backend/files/provision/files/buildsys.pub root@$BUILD_IP:~/.ssh/authorized_keys

# copr-be(copr) -> web(copr)
mkdir -p /home/copr/.ssh
cp roles/copr/docker/backend/files/provision/files/buildsys.pub /home/copr/.ssh/authorized_keys
chown copr:copr /home/copr/.ssh/authorized_keys

# copr-be(copr) -> builder(container)

# builder(root) -> web(copr)
scp roles/copr/docker/backend/files/provision/files/buildsys.priv root@$BUILD_IP:~/.ssh/id_rsa
