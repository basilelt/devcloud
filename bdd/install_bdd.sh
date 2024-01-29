apt update -y && apt upgrade -y && apt full-upgrade -y && apt dist-upgrade -y && apt autoclean -y && apt clean -y && apt autoremove -y
apt install -y docker.io git open-vm-tools openssh-client docker-compose sudo net-tools
usermod -aG docker $USER

cat > /etc/systemd/system/bdd.service <<EOF
[Unit]
Description=bdd service with docker compose
PartOf=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/home/bdd/devcloud/bdd
ExecStart=/usr/bin/docker-compose up -d --remove-orphans --build
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

systemctl enable bdd.service
systemctl daemon-reload

sudo -u bdd git clone https://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@github.com/basilelt/devcloud
cd /home/bdd/devcloud/bdd

systemctl start bdd.service
