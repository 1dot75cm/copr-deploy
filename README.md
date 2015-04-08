# copr-deploy
Deploy your Copr build service

## Copr 架构

![arch](https://raw.githubusercontent.com/1dot75cm/copr-deploy/master/snapshot/copr_arch.png)

## 文件说明

- ansible/： ansible 脚本
- docker/： Dockerfile 文件
- *.sh： 准备环境的脚本

## 安装步骤

1. 克隆 git 库
> ```
> # cd /mnt
> # git clone https://github.com/1dot75cm/copr-deploy
> ```

2. 创建虚拟机    
创建一台虚拟机作为 Builder。如果你不想在物理机中部署 Web 部分，则需要创建另一台虚拟机来运行 Docker。

3. 依次检查/执行 *.sh 脚本，来准备环境
> ```
> # sh web_host.sh  # 在作为 Web 的物理机中执行
> # sh build_host.sh  # 在作为 Builder 的虚拟机中执行
> # sh sshkeys.sh  # 在作为 Web 的物理机中执行
> ```

4. 部署 Copr 至 Docker   
检查容器 IP 并写入 ansible/hosts。   
配置 ansible/ansible.cfg 中 roles_path 的路径，为 ansible/roles 的绝对路径。   
配置 ansible/vars/global.yml 中的相关变量（容器 IP 地址）。
> ```
> # cd ansible
> # ansible-playbook -i hosts master.yml -k
> ```
