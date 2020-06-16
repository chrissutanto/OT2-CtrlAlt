from flask import Flask, render_template, url_for
from GetDrive import getProtocol, getName

app = Flask(__name__)


def sampleText():
    return "hi"

@app.route('/')
def home():
    items = getProtocol()
    print(items[1]['id'])
    return render_template('home.html', items=items)

@app.route('/<protocol_id>')
def protocolPage(protocol_id):
    protocol_name = getName(protocol_id)
    return render_template('protocol.html', id=protocol_id, name=protocol_name)

if __name__== '__main__':
    app.run(debug=True)

 