---
title: Flask
description: A popular minimal server framework for Python
tags:
  - python
  - flask
---

# Python Flask Example

This is a [Flask](https://flask.palletsprojects.com/en/1.1.x/) app that serves a simple JSON response.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/zUcpux)

## ✨ Features
- Python
- Flask

## 💁♀️ How to use
- make sure you have a .env file
- Build containers `docker compose build`
- Start containers `docker compose up`


### Forwarding webhooks
This app uses ngrok to forward webhooks from AssemblyAI. You can create your own ngrok account,
then update the `API_URL` in the .env file with the ngrok URL. (in production, `API_URL` is the app's actual URL)

## Commands
- Run Migrations `alembic upgrade head`
- Create migration `alembic revision --autogenerate -m "message"`
- Run ngrok (port forwarding for webhooks) `ngrok http --domain=flexible-cheaply-jay.ngrok-free.app 5003`
- Run celery (for async tasks) `celery -A main.celery worker --loglevel=info` (not needed w/ Docker)


## 📝 Notes
- Sometimes it seems like workers are not picking up jobs (message in console about logs being
mistimed). Solution has been to restart the redis server on Railway
