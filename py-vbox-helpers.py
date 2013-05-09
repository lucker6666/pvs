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
    return VMsmatch

#startVMsWithBrowsers({"IE":"9","FF":"20"})

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
        return json.dumps(vmsList)

@app.route('/pvb/listRunningVMs')
def hello1():
    runVmsList = getRunningVMsAsList()
    if len(runVmsList) == 0 :
        return redirect(url_for('exampleJsonError', code="pvb_E_002", message = "No Running VMs found", status=400))
    else:
        print json.dumps(runVmsList)
        return json.dumps(runVmsList)


@app.route('/pvb/startVMs/<listOfBrowsers>')
def start(listOfBrowsers):
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
    try:
        # open the url and read the content in HTML form
        url = urllib2.urlopen("http://10.0.2.15:4444/grid/console")
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
            print "GRID CONSOLE : " , jsonobject
            # prettify json to print on client webpage
            return jsonify(zipping)


    except URLError, e:
        print "Error :", e.reason
        # print "Testing if attribute, "code" present for the error object,e : ", hasattr(e, 'code')
        return redirect(url_for('exampleJsonError', code="pvb_E_004", message = str(e.reason)+" : Selenium hub is not started", status=500))
        # return str(e.reason)

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