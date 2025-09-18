# `ZION Discord Music Bot 🎵`

Welcome to **Magi of Zion**, the sleek and simple Discord music bot designed to bring your favorite tunes straight to your Discord channel!

---

## Features

- 🎶 **Play Music**: Stream music from YouTube, Spotify, and more.
- ⚡ **Fast and Reliable**: Low-latency playback for a smooth listening experience.
- 🎛 **Easy Controls**: Play, pause, skip, and stop commands at your fingertips.
- 🔊 **Seamless Queue Management**: Add, view, and manage your song queue effortlessly.
- 🎧 **High-Quality Audio**: Enjoy crisp and clear sound in your voice channels.

---

## How to Use

1. **Invite ZION** to your server.  
2. Join a voice channel.  
3. Use simple commands to control the music:  

| Command       | Description                                 |
| --------------|---------------------------------------------|
| `.play <url or title>` | Play a song or add it to the queue |
| `.volume`              | Pause the current song             |
| `.stop`                | Stop the music                     |

---

## Get Started

Invite ZION to your Discord channel and start playing your favorite tracks instantly!

---

## Support

Need help or want to suggest features? Feel free to open an issue or contact the maintainer.

---

*Let the music flow! 🎵*

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
