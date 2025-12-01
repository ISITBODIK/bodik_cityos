# almalinux update
sudo dnf update -y

# 各種ツール
sudo dnf install -y tar wget bind-utils net-tools traceroute lsof vim rsync nfs-utils unzip

# gitインストール
sudo yum install -y git

# リポジトリ追加
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# dockerインストール
sudo dnf -y install docker-ce

# 起動と自動起動
sudo systemctl enable docker
sudo systemctl start docker
# docker userに追加
sudo usermod -aG docker ${USER}

## docker-compose
#sudo wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.32.1/docker-compose-Linux-x86_64
# 権限設定
#sudo chmod +x /usr/local/bin/docker-compose
# python
sudo dnf -y install python3.12 python3.12-devel python3.12-pip
sudo alternatives --install /usr/bin/pip pip /usr/bin/pip3.12 30

## docker-compose
pip3 install docker-compose

# タイムゾーン設定
sudo timedatectl set-timezone Asia/Tokyo

#vim ~/.bashrc
#alias python="python3" 
#alias pip="pip3"

# set ssh keep alive
# sudo vi /etc/ssh/sshd_config
#  ClientAliveInterval 60
#  ClientAliveCountMax 3
# sudo systemctl restart sshd
