# Realtime Chat App

A full-featured real-time chat application built with FastAPI and WebSockets, containerized with Docker, and deployed on Railway. Features authentication, emoji reactions, reply-to-message, and dark/light mode.

## Live Demo

https://realtime-chat-production-7d6d.up.railway.app

Open the link on two different devices simultaneously and chat in real time — no refresh needed, messages appear instantly.

## Features

- Real-time messaging via WebSockets — persistent bidirectional connection, no polling
- Username and password authentication — new users are registered automatically, returning users are verified
- Reply to specific messages — hover any message and click the reply button
- Emoji reactions — react to any message with 12 emoji options
- Dark and light mode — toggle from the header or settings menu
- Online users bar — see who is currently in the chat room with their avatar color
- Sound notifications — subtle ping on new messages (toggleable)
- Hamburger menu — settings, profile, and help panel
- Fully responsive — works on mobile and desktop
- Sound notification toggle in settings

## Tech Stack

- FastAPI - Python web framework with built-in WebSocket support
- WebSockets - persistent bidirectional connection protocol for real-time communication
- Docker - containerization for consistent deployment
- GitHub Actions - CI/CD pipeline that builds and tests on every push
- Railway - cloud deployment platform

## How WebSockets Work Here

Normal HTTP closes the connection after each request. WebSockets keep the connection permanently open, like a phone call that stays connected. When a user sends a message, it goes to the server instantly, and the server broadcasts it to every connected client simultaneously — all in milliseconds.

## Running Locally with Docker

1. Clone the repo:
git clone https://github.com/Qayyum404/realtime-chat.git
cd realtime-chat

2. Build and run:
docker build -t realtime-chat .
docker run -d -p 8000:8000 realtime-chat

3. Open in browser:
http://localhost:8000

4. Open a second tab with a different username and start chatting.

## CI/CD

Every push to main automatically builds the Docker image and runs a smoke test via GitHub Actions. Railway also auto-deploys on every successful push.

## Architecture

Client (Browser) ←→ WebSocket Connection ←→ FastAPI Server
                                                    ↓
                                         ConnectionManager
                                         (tracks all active
                                          connections in memory)
                                                    ↓
                                    Broadcasts to all connected clients
