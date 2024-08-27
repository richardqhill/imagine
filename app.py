import os
import json

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import replicate


app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


def generate_replicate_image(prompt_text: str):
    # return "https://archive.org/download/placeholder-image/placeholder-image.jpg"

    replicate_res = replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={"prompt": prompt_text}
    )
    return replicate_res[0]    

def generate_imagine_blocks(prompt_text: str):
    image_url = generate_replicate_image(prompt_text)
    return [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": prompt_text
            },
            "block_id": "generated image",
            "image_url": image_url,
            "alt_text": "generated image"
        },
        {
            "type": "actions",
            "block_id": "actions1",
            "elements": [
                {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Send"
                },
                "value": json.dumps({ "image_url": image_url, "prompt_text": prompt_text }),
                "style": "primary",
                "action_id": "send"
                },
                {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Retry"
                },
                "value": json.dumps({ "prompt_text": prompt_text }),
                "action_id": "retry"
                },
                {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "value": "cancel",
                "action_id": "cancel"
                }
            ]
        }]

@app.command("/imagine")
def handle_imagine(ack, command, client):
    ack()        
    client.chat_postEphemeral(                       
        token=os.environ.get("SLACK_BOT_TOKEN"),
        channel=command['channel_id'],
        user=command['user_id'],
        text=command['text'],
        blocks=generate_imagine_blocks(prompt_text=command['text'])
    )

@app.action("cancel")
def delete_ephem_message(ack, respond):
    ack()
    respond({
        "response_type": "ephemeral",
        "text": "",
        "replace_original": True,
        "delete_original": True
    })

@app.action("retry")
def retry_ephem_message(ack, respond, action):
    ack()

    actionValue = json.loads(action["value"])
    prompt_text = actionValue["prompt_text"]
    if not prompt_text:
        return

    blocks=generate_imagine_blocks(prompt_text)
    respond({
        "response_type": "ephemeral",
        "text": "retry",
        "blocks": blocks,
        "replace_original": True,
        "delete_original": True
    })
    
@app.action("send")
def post_ephem_message(ack, body, client, respond, action):
    delete_ephem_message(ack, respond)

    # extract image url and prompt text from the button action value
    actionValue = json.loads(action["value"])
    image_url = actionValue["image_url"]
    prompt_text = actionValue["prompt_text"]
    if not image_url or not prompt_text:
        return

    blocks = [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": prompt_text
            },
            "block_id": "generated image",
            "image_url": image_url,
            "alt_text": "generated image"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "image",
                    "image_url": "https://cdn.getgrow.io/images/favicon/imagine.webp",
                    "alt_text": "imagine logo"
                },
                {
                    "type": 'mrkdwn',
                    "text": "Posted using /imagine",
                }
            ]
        }
    ]

    # post as user by getting their display name and avatar (as_user parameter is deprecated)
    userID = body['user']['id']
    profile = client.users_profile_get(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        user=userID
    )

    if not profile._initial_data['ok']:
        return

    client.chat_postMessage(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        channel=body['container']['channel_id'],
        text=prompt_text,
        blocks=blocks,
        username=profile.data['profile']['display_name_normalized'],
        icon_url=profile.data['profile']['image_512'],
    )

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
