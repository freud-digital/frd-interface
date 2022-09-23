#/bin/bash
clear
docker container stop frd-int
docker build -t frd-int:latest .
echo "##################"
echo "##################"
docker run -d --rm --name frd-int -p 8020:8020 frd-int
docker container logs -f frd-int