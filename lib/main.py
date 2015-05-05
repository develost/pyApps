import logging
import urllib
import httplib
import getpass
import zlib
import base64
import sys
import os
import re

# server connection for updates
#server='localhost'
#port=18080
#url='/apps'
#useSSL=False

server='www.develost.com'
port=443
url='/apps'
useSSL=True
extCfg='cfg'
extLog='log'

# global variables
projectName=''
username=''
password=''
version=''

def __loadConfig__():
    global projectName
    global username
    global password
    global version

    replaceConfiguration = False
    lines = []
    try:
        with open (os.path.dirname(os.path.abspath(__file__)) +'/../cfg/'+projectName+'.'+extCfg, 'r') as cfgFile:
            lines = [line.rstrip() for line in cfgFile]
    except IOError as ioe:
        print "Config file not found - creating one from scratch"
        lines.append("# --------------------------------------------------")
        lines.append("# " + projectName + " configurations              ")
        lines.append("# --------------------------------------------------")
            
    usernameList = [line for line in lines if line.startswith("username=")]
    if not usernameList:
        username = raw_input('Username: ')
        lines.append("username="+username)
        replaceConfiguration = True
    else:
        username = usernameList[0].replace("username=","",1).strip()
    
    passwordList = [line for line in lines if line.startswith("password=")]
    if not passwordList:
        password = getpass.getpass()
        lines.append("password="+password)
        replaceConfiguration = True
    else:
        password = passwordList[0].replace("password=","",1).strip()
    
    versionList = [line for line in lines if line.startswith("version=")]
    if not versionList:
        version = 'last'
        lines.append("version="+version)
        replaceConfiguration = True
    else:
        version = versionList[0].replace("version=","",1).strip()

    if replaceConfiguration:    
        with open(os.path.dirname(os.path.abspath(__file__)) +'/../cfg/'+projectName+'.'+extCfg, 'w') as cfgFile:
            cfgFile.write('\n'.join(lines) + '\n')            
    return
    
def __retrieveCode__():
    global projectName
    global username
    global password
    global version
    print projectName
    code = None
    params = urllib.urlencode({'projectName':projectName,'version':version,'username':username,'password':password})
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    connection = None
    if useSSL:
        connection = httplib.HTTPSConnection(server,port)
    else:
        connection = httplib.HTTPConnection(server,port)
        
    connection.request("POST",url+'/'+projectName+'/'+version+'/'+'index.php',params,headers)
    response = connection.getresponse()
    
    print response.reason
    if response.status == 200:
        code = response.read()
    else:
        print "Error:" , response.reason , response.status
    return code
        
def __main__():
    print "projectName",projectName
    print "version",version
    print "username",username
    print "password",password
    
    code = __retrieveCode__()
    #print code
    if code:
        #exec code
        exec (code, globals())
        entryPoint()
    return

def main():
    global projectName
    fileName, fileExtension = os.path.splitext(sys.argv[0])
    projectName = os.path.basename(fileName)
    if re.match('[A-Za-z0-9 ]+',projectName):
        __loadConfig__()
        logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__)) +'/../log/'+projectName+'.'+extLog,format='%(asctime)s %(message)s',level=logging.DEBUG)
        __main__()
    else:
        print "Error: filename not valid"
        raw_input("Press enter to continue")
