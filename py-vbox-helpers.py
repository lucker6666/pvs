#! /usr/bin/env python

import subprocess
import json
import urllib2
from urllib2 import URLError
import logging
from xml.dom import minidom
from flask import Flask, jsonify
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from flask import make_response, redirect, url_for
import socket

#################################
# HTML Parser
#################################
# This class serves as a basis for parsing files in HTML
class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.vmsCount = 0
        # store ip address of VMs that are registered to hub
        self.vmsAddress = []
        # store the browsers data which are registered to grid
        self.browData = []

    # Handles the start tags of the HTML snippet
    def handle_starttag(self, tag, attrs):
        # print "Start tag:", tag
        # for attr in attrs:
        #     print "     attr:", attr

        # if the tag is "legend", then set the count flag based on which the handle_data method gets the 
        # tag's data
        if tag == 'legend':
            self.vmsCount = 1

        if tag == 'img':
            for name,value in attrs:
                if name == 'title':
                    self.browData.append(str(value))


    def handle_data(self, data):
        if self.vmsCount:
            # self.vmsAddress.append(data)

            #append data, which starts with "listening", to the list 
            if data.startswith('listening'):
                # remove the prefix "listening on http://"
                stripData = data[20:]
                # seperate ip address and port ex, 0.0.0.0:1234 into (0.0.0.0 , 1234 )
                tupleData = tuple(stripData.split(':'))
                self.vmsAddress.append(str(tupleData))

############################################
#Helper methods
############################################

