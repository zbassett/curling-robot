from channels import Group
from channels.sessions import channel_session

# Connected to websocket.connect
def ws_add(message):
    label = message['path'].strip('/').split('/')
    message.reply_channel.send({"accept": True})
    Group(message['path'].strip('/')).add(message.reply_channel)

# Connected to websocket.receive
def ws_message(message):
    Group("chat").send({
        "text": "[user] %s" % message.content['text'],
    })

# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("chat").discard(message.reply_channel)