###STAND-ALONE SCRIPT###

# This script modifies the 'java.naming.security.principal' and
# 'java.naming.security.credentials' resource properties of the
# SonicMQ JMS Providers to the common value 'USGClient'

# Example of how to invoke:
# /IBM/WebSphere70/AppServer64/bin/wsadmin.bat -p J:/promotion/properties/devwas/wsadmin.properties -f ../jython/modifyResPropLoginInfo_Etien.py

def modifyProperty(resProp, propValue):
    print "Entering modifyProperty..."
    # Modify if exists, and return
    if(resProp != ""):
       curPropName = AdminConfig.showAttribute(resProp, 'name')
       curPropValue = AdminConfig.showAttribute(resProp, 'value')
       if(curPropValue != propValue):
           AdminConfig.modify(resProp, [['value', propValue]])
           print "Modified property ",curPropName,", from ",curPropValue," to ",propValue
       curPropValue = AdminConfig.showAttribute(resProp, 'value')
       print "Name: " + curPropName + "; Value: " + curPropValue
       print "Exiting modifyProperty."
       return
    # Since it does not exist, throw an error message, and raise an exception
    raise Exception, "Script raised exception: the property being passed in  does not exist!"
    print "Exiting modifyProperty."
    return


# Main
try:
    print "Starting JMS Provider Custom Properties Look-up..."

    # Used to keep track of property sheets that will need manual modification
    propSheetList = []

    # Generate list of JMS Providers
    jmsProvList = AdminConfig.list('JMSProvider')
    #print jmsProvList

    # Traverse list of providers looking for the 'SonicMQ' providers
    for jmsProv in jmsProvList.split("\r\n"):
        curJSMProvName = AdminConfig.showAttribute(jmsProv, 'name')

	# Once a 'SonicMQ' provider is found...
        if (curJSMProvName == 'SonicMQ'):

		print curJSMProvName + " properties:"

		# Display cluster information
		temp = jmsProv.split("/")[3]
		cluster = temp.split("|")[0]
		print "Cluster: " + cluster

		# Capture properties
		propSet = AdminConfig.showAttribute(jmsProv, 'propertySet')

		resProps = AdminConfig.showAttribute(propSet, 'resourceProperties')
		#print resProps # DEBUG
		resPropsList = resProps[1:len(resProps)-1].split(" ")

		# Print properties in the format 'name, nalue' and modify the ones needing change
		for resProp in resPropsList:

                        name = AdminConfig.showAttribute(resProp, 'name')
                        value = AdminConfig.showAttribute(resProp, 'value')

			print name + ", " + value

                        if (name == 'java.naming.security.principal' or name == 'java.naming.security.credentials'):
                            if (value != 'USGClient'):
                                print "The value for " + name + " needs to be changed to 'USGClient'"
                                modifyProperty(resProp, 'USGClient')

                                # Add to list of property sheets to be manually modified, if not added yet
				if (propSheetList.count(cluster) == 0):
					propSheetList.extend([cluster])
		#print propSheetList # DEBUG
		print "" # Used for padding the output on command line window

    # Print out to the screen the property sheets that need to be manually modified given the changes from above
    print "Please manually modify the following (if any) property sheets in order to complete the process:"
    for propSheet in propSheetList:
    	print propSheet

    # Save changes
    AdminConfig.save()

# Generate exception
except:
    print "Exception: ", sys.exc_type, sys.exc_value