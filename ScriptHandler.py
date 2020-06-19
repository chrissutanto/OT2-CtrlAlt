import re

# Protocol must contain item type and location in same line, location must be defined in the load statement

# Takes protcol ID, returns lines of script
def getLines(protocol_id):
    file = open('protocol_files/{}.py'.format(protocol_id))
    lines = file.readlines()
    return lines

# Takes line containing item info, returns dictionary of {location:item}
def getItem(line):
    pattern = "'(.*?)'"
    item = re.search(pattern, line)[1]
    afterComma = line[line.find(","):]
    location = re.search(pattern, afterComma)[1]
    return {'location': location, 'item': item}

# Takes labware, returns deck location, used to sort list of labware in order of deck location
def getLocation(labware):
    return labware['location']

# Takes protocol ID, returns list of dict containing labware info
def findLabware(protocol_id):
    labware = []
    lines = getLines(protocol_id)
    for i in range(len(lines)):
        if "protocol.load_labware" in lines[i]:
            if "'" in lines[i]:
                new_item = getItem(lines[i])
            elif "'" in lines[i+1]:
                new_item = getItem(lines[i+1])
            labware.append(new_item)
    labware.sort(key=getLocation)
    return labware

# Takes protocol ID, returns list of dict containing pipette info
def findPipettes(protocol_id):
    pipettes = []
    lines = getLines(protocol_id)
    for i in range(len(lines)):
        if "protocol.load_instrument" in lines[i]:
            if "'" in lines[i]:
                new_item = getItem(lines[i])
            elif "'" in lines[i+1]:
                new_item = getItem(lines[i+1])
            pipettes.append(new_item)
    return pipettes