# return a map of all registered VBox VMs
def getVMList():
    vms = {}
    out = subprocess.Popen("VBoxManage list vms", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in out.stdout.readlines():
        (name, id) = line.split('" {')
        vms.setdefault(name.replace("\"",""), {}).setdefault('id', id.replace("}\n",""))
    retval = out.wait()
    return vms

# get VM description as String
def getVMDescription(vmName):
    p = subprocess.Popen("VBoxManage showvminfo " + vmName, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, errors = p.communicate() # store output and error in separate variables
    retval = p.wait()
    if p.returncode or errors:
        print "Something went wrong when gettin VM info! Error msg:'", errors, "' Error code:",  p.returncode
        return
    else:
        start=output.index('Description:') + 13 # +13 to remove the word Descritpion: with following new line char
        end=output.index("Guest:")
        return output[start:end]

# get VM descritpion as JSON
def getVMDescriptionAsJSON(vmName):
    return json.loads(getVMDescription(vmName))

def getRunningVMList():
    runningVms = {}
    out = subprocess.Popen("VBoxManage list runningvms", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in out.stdout.readlines():
        (name, id) = line.split('" {')
        runningVms.setdefault(name.replace("\"",""), {}).setdefault('id', id.replace("}\n",""))
    retval = out.wait()
    return runningVms


##########################################################
# Example usage
##########################################################

# # display all the VMs and their uuids
# print "\nPrinting all the found VMs"
# for k,v in getVMList().items():
#     print "VM name:'"+ k+ "' and uuid:", v["id"]

# # print description parsed as String
# print "\nPrinting description as String"
# print getVMDescription("linux")

# # print description parsed as JSON
# print "\nPrinting description parsed as JSON"
# print getVMDescriptionAsJSON("linux")

# # access value from JSON structure
# box = getVMDescriptionAsJSON("linux")['box']
# print "\nGuest OS is: %s %s with locale set to: %s" % (box["OS"], box["OS_lang"], box["Browsers"]["IE"]["version"])

# get VMs names as a list
def getVMsAsList():
    vms = []
    for k,v in getVMList().items():
        vms.append(k)
    return vms

# get running VMs names as a list
def getRunningVMsAsList():
    runningVms = []
    for k,v in getRunningVMList().items():
        runningVms.append(k)
    return runningVms

# find the VMs with required browsers version
def findMatchedVM(browsers,retFlag):
    vmsPresent = getVMsAsList()
    matchedVM = []
    print browsers
    # defining an empty dictionary, tempDict
    tempDict = {}
    matchedBrowsers = []
    for vm in vmsPresent:
        box = getVMDescriptionAsJSON(vm)['box']

        for brow in browsers:
            for b in brow:
                for i in  box["Browsers"]:
                    if b == i:
                        if box["Browsers"][i]["version"] == brow[b]:
                            matchedVM.append(vm)
                            tempDict[str(b)] = str(brow[b])
                            # # x = (str(brow) , str(browsers[brow]))
                            matchedBrowsers.append(brow)
                            print matchedBrowsers


    if retFlag==0:
        print "Matching VMs : ", matchedVM
        return matchedVM
    elif retFlag==1:
        print "Matching browsers : ", matchedBrowsers
        return matchedBrowsers

def startVMsWithBrowsers(browsers):
    # pass the flag,0 to get matching VMs
    VMs = findMatchedVM(browsers,0)
    #"set()" Removes duplicates from list 
    VMsmatch = list(set(VMs))

    vmsRunning = getRunningVMsAsList()
    # Get the difference between VMs to start and already running VMs
    # Start the required VMs which are not already running
    differenceVM = list(set(VMsmatch).difference(set(vmsRunning)))
    print "Starting VM(s) : " , differenceVM
    for vm in differenceVM:
       out = subprocess.Popen("VBoxManage startvm "+vm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print "Running VM(s)" , VMsmatch
    return VMsmatch


def verifyBrowsersAvailable(browsers):
    # pass the flag,1 to get the matching browsers
    browsersMatched = findMatchedVM(browsers,1)
    return browsersMatched
    

def startHub():
    hubVM = "Selenium-hub-LinuxMint"
    out = subprocess.Popen("VBoxManage startvm "+hubVM, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return "Starting selenium-grid Hub"


def verifyGridBrowsers(browsers):
    # flag=1 to get browsers from htmlParserHelper
    registeredRequiredBrowsers = []
    # get the registerd browsers list from grid console
    brow = htmlParserHelper(1)
    for i in range (len(brow)):
        # remove "type=WebDriver" from each list item
        data = brow[i].replace("type=WebDriver","")
        print "DATA : ", data
        # verify the registered browsers against the required browsers list
        for browse in browsers:
            print "BROWSE : ", browse
            print "BROWSER : ", browsers
            for key in browse:
                print "KEY : ", key
                print "VALUE : ", browse[key]
                # find() method returns -1 if the string not found and the index of string if found
                if data.find("browserName="+key+", version="+browse[key]) != -1:
                    registeredRequiredBrowsers.append(browse)
                    print "Registered : ", registeredRequiredBrowsers
                    break
    return registeredRequiredBrowsers

def htmlParserHelper(flag):
    try:
        # open the url and read the content in HTML form
        url = urllib2.urlopen("http://localhost:4444/grid/console")
        info = url.read()

        print "INFO : !!! ", info

        parser = MyHTMLParser()
        # feed the HTML which needs to be parsed
        parser.feed(info)
        print "VMs address and ports !! : ", parser.vmsAddress
        print "BROWWWSERS !! : ", parser.browData
        zipping = dict(zip(parser.vmsAddress, parser.browData))
        # prettify json with indent and seperators to print in command line
        jsonobject = json.dumps(zipping, sort_keys=True, indent=4, separators=(',', ': '))

        # check if there are any nodes registered to the hub
        if len(zipping) == 0:
            print "INFO: NO nodes registered"
            return redirect(url_for('exampleJsonError', code="pvb_E_005", message = "Started hub : No nodes registered to the hub", status=400))
        else:
            if flag==0:
                print "GRID CONSOLE : " , jsonobject
                # prettify json to print on client webpage
                return jsonify(zipping)
            elif flag==1:
                print "BROWSERS: ", parser.browData
                return parser.browData


    except URLError, e:
        print "Error :", e.reason
        # print "Testing if attribute, "code" present for the error object,e : ", hasattr(e, 'code')
        return redirect(url_for('exampleJsonError', code="pvb_E_004", message = str(e.reason)+" : Selenium hub is not started", status=500))
        # return str(e.reason)

def shutDownVMs():
    getRunningVMs = getRunningVMsAsList()
    print "test : ", getRunningVMs
    for vm in getRunningVMs:
        out = subprocess.Popen("VBoxManage controlvm "+vm+" poweroff", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return "Shutting Down VMs : " + json.dumps(getRunningVMs)


################################### 
# Flask methods 
###################################

# Using 'FLASK', a python framework, to start the http server and expose a few methods in this script which
# can be accessed by making http calls


app = Flask(__name__)

@app.route('/pvb/')
def index():
    return 'Welcome to the Python VBox Selenium manager.'


@app.route('/pvb/listVMs')
def hello():
    vmsList = getVMsAsList()
    if len(vmsList) == 0 :
        return redirect(url_for('exampleJsonError', code="pvb_E_001", message = "No VMs found. Install a few Vms to start testing !!", status=400))
    else:
        return "List of all the VMs : " + json.dumps(vmsList)


@app.route('/pvb/listRunningVMs')
def hello1():
    runVmsList = getRunningVMsAsList()
    if len(runVmsList) == 0 :
        return redirect(url_for('exampleJsonError', code="pvb_E_002", message = "No Running VMs found", status=400))
    else:
        print json.dumps(runVmsList)
        return "List of Running VMs : " + json.dumps(runVmsList)


@app.route('/pvb/verifyBrowsers/<listOfBrowsers>')
def findAvailableBrowsers(listOfBrowsers):
    brow = verifyBrowsersAvailable(json.loads(listOfBrowsers))
    if len(brow) == 0 :
        return redirect(url_for('exampleJsonError', code="pvb_E_006", message = "No matching browsers found in the VMs", status=400))
    else:
        print "Matched Browsers : ", brow
        return "List of required browsers available : " + str(brow)


@app.route('/pvb/startVMs/<listOfBrowsers>')
def start(listOfBrowsers):
    startHub()

    # the parameter "listofbrow" is returned as string from the URL. Hence, use json.loads(listofbrow) to 
    # convert to json
    vmsToStart = startVMsWithBrowsers(json.loads(listOfBrowsers))
    if len(vmsToStart) == 0:
        return redirect(url_for('exampleJsonError', code="pvb_E_003", message = "The required browsers cannot be found in any of the VMs. Check the available browsers", status=400))
    else:
        return "Starting VM(s) : " + json.dumps(vmsToStart)

# Parse the HTML of grid console page to extract VMs address, port and browsers data
@app.route('/pvb/gridConsole')
def checkGrid():
    return htmlParserHelper(0)


@app.route('/pvb/gridBrowsersAvailable/<listOfBrowsers>')
def checkGridBrowsers(listOfBrowsers):
    gridBrow = verifyGridBrowsers(json.loads(listOfBrowsers))
    if len(gridBrow) == 0 :
        return redirect(url_for('exampleJsonError', code="pvb_E_007", message = "No required browsers registered in the grid", status=400))
    else:
        return "List of required browsers, registered in grid : "+ json.dumps(gridBrow)


@app.route('/pvb/shutdownVMs')
def shutVMs():
    return shutDownVMs()

################################### 
# Error handling 
###################################

@app.route('/pvb/err/<code>/<message>/<status>')
def exampleJsonError(code,message,status):
    error = {'error': {'errorCode':code, 'msg':message, 'statusCode':status}}
    errorMessage = jsonify(error)
    errorMessage.headers['Content'] = 'application/json'
    errorMessage.status_code=int(status)

    print json.dumps(error,sort_keys=True, indent=4, separators=(',', ': '))
    return errorMessage

app.debug = True
app.run(host='0.0.0.0')