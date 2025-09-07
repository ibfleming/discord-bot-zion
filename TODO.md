- Kick bot out of voice channel after inactivity

docker build -t zion-discord-bot .
docker login
docker tag zion-discord-bot ibfleming/zion-discord-bot:latest
docker push ibfleming/zion-discord-bot:latest

USERNAME=ibfleming
APP=zion-discord-bot
docker build -t $ .
docker tag my-app $USERNAME/$APP:1.0.1
docker push $USERNAME$/$APP:1.0.1