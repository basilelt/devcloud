mkdir /storage/nfs/website
mkdir /storage/nfs/website/volumes
mkdir /storage/nfs/website/volumes/static

git clone https://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@github.com/basilelt/devcloud

cp -R /storage/nfs/website/devcloud/web/django/django/G7/G7App/static/* /storage/nfs/website/volumes/static/
hostnamectl set-hostname web1g1
cd /storage/nfs/website/devcloud/web/

cat > /etc/docker/daemon.json <<EOF
{
  "insecure-registries" : ["10.129.4.176:5000"]
}
EOF
systemctl restart docker

docker swarm init
docker service create --name registry --publish published=5000,target=5000 registry:2

docker-compose build
docker-compose push
docker stack deploy --compose-file docker-compose.yml stackweb