import os
from slack_bolt import App
from dotenv import load_dotenv

from broker import cloudamqp

# Load environment variables from .env file
load_dotenv()

# Initializes your app with your bot token and socket mode handler
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


@app.event("app_mention")
def handle_app_mention(event) -> None:
    """ 
        Event handler - Invoked when the bot app is mentioned in a slack channel
        This function publishes the message it receives from Slack to a LavinMQ
        instance on CloudAMQP

        Args:
        - event
        - say
    """
    message = event["text"]
    user = event["user"]
    channel = event["channel"]
    thread_ts = event["ts"]

    # Publish message to the LavinMQ instance on CloudAMQP
    cloudamqp.publish_message(
        message_body= {
            "prompt": message,
            "user": user,
            "channel": channel,
            "thread_ts": thread_ts
        }
    )
    
    
@app.event("message")
def handle_message_events(body, logger):
    pass


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))