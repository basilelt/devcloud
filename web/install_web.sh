apt update -y && apt upgrade -y && apt full-upgrade -y && apt dist-upgrade -y && apt autoclean -y && apt clean -y && apt autoremove -y
apt install -y docker.io git open-vm-tools openssh-client docker-compose sudo net-tools
usermod -aG docker $USER

hostnamectl set-hostname web.g1.local

cat > /etc/systemd/system/web.service <<EOF
[Unit]
Description=web service with docker compose
PartOf=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/home/web/devcloud/web
ExecStart=/usr/bin/docker-compose up -d --remove-orphans --build
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

systemctl enable web.service
systemctl daemon-reload

sudo -u web git clone https://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@github.com/basilelt/devcloud
cd /home/web/devcloud/web

systemctl start web.service
