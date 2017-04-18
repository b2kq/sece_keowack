# Get the scope ID, check validity, and return it
def getScopeID(scopeS, scopeN):
    #print "DEBUG: START: getScopeID"

    scope = getScopeString(scopeS, scopeN)
    scopeID = AdminConfig.getid(scope)
    if(scopeID == ""):
        print "Exception: getScopeID: Bad scope parms, " + scopeS + " " + scopeN
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    #print "DEBUG: END: getScopeID"
    return scopeID

# Build the scope string, print and return it
def getScopeString(scopeS, scopeN):
    #print "DEBUG: START: getScopeString"

    if((scopeN == None) | (scopeN == "")):
        if((scopeS == None) | (scopeS == "")):
            scope = '/Cell:' + cellName + '/'
        else:
            scope = '/Cell:' + cellName + '/ServerCluster:' + scopeS + '/'
    else:
        if((scopeS == None) | (scopeS == "")):
            scope = '/Cell:' + cellName + '/Node:' + scopeN + '/'
        else:
            scope = '/Cell:' + cellName + '/Node:' + scopeN + '/Server:' + scopeS + '/'

    #print "DEBUG: END: getScopeString"
    return scope