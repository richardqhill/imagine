# imagine
<h1 align="center"><img src="https://raw.githubusercontent.com/richardqhill/imagine/main/docs/static/imagine.webp" alt="imagine logo" width="32"/>   /imagine</h1>

A basic slack app that generate images using text prompts
- Interface inspired by the giphy slack app
- Built using Slack's Bolt python framework
- Image generation using SDXL model hosted on replicate.com
- Uses flask, gunicorn, nginx, and ngrok



## Example

<img src="https://raw.githubusercontent.com/richardqhill/imagine/main/docs/static/example.webp">

## Setup

* follow these instructions to get your Slack bot token and signing secret: 
 https://api.slack.com/tools/bolt-python

* setup your .env file:
```bash
SLACK_BOT_TOKEN=XXXXX
SLACK_SIGNING_SECRET=XXXXX
REPLICATE_API_TOKEN=XXXXX
NGROK_DOMAIN=XXXXX.ngrok.io
NGROK_AUTHTOKEN=XXXXX
```

* run the app:
```bash
docker compose up
```