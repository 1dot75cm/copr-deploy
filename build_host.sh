#!/bin/bash
WEB_IP="10.8.14.105"
BUILD_IP="192.168.1.0/24"
HOSTNAME="Builder"
IP="10.8.7.209"
MASK="16"
GW="10.8.14.105"

# config sshd
# create .ssh dir
mkdir -p /root/.ssh

#mkdir -p /var/lib/docker/devicemapper/devicemapper
#echo '/dev/vdb /var/lib/docker/devicemapper/devicemapper xfs defaults,noatime 0 0' >> /etc/fstab
#umount /data
#mount -a

# config network
systemctl enable NetworkManager; systemctl restart NetworkManager
# create br0 interface
nmcli conn add type bridge ifname br0 con-name br0 save yes stp no ip4 $IP gw4 $GW
nmcli conn add type bridge-slave ifname eth0 master br0
nmcli conn mod br0 ipv4.addr "$IP/$MASK $GW"
nmcli conn mod br0 ipv4.dns "8.8.8.8 8.8.4.4 114.114.114.114"
nmcli conn up br0
nmcli conn down eth0
hostnamectl set-hostname "$HOSTNAME"

iptables -t nat -A POSTROUTING -s "$BUILD_IP" -o br0 -j MASQUERADE
echo "iptables -t nat -A POSTROUTING -s $BUILD_IP -o br0 -j MASQUERADE" >> /etc/rc.local
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf; sysctl -p

# docker repos
wget https://copr.fedoraproject.org/coprs/mosquito/docker/repo/epel-7/mosquito-docker-epel-7.repo -O /etc/yum.repos.d/mosquito-docker-epel-7.repo

# system update
yum install centos-release epel-release bridge-utils tuned-utils vim ntp net-tools time wget tcpdump strace cronie docker NetworkManager-tui elinks collectd
mv /etc/yum.repos.d/CentOS-Base.repo.rpmnew /etc/yum.repos.d/CentOS-Base.repo
mv /etc/yum.repos.d/epel.repo.rpmnew /etc/yum.repos.d/epel.repo

# enable some service
systemctl enable tuned docker collectd

# collectd config file
cat > /etc/collectd.d/copr.conf <<EOF
Hostname    "build"
Interval    10
LoadPlugin  write_graphite

<Plugin write_graphite>
  <Node "example">
    Host "10.8.14.105"
    Port "2003"
    Protocol "tcp"
#    LogSendErrors true
#    Prefix "collectd"
#    Postfix "collectd"
#    StoreRates true
#    AlwaysAppendDS false
#    EscapeCharacter "_"
  </Node>
</Plugin>
EOF
sed -i "/Host /s|\".*|\"$WEB_IP\"|" /etc/collectd.d/copr.conf
systemctl start collectd

# config tuned
tuned-adm profile throughput-performance

# build docker container
sed -i 's|=$|=--storage-opt dm.basesize=20G|' /etc/sysconfig/docker-storage
systemctl start docker
docker pull fedora
docker pull fedora:21
docker build -f docker/Dockerfile -t systemd:unpriv .
sed -i 's|=$|=-b=br0|' /etc/sysconfig/docker-network
systemctl restart docker
