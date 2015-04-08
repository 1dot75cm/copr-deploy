FROM fedora:21
MAINTAINER mosquito <sensor.wen@gmail.com>
ENV container docker

RUN yum update -y && yum clean all
RUN yum install -y systemd openssh-server openssh-clients initscripts rsyslog \
    wget iputils iproute net-tools passwd hostname bind-utils dnf dnf-plugins-core \
    yum-plugin-fastestmirror && yum clean all

RUN systemctl mask dev-mqueue.mount dev-hugepages.mount \
    systemd-remount-fs.service sys-kernel-config.mount \
    sys-kernel-debug.mount sys-fs-fuse-connections.mount \
    display-manager.service systemd-logind.service tmp.mount console-getty.service
RUN systemctl set-default multi-user.target
RUN systemctl enable sshd rsyslog

ADD dbus.service /etc/systemd/system/dbus.service

RUN mkdir -p /var/run/sshd /root/.ssh
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN sed -i 's|UsePrivilegeSeparation sandbox|UsePrivilegeSeparation no|' /etc/ssh/sshd_config
ADD buildsys.pub /root/.ssh/authorized_keys
RUN echo "root:redhat" | chpasswd
RUN cp /etc/skel/.bash* /root/
RUN rm -f /etc/localtime; ln -s /usr/share/zoneinfo/UTC /etc/localtime

VOLUME ["/sys/fs/cgroup"]
VOLUME ["/run"]
CMD ["/usr/lib/systemd/systemd"]
