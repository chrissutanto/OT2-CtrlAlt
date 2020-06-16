from flask import Flask, render_template
from GetDrive import getProtocol

app = Flask(__name__)


def sampleText():
    return "hi"

@app.route('/')
def home():
    getProtocol()
    return render_template('home.html')

if __name__== '__main__':
    app.run(debug=True)

 