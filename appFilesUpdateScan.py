# This is an stand-alone script

lineSep  = java.lang.System.getProperty('line.separator')

def toogleFileUpdateScan(enable):
    #print "DEBUG: START: toogleFileUpdateScan"

    appList = AdminApp.list()
    for appName in appList.split(lineSep):
        if(enable.upper() == "FALSE"):
            print "INFO: toogleFileUpdateScan: Current info for " + appName
            print AdminApp.view(appName, '-reloadEnabled')
            print AdminApp.view(appName, '-reloadInterval')
            AdminApp.edit(appName, "-reloadEnabled true -reloadInterval 0")
            print "INFO: toogleFileUpdateScan: Disabled update scanning for " + appName
            print
            print
        else:
            raise Exception, "Enable update scanning not implemented"

    #print "DEBUG: END: toogleFileUpdateScan"
    return