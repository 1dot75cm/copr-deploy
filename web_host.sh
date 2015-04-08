#!/bin/bash
BUILD_IP="192.168.1.0/24"

# config sshd
ssh-keygen -f buildsys
cp buildsys.pub docker/
cp buildsys.pub ansible/roles/copr/docker/backend/files/provision/files/buildsys.pub
cp buildsys ansible/roles/copr/docker/backend/files/provision/files/buildsys.priv

# create user
useradd copr
mkdir -p /home/copr/.ssh

# config sudoer
sed -i '/requiretty/s|^|#|' /etc/sudoers
echo -e "copr\tALL=(ALL)\tNOPASSWD:ALL" > /etc/sudoers.d/users

# config network
iptables -t nat -A POSTROUTING -s $BUILD_IP -o eth0 -j MASQUERADE
echo "iptables -t nat -A POSTROUTING -s $BUILD_IP -o eth0 -j MASQUERADE" >> /etc/rc.local
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf; sysctl -p

# docker repos
wget https://copr.fedoraproject.org/coprs/mosquito/docker/repo/epel-7/mosquito-docker-epel-7.repo -O /etc/yum.repos.d/mosquito-docker-epel-7.repo

# system update
yum install centos-release epel-release vim tree lsof ntp bridge-utils bind-utils net-tools time wget rsync mailx elinks traceroute docker ansible ansible-lint sshpass fail2ban mosh tuned-utils tcpdump strace cronie
mv /etc/yum.repos.d/CentOS-Base.repo.rpmnew /etc/yum.repos.d/CentOS-Base.repo
mv /etc/yum.repos.d/epel.repo.rpmnew /etc/yum.repos.d/epel.repo

# enable some service
systemctl enable fail2ban tuned docker rc-local

# config fail2ban
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.d/sshd.local
sed -i '/Comments/i[sshd]\nenabled = true' /etc/fail2ban/jail.d/sshd.local
systemctl start fail2ban
fail2ban-client start sshd

# config tuned
tuned-adm profile network-latency

# build docker container
systemctl start docker
docker pull fedora
docker pull fedora:21
docker build -f docker/Dockerfile -t systemd:unpriv .
docker build -f docker/Dockerfile_httpd -t httpd:unpriv .

# create docker container
docker run -d -p 80:80 -p 443:443 --hostname=copr.fdzh.org --name copr-fe \
-v /sys/fs/cgroup:/sys/fs/cgroup:ro \
-v /data/log/copr-fe:/var/log \
-v /data/conf/httpd:/etc/httpd/conf.d \
-v /data/conf/copr-fe:/etc/copr \
-v /data/static/html:/usr/share/copr/coprs_frontend/coprs/templates \
-v /data/static/other:/usr/share/copr/coprs_frontend/coprs/static \
-v /data/webroot:/var/lib/copr \
-v /data/dbdata:/var/lib/pgsql \
-v /data/mail:/var/mail \
-m 1024m --memory-swap=1280m \
httpd:unpriv

docker run -d --name copr-be \
-v /sys/fs/cgroup:/sys/fs/cgroup:ro \
-v /data/log/copr-be:/var/log \
-v /data/conf/copr-be:/etc/copr \
-v /data/webroot:/var/lib/copr \
-v /data/conf/ansible:/home/copr/provision \
-m 1024m --memory-swap=1280m \
systemd:unpriv

docker run -d -p 8080:80 -p 2003:2003 -m 1024m --name=graphite \
--cap-add=net_broadcast --cap-add=net_admin --cap-add=sys_admin \
-v /sys/fs/cgroup:/sys/fs/cgroup:ro systemd:unpriv

## Graphite configuration ##
# yum install graphite-web python-whisper python-carbon
# cd /usr/lib/python2.7/site-packages/graphite
# cp local_settings.py.example local_settings.py
# python manage.py syncdb  # 初始化数据库
# python manage.py createsuperuser  # 创建管理员
# vi /etc/httpd/conf.d/graphite-web.conf  # 酌情修改配置
# chown apache:apache /var/lib/graphite-web/graphite.db
# systemctl start httpd
# systemctl start carbon-cache
# 最后在目标机安装 Collectd，并配置数据发送至 graphite 的 2003 端口即可

# postgres backup
#echo '0 0 * * * /usr/bin/docker exec copr-fe su -c - postgres "backup-database coprdb"' > /etc/cron.d/cron-backup-database-coprdb
#echo '0 * * * * /usr/bin/docker exec copr-fe su -c - postgres "clean-task"' >> /etc/cron.d/cron-backup-database-coprdb
#crontab /etc/cron.d/cron-backup-database-coprdb
#systemctl restart crond
