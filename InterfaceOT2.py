import os

# retrieves IP address from ip.txt
def getIP():
    ip_file = open("ip.txt", "r+")
    ip = ip_file.read()
    ip_file.close()
    return ip

# Sends protocol to OT2 and executes file
def sendProtocol(protocol):
    ip = getIP()
    name = protocol['id']
    # change following lines from print to os.popen
    print("scp -i ot2_ssh_key /protocol_files/{}.py root@{}:/data/{}.py".format(name, ip, name))
    print('ssh -i ot2_ssh_key root@{} "opentrons_execute /data/{}.py"'.format(ip, name))
    return None

# Saves ip to file and initiates connection
def setIP(results):
    # if not os.path.exists('ip.txt'):
    #     ip_file = open("ip.txt", "w+")
    ip_file = open("ip.txt", "w+")
    ip = results[0][1]['value']
    ip_file.write(ip)
    ip_file.close()

# generates ssh key pair, installs key on OT2 at ip set with setIP, MUST BE CONNECTED TO OT2
def firstTimeSetup():
    ip = getIP()
    # change following lines from print to os.popen
    print('ssh-keygen -f ot2_ssh_key')
    # must be connected to OT-2 for following steps
    print("@{key = Get-Content ot2_ssh_key.pub | Out-String} | ConvertTo-Json | Invoke-WebRequest -Method Post -ContentType 'application/json' -Uri {}:31950/server/ssh_keys".format(ip))

