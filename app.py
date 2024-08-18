import os
import json
from slack_bolt import App
import replicate

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

def generate_blocks(command_text):
    output = replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={"prompt": command_text}
    )

    image_url = output[0]

    return [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": command_text
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
                "value": json.dumps({ "url": image_url, "title": command_text}),
                "style": "primary",
                "action_id": "send"
                },
                {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Retry"
                },
                "value": "retry",
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
def repeat_text(ack, command, client):
    ack()        
    client.chat_postEphemeral(                       
        token=os.environ.get("SLACK_BOT_TOKEN"),
        channel=command['channel_id'],
        user=command['user_id'],
        text=command['text'],
        blocks=generate_blocks(command['text'])
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
def retry_ephem_message(ack, respond):
    ack()
    blocks=generate_blocks('retry')
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

    # extract image url and image title from action value
    actionValue = json.loads(action["value"])
    image_url = actionValue["url"]
    title = actionValue["title"]
    if not image_url or not title:
        return

    blocks = [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": title
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
        text=title,
        blocks=blocks,
        username=profile.data['profile']['display_name_normalized'],
        icon_url=profile.data['profile']['image_512'],
    )


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
