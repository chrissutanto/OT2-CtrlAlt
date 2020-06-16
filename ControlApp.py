from flask import Flask, render_template, url_for
from GetDrive import getProtocol, getProtocolList, getDownload

app = Flask(__name__)


def sampleText():
    return "hi"

@app.route('/')
def home():
    items = getProtocolList()
    return render_template('home.html', items=items)

@app.route('/<protocol_id>')
def protocolPage(protocol_id):
    protocol = getProtocol(protocol_id)
    getDownload(protocol_id)
    return render_template('protocol.html', id=protocol_id, name=protocol['name'], modifiedTime=protocol['modifiedTime'])

if __name__== '__main__':
    app.run(debug=True)

 