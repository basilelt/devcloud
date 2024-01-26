apt update -y && apt upgrade -y && apt full-upgrade -y && apt dist-upgrade -y && apt autoclean -y && apt clean -y && apt autoremove -y
apt install -y docker.io git open-vm-tools openssh-client docker-compose sudo net-tools
usermod -aG docker $USER

hostnamectl set-hostname bdd.g1.local

cat > /etc/systemd/system/bdd.service <<EOF
[Unit]
Description=bdd service with docker compose
PartOf=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/home/web/devcloud/bdd
ExecStart=/usr/bin/docker-compose up -d --remove-orphans --build
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

systemctl enable bdd.service
systemctl daemon-reload

sudo -u web git clone https://@github.com/basilelt/devcloud
cd /home/web/devcloud/bdd

systemctl start bdd.service
