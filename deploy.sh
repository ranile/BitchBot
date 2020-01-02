docker stop bitch_bot
docker rm bitch_bot
git pull
docker build -t bitch_bot .
docker run -d --network=host --name=bitch_bot bitch_bot
echo "Sucessfully deployed"