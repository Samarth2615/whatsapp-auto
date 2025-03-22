from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers import YowLayerEvent
from yowsup.stacks import YowStackBuilder
from yowsup.layers.network import YowNetworkLayer
from flask import Flask
import threading

app = Flask(__name__)

CREDENTIALS = ("919253323008", "YOURPASSWORD")  # Replace YOURPASSWORD

class EchoLayer(YowInterfaceLayer):
    def __init__(self):
        super(EchoLayer, self).__init__()
        self.connected = False

    @ProtocolEntityCallback("success")
    def on_success(self, success_entity):
        self.connected = True
        print("Connected to WhatsApp")

    @ProtocolEntityCallback("failure")
    def on_failure(self, failure_entity):
        print("Connection failed")

    def send_message(self, number, content):
        if self.connected:
            message_entity = TextMessageProtocolEntity(content, to=number)
            self.toLower(message_entity)

def start_whatsapp():
    stackBuilder = YowStackBuilder()
    stack = stackBuilder.pushDefaultLayers(True).push(EchoLayer()).build()
    stack.setCredentials(CREDENTIALS)
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
    stack.loop(timeout=5, discrete=0.5)
    return stack.getLayer(-1)

whatsapp_layer = None

@app.route('/send_yes')
def send_yes():
    global whatsapp_layer
    if whatsapp_layer and whatsapp_layer.connected:
        whatsapp_layer.send_message("GROUP_JID", "Yes")  # Replace GROUP_JID
        return "Sent 'Yes' to the group!"
    return "WhatsApp not connected!"

if __name__ == "__main__":
    whatsapp_thread = threading.Thread(target=lambda: globals().update(whatsapp_layer=start_whatsapp()))
    whatsapp_thread.daemon = True
    whatsapp_thread.start()
    app.run(host="0.0.0.0", port=5000)
