from flask import Flask, render_template, url_for, flash, request, redirect
from GetDrive import getProtocol, getProtocolList, getDownload, deleteProtocolFiles, getWellMapList, getWellMap
from GetSheet import saveHistory, getWellMapData
from ScriptHandler import findLabware, findPipettes, findMetadata, findModFields, editModFields, editScriptRTPCR, simulateProtocol, editLabware
from InterfaceOT2 import sendProtocol, setIP, getIP, firstTimeSetup
import os.path
from Forms import modifyForm, LabwareForm
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

@app.route('/send/<protocol_id>', methods=['post', 'get'])
def sendPage(protocol_id):
    protocol = getProtocol(protocol_id)
    wellmap = None
    modfields = []
    modFields = findModFields(protocol_id)

    fields = ['description']
    form = modifyForm(fields = fields)
    if form.validate_on_submit():
        results = []
        for data in enumerate(form.fields.data):
            results.append(data)
        sendProtocol(protocol)
        saveHistory(protocol, wellmap, modFields, results)
        return render_template('send.html', id = protocol_id, name=protocol['name'])
    return render_template('description.html', id=protocol_id, name=protocol['name'], form = form)

@app.route('/send/<protocol_id>/<wellmap_id>', methods=['post', 'get'])
def sendPageWellMap(protocol_id, wellmap_id):
    protocol = getProtocol(protocol_id)
    wellmap = getWellMap(wellmap_id)
    name = protocol['name'] + " with " + wellmap['name']
    modfields = []
    modFields = findModFields(protocol_id)

    fields = ['description']
    form = modifyForm(fields = fields)
    if form.validate_on_submit():
        results = []
        for data in enumerate(form.fields.data):
            results.append(data)
        sendProtocol(protocol)
        saveHistory(protocol, wellmap, modFields, results)
        return render_template('send.html', id = protocol_id, name=protocol['name'])
    return render_template('description.html', id=protocol_id, name=name, form = form)

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
    return render_template('wellmap.html', protocol_id=protocol_id, protocol_name=protocol['name'], wellmap_id=wellmap_id, wellmap_name=wellmap['name'], modifiedTime=wellmap['modifiedTime'], wellmapdata=wellmapdata)

@app.route('/wellmap/<protocol_id>/<wellmap_id>/confirm')
def wellMapConfirm(protocol_id, wellmap_id):
    protocol = getProtocol(protocol_id)
    wellmap = getWellMap(wellmap_id)
    wellmapdata = getWellMapData(wellmap_id)
    editScriptRTPCR(protocol_id, wellmapdata)
    modfields = []
    modFields = findModFields(protocol_id)
    return render_template('confirm.html', protocol_id=protocol_id, protocol_name=protocol['name'],  modifiedTimeProtocol=protocol['modifiedTime'], wellmap_id=wellmap_id, wellmap_name=wellmap['name'], wellmapdata=wellmapdata,  modifiedTimeWellmap=wellmap['modifiedTime'], modFields=modFields)

@app.route('/confirm/<protocol_id>')
def protocolConfirm(protocol_id):
    protocol = getProtocol(protocol_id)
    modfields = []
    modFields = findModFields(protocol_id)
    return render_template('confirm.html', protocol_id=protocol_id, protocol_name=protocol['name'], modifiedTimeProtocol=protocol['modifiedTime'], wellmap_info=None, wellmap_name=None, wellmapdata=None, modFields=modFields)

@app.route('/simulate/<protocol_id>')
def simulatePage(protocol_id):
    simulationLog = simulateProtocol(protocol_id)
    protocol = getProtocol(protocol_id)
    return render_template('simulate.html', simulationLog=simulationLog, protocol_id=protocol_id, protocol_name=protocol['name'])

@app.route('/options')
def optionsPage():
    return render_template('options.html')

@app.route('/history')
def historyPage():
    return render_template('history.html')

@app.route('/firstTimeSetup')
def firstConnection():
    firstTimeSetup()
    return redirect(url_for('home'))

@app.route('/deleteProtocol')
def deletePage():
    deleteProtocolFiles()
    message = 'Protocol cache deleted'
    return redirect(url_for('home'))

@app.route('/connection', methods=['post', 'get'])
def setupConnection():
    fields = ['ip']
    form = modifyForm(fields = fields)
    if form.validate_on_submit():
        results = []
        for data in enumerate(form.fields.data):
            results.append(data)
        setIP(results)
        return redirect(url_for('home'))
    return render_template('connection.html', form=form)

@app.route('/editLabware/<protocol_id>', methods=['post', 'get'])
def editLabwarePage(protocol_id):
    labwareForm = LabwareForm()
    labwareResults = None
    labware = findLabware(protocol_id)
    if labwareForm.validate_on_submit():
        labwareResultsSource = labwareForm.source.data
        labwareResultsDestination = labwareForm.destination.data
        editLabware(labwareResultsSource, labwareResultsDestination, protocol_id)
        return redirect(url_for('protocolPage', protocol_id=protocol_id))
    print('submission not validated')
    print(labwareForm.errors)
    protocol = getProtocol(protocol_id)
    return render_template('editLabware.html', id=protocol_id, name=protocol['name'], form=labwareForm, labware=labware)


@app.route('/modify/<protocol_id>', methods=['post', 'get'])
def modifyPage(protocol_id):
    modFields = findModFields(protocol_id)
    # fields = []
    # for field in modFields:
    #     fields.append(field['value'])
    form = modifyForm(fields=modFields)
    if form.validate_on_submit():
        results = []
        for data in enumerate(form.fields.data):
            results.append(data)
        editModFields(protocol_id, results)
        return redirect(url_for('protocolPage', protocol_id=protocol_id))
    protocol = getProtocol(protocol_id)
    return render_template('modify.html', id=protocol_id, name=protocol['name'], form=form, modFields=modFields)

if __name__== '__main__':
    app.run(debug=True)

 