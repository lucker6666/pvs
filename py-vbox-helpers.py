#! /usr/bin/env python

import subprocess
import json
import urllib
import logging
from xml.dom import minidom
from flask import Flask, jsonify
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint


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
def findMatchedVM(browsers):
    vmsPresent = getVMsAsList()
    matchedVM = []
    for vm in vmsPresent:
        box = getVMDescriptionAsJSON(vm)['box']

        for brow in browsers:
            for i in  box["Browsers"]:
                if brow == i:
                    if box["Browsers"][i]["version"] == browsers[brow]:
                        matchedVM.append(vm)
    return matchedVM



def startVMsWithBrowsers(browsers):
    VMs = findMatchedVM(browsers)
    #"set()" Removes duplicates from list 
    VMsmatch = list(set(VMs))

    vmsRunning = getRunningVMsAsList()
    differenceVM = list(set(VMsmatch).difference(set(vmsRunning)))
    print "Starting VM(s) : " , differenceVM
    for vm in differenceVM:
       out = subprocess.Popen("VBoxManage startvm "+vm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print "Running VM(s)" , VMsmatch

#startVMsWithBrowsers({"IE":"9","FF":"20"})


# Using 'FLASK', a python framework, to start the http server and expose a few methods in this script which
# can be accessed by making http calls

app = Flask(__name__)

@app.route('/pvb/')
def index():
    return 'Welcome to the Python VBox Selenium manager.'


@app.route('/pvb/listVMs')
def hello():
    return json.dumps(getVMsAsList())

@app.route('/pvb/listRunningVMs')
def hello1():
    return json.dumps(getRunningVMsAsList())


@app.route('/pvb/startVMs/<listOfBrowsers>')
def start(listOfBrowsers):
    # the parameter "listofbrow" is returned as string from the URL. Hence, use json.loads(listofbrow) to convert to jason
    return "Starting VM" , startVMsWithBrowsers(json.loads(listOfBrowsers))

"""an example json error msg"""
@app.route('/pvb/err')
def exampleJsonError():
    return json.dumps({'error': {'code':123, 'msg':'this is an example error'}},
            sort_keys=True,
            indent=4, 
            separators=(',', ': '))


# Parse the HTML of grid console page to extract VMs address, port and browsers data
@app.route('/pvb/gridConsole')
def checkGrid():
    # open the url and read the content in HTML form
    url = urllib.urlopen("http://localhost:4444/grid/console")
    info = url.read()

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

    parser = MyHTMLParser()
    # feed the HTML which needs to be parsed
    parser.feed(info)
    print "VMs address and ports !! : ", parser.vmsAddress
    print "BROWWWSERS !! : ", parser.browData
    zipping = dict(zip(parser.vmsAddress, parser.browData))
    # prettify json with indent and seperators to print in command line
    jsonobject = json.dumps(zipping, sort_keys=True, indent=4, separators=(',', ': '))
    print "JSON : " , jsonobject
    # prettify json to print on client webpage
    return jsonify(zipping)

app.debug = True
app.run(host='0.0.0.0')
