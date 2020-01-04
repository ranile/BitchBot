result=$(git pull)
if [[ $result == "Already up to date." ]]; then
  echo Already up to date. No need to redeploy
  echo Exiting...
  exit 0
fi

docker stop bitch_bot
docker rm bitch_bot
docker build -t bitch_bot .
docker run -d --network=host --name=bitch_bot bitch_bot
echo Sucessfully deployed