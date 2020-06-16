from flask import Flask, render_template
from GetDrive import getProtocol

app = Flask(__name__)


def sampleText():
    return "hi"

@app.route('/')
def home():
    items = getProtocol()
    return render_template('home.html', items=items)

if __name__== '__main__':
    app.run(debug=True)

 