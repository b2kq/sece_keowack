JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")

def listServers(envName):
    try:
        f = open("J:/temp/"+envName+"_Servers.txt","w")
        nodes = (AdminConfig.list('Node')).split(lineSep)
        f.write('%s^%s^%s^%s^%s' % ('Env', 'HostName', 'Node Name', 'Server Type', 'Server Name') + lineSep)
        for node in nodes:
            nName = node[0:node.find("(")]
            nodeId = AdminConfig.getid("/Node:" + nName)
            nodeHostName = AdminConfig.showAttribute(nodeId, 'hostName')
            serverEntries = (AdminConfig.list('ServerEntry', node)).split(lineSep)
            for serverEntry in serverEntries:
                sName = AdminConfig.showAttribute(serverEntry,"serverName")
                sType = AdminConfig.showAttribute(serverEntry,"serverType")
                if sType != None and sType != 'DEPLOYMENT_MANAGER' and sType != 'NODE_AGENT':                
                    #print '%s;%s;%s;%s' % (envName,nName,sType,sName)
                    f.write('%s^%s^%s^%s^%s' % (envName,nodeHostName, nName,sType,sName) + lineSep)
                #else:
                    #print "Exception: No app/web servers exist in " + envName
        #endFor
        f.close()
    except:
        typ, val, tb = sys.exc_info()
        if(typ==SystemExit):  raise SystemExit,`val`
        print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
        return -1
    #endTry
#endDef

# Main
try:
    if(len(sys.argv) == 1):
        envName = sys.argv[0]
        print "INFO: Getting info for all servers in " + envName
        print ""
        listServers(envName)
    else:
        print "Exception: main: Missing/Bad input parameters"
        raise Exception, "Script raised exception"
    #endif
except:
    print "Exception: Invalid Request"