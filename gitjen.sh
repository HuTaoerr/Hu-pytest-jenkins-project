git add .
git commit -m "update"
git push origin master


docker stop myjenkins
docker rm myjenkins

docker run \
  -d \
  -p 8100:8080 \
  -p 50000:50000 \
  --name myjenkins \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myjenkins-with-docker-cli
