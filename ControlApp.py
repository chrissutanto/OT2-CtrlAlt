from flask import Flask, render_template, url_for, flash
from GetDrive import getProtocol, getProtocolList, getDownload
from OT2Control import sendOT2, saveHistory
from ScriptHandler import findLabware, findPipettes, findMetadata

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd0080a835082e8d2cb14d386'

def sampleText():
    return "hi"

@app.route('/')
def home():
    items = getProtocolList()
    return render_template('home.html', items=items)

@app.route('/protocol/<protocol_id>')
def protocolPage(protocol_id):
    protocol = getProtocol(protocol_id)
    getDownload(protocol_id)
    labware = findLabware(protocol_id)
    pipettes = findPipettes(protocol_id)
    metadata = findMetadata(protocol_id)
    return render_template('protocol.html', id=protocol_id, name=protocol['name'], modifiedTime=protocol['modifiedTime'], pipettes=pipettes, labware=labware, metadata=metadata)

@app.route('/send/<protocol_id>')
def sendPage(protocol_id):
    protocol = getProtocol(protocol_id)
    sendOT2(protocol)
    return render_template('send.html', id=protocol_id, name=protocol['name'])


if __name__== '__main__':
    app.run(debug=True)

 