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

# Takes line containing metadata info, returns dictionary of {field:value}
def getInfo(line):
    pattern = "'(.*?)'"
    field = re.search(pattern, line)[1]
    afterColon = line[line.find(":"):]
    value = re.search(pattern, afterColon)[1]
    return {'field': field, 'value': value}

# Takes line containing modifiable field, returns dictionary of {field:value}
def getField(line):
    field = line.split("=")[0].strip() 
    value = line.split("=")[1].strip()
    description = ""
    if "#" in value:
        description = value.split("#")[1].lstrip().capitalize()
        value = value.split("#")[0]
    return {'field': field, 'value': value, 'description': description}

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

# Takes protocol ID, returns list of dict containing metadata
def findMetadata(protocol_id):
    metadata = []
    lines = getLines(protocol_id)
    for i in range(len(lines)):
        if "metadata" in lines[i]:
            while not "}" in lines[i+1]:
                metadata.append(getInfo(lines[i+1]))
                i = i+1    
            break
    return metadata

# Returns modifiable fields and their default values
def findModFields(protocol_id):
    fields = []
    lines = getLines(protocol_id)
    for i in range(len(lines)):
        if "# modify" in lines[i]:
            while not "# end modify" in lines[i+1]:
                fields.append(getField(lines[i+1]))
                i = i+1
    return fields

# Takes list of tuples representing user input, updates script modfields
def editModFields(protocol_id, user_input):
    lines = getLines(protocol_id)
    input_no = 0
    for i in range(len(lines)):
        if "# modify" in lines[i]:
            while not "# end modify" in lines[i+1]:
                if "=" in lines[i+1]:
                    field = lines[i+1].split("=")[0]
                    new_value = user_input[input_no][1]['value']
                    lines[i+1] = field + "= " + new_value + "\n"
                    input_no = input_no + 1
                i = i + 1
    protocol_file = open("protocol_files/{}.py".format(protocol_id), "w")
    protocol_file.writelines(lines)
    protocol_file.close()