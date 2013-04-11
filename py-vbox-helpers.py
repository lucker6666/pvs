import subprocess
import json

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


##########################################################
# Example usage
##########################################################

# display all the VMs and their uuids
print "\nPrinting all the found VMs"
for k,v in getVMList().items():
	print "VM name:'"+ k+ "' and uuid:", v["id"]

# print description parsed as String
print "\nPrinting description as String"
print getVMDescription("win7_ie8")

# print description parsed as JSON
print "\nPrinting description parsed as JSON"
print getVMDescriptionAsJSON("win7_ie8")

# access value from JSON structure
box = getVMDescriptionAsJSON("win7_ie8")['box']
print "\nGuest OS is: %s %d with locale set to: %s" % (box["os"], box["version"], box["locale"])





