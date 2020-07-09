import re, os

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
                    if "#" in lines[i+1]:
                        description = lines[i+1].split("#")[1]
                        lines[i+1] = field + "= " + new_value + " # " + description.lstrip().capitalize()
                    else:
                        lines[i+1] = field + "= " + new_value + "\n"
                    input_no = input_no + 1
                i = i + 1
    protocol_file = open("protocol_files/{}.py".format(protocol_id), "w")
    protocol_file.writelines(lines)
    protocol_file.close()

# findMatch: takes source info, destination info, and key to match (value, color) and returns list of matches
def findMatch(source, destination, matchKey):
    matches = []
    for row in destination:
        temp_row = []
        for well in row:
            if well[matchKey] == source[matchKey] and source[matchKey] != None:
                temp_row.append(True)
            else:
                temp_row.append(False) 
        matches.append(temp_row)
    return matches

# takes source title (as defined in protocol file), source location, and 2d array of matches, returns string to write to script
def generateCommand(source_title, source_location,  matches):
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    if source_title == 'source_1':
        volume = 'source_1_volume'
    elif source_title == 'source_2':
        volume = 'source_2_volume'

    command = ''

    destinations = ''

    row_idx = 0
    match = False
    for row in matches:
        col_idx = 0
        for well in row:
            if well:
                match = True
                for i in range(3):
                    destinations = destinations + "d['" + letters[row_idx] + str(col_idx * 3 + i + 1) + "'], "
            col_idx = col_idx + 1

        row_idx = row_idx + 1

    destinations = destinations[:-2]
    if match:
        command =  "\n" + "    " + 'single_pipette.distribute(' + volume + ', ' + source_title + ".wells_by_name()['" + source_location + "'], [" + destinations + '])'
    return command

# takes protocol id and command string, writes string onto file that matches the id
def writeToScript(protocol_id, command):
    with open("protocol_files/{}.py".format(protocol_id), 'a') as file:
        file.write(command)
    return None

# Sets up dictionary of destination wells in protocol file
def writeSetup(protocol_id):
    command = "    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']" + "\n" + "    d = {}" + "\n" + "    for letter in letters:" + "\n" + "        for i in range(1, 13):" + "\n" + "            d[letter + str(i)] = destination.wells_by_name()[letter + str(i)]"
    with open("protocol_files/{}.py".format(protocol_id), 'a') as file:
        file.write(command)
    return None

# Clears all lines in protocol file after "# commands"
def clearCommands(protocol_id):
    lines = getLines(protocol_id)
    for i in range(len(lines)):
        if "# commands" in lines[i]:
            protocol_file = open("protocol_files/{}.py".format(protocol_id), "w")
            lines = lines[:i+1]
            protocol_file.writelines(lines)
            protocol_file.close()
            break
            



# Takes dictionary (different ranges) of dictionaries (range, values, etc), and edits protocol file with appropriate code
def editScriptRTPCR(protocol_id, well_map_info):
    Source1 = well_map_info['Source1']
    Source2 = well_map_info['Source2']
    Destination = well_map_info['Destination']
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    # for each cell in source 1:
        # find destination wells with same color (findMatch)
        # distribute to all matches with single-channel pipette (appendScript)

    clearCommands(protocol_id)
    writeSetup(protocol_id)

    row_idx = 0
    for row in Source1:
        col_idx = 0
        for well in row:
            matches = findMatch(well, Destination, 'color')
            command = generateCommand('source_1', letters[row_idx] + str(col_idx+1), matches)
            writeToScript(protocol_id, command)
            col_idx = col_idx + 1
        row_idx = row_idx + 1

    row_idx = 0
    for row in Source2:
        col_idx = 0
        for well in row:
            matches = findMatch(well, Destination, 'value')
            command = generateCommand('source_2', letters[row_idx] + str(col_idx+1), matches)
            writeToScript(protocol_id, command)
            col_idx = col_idx + 1
        row_idx = row_idx + 1

# Takes protocol id, simulates protocol file and returns log
def simulateProtocol(protocol_id):
    return os.popen("opentrons_simulate.exe protocol_files\{}.py".format(protocol_id)).read().splitlines()