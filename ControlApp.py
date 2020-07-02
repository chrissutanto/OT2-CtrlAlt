from flask import Flask, render_template, url_for, flash, request, redirect
from GetDrive import getProtocol, getProtocolList, getDownload, deleteProtocolFiles, getWellMapList, getWellMap
from GetSheet import sendOT2, saveHistory, getWellMapData
from ScriptHandler import findLabware, findPipettes, findMetadata, findModFields, editModFields
import os.path
from Forms import modifyForm
from flask_wtf import Form


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
    if not os.path.exists('protocol_files/{}.py'.format(protocol_id)):
        getDownload(protocol_id)
    labware = findLabware(protocol_id)
    pipettes = findPipettes(protocol_id)
    metadata = findMetadata(protocol_id)
    modFields = []
    wellmap = 'false'
    for data in metadata:
        if data['field'].lower() == 'modify':
            if data['value'].lower() == 'true':
                modFields = findModFields(protocol_id)
        if data['field'].lower() == 'well-map':
            if data['value'].lower() == 'true':
                wellmap = 'true'
    return render_template('protocol.html', id=protocol_id, name=protocol['name'], modifiedTime=protocol['modifiedTime'], pipettes=pipettes, labware=labware, metadata=metadata, modFields=modFields, wellmap=wellmap)

@app.route('/send/<protocol_id>')
def sendPage(protocol_id):
    protocol = getProtocol(protocol_id)
    wellmap = None
    sendOT2(protocol, wellmap)
    return render_template('send.html', id=protocol_id, name=protocol['name'])

@app.route('/send/<protocol_id>/<wellmap_id>')
def sendPageWellMap(protocol_id, wellmap_id):
    protocol = getProtocol(protocol_id)
    wellmap = getWellMap(wellmap_id)
    name = protocol['name'] + " with " + wellmap['name']
    sendOT2(protocol, wellmap)
    return render_template('send.html', id=protocol_id, name=name)

@app.route('/wellmapselect/<protocol_id>')
def wellMapSelectPage(protocol_id):
    protocol = getProtocol(protocol_id)
    items = getWellMapList()
    return render_template('wellmapselect.html', id=protocol_id, name=protocol['name'], items=items)

@app.route('/wellmap/<protocol_id>/<wellmap_id>')
def wellMapPage(protocol_id, wellmap_id):
    protocol = getProtocol(protocol_id)
    wellmap = getWellMap(wellmap_id)
    wellmapdata = getWellMapData(wellmap_id)
    # publishDoc(wellmap_id)
    return render_template('wellmap.html', protocol_id=protocol_id, protocol_name=protocol['name'], wellmap_id=wellmap_id, wellmap_name=wellmap['name'], modifiedTime=wellmap['modifiedTime'], wellmapdata=wellmapdata)

@app.route('/options')
def optionsPage():
    return render_template('options.html')

@app.route('/deleteProtocol')
def deletePage():
    deleteProtocolFiles()
    message = 'Protocol cache deleted'
    return render_template('confirm.html', message=message)

@app.route('/modify/<protocol_id>', methods=['post', 'get'])
def modifyPage(protocol_id):
    modFields = findModFields(protocol_id)
    fields = []
    for field in modFields:
        fields.append(field['value'])
    form = modifyForm(fields=modFields)
    if form.validate_on_submit():
        results = []
        for data in enumerate(form.fields.data):
            results.append(data)
        print(results)
        editModFields(protocol_id, results)
        return redirect(url_for('protocolPage', protocol_id=protocol_id))
    protocol = getProtocol(protocol_id)
    return render_template('modify.html', id=protocol_id, name=protocol['name'], form=form, modFields=modFields)

if __name__== '__main__':
    app.run(debug=True)

 