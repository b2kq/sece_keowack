JYTHON_HOME = "/promotion/jython"
#print "DEBUG: START: gl"
execfile(JYTHON_HOME+"/global.py")
#print "DEBUG: START: gl1"
execfile(JYTHON_HOME+"/jvm.py")
#print "DEBUG: START: gl2"
execfile(JYTHON_HOME+"/security.py")
#print "DEBUG: START: gl3"
execfile(JYTHON_HOME+"/transport.py")
#print "DEBUG: START: gl4"
execfile(JYTHON_HOME+"/datasource.py")
#print "DEBUG: START: gl5"
execfile(JYTHON_HOME+"/resource.py")
#print "DEBUG: START: gl6"
execfile(JYTHON_HOME+"/idm.py")
#print "DEBUG: START: gl7"
execfile(JYTHON_HOME+"/application.py")
#print "DEBUG: START: gl8"
execfile(JYTHON_HOME+"/buildEnv.py")
#print "DEBUG: START: gl9"
execfile(JYTHON_HOME+"/scope.py")
#print "DEBUG: START: gl10"
execfile(JYTHON_HOME+"/ra.py")
#print "DEBUG: START: gl11"
execfile(JYTHON_HOME+"/xml.py")
#print "DEBUG: START: gl12"
execfile(JYTHON_HOME+"/common.py")
#print "DEBUG: START: gl13"
execfile(JYTHON_HOME+"/sib.py")
#print "DEBUG: START: gl14"
execfile(JYTHON_HOME+"/webserver.py")
#print "DEBUG: START: gl15"
execfile(JYTHON_HOME+"/saveOperations.py")
#print "DEBUG: START: gl16"
execfile(JYTHON_HOME+"/jms.py")
#print "DEBUG: START: gl17"
execfile(JYTHON_HOME+"/wily.py")
#print "DEBUG: START: gl18"
execfile(JYTHON_HOME+"/jvmOperations.py")
#print "DEBUG: START: gl19"

def managerCheck():
    #print "DEBUG: START: managerCheck"
    global DMGR, STANDALONE, MGRNODENAME
    MGRNODENAME = AdminControl.getNode()
    command = "AdminControl.completeObjectName('type=Server,node=" + MGRNODENAME + ",cell=" + cellName + ",*')"
    serverList = eval(command)
    server = serverList.split(lineSep)[0]
    processType = AdminControl.getAttribute(server, 'processType')
    if(processType == "DeploymentManager"):
        print "INFO: managerCheck: Connected to a Deployment Manager"
        DMGR = "TRUE"
        STANDALONE = "FALSE"
    elif(processType == "ManagedProcess" or processType == "NodeAgent"):
        print "INFO: managerCheck: Connected to a NodeAgent"
        print "Exception: managerCheck: This script was not run by connecting to dmgr process"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    elif(processType == "UnManagedProcess"):
        print "INFO: managerCheck: Connected to an UnManaged Process"
        DMGR = "FALSE"
        STANDALONE = "TRUE"
    #print "DEBUG: END: managerCheck"
    return

# Main
try:    

    #print "DEBUG: START: main"
    global SAVE

    SAVE = 0
    if(len(sys.argv) == 3):
	env = sys.argv[0].upper()
        propFile = sys.argv[1]
        task = sys.argv[2]
   # elif(len(sys.argv) == 4):
   #     propFile = sys.argv[1]
   #     task = sys.argv[2]
   #     if(sys.argv[3].upper() == "SAVE"):
   #         SAVE = 1
   #     elif(sys.argv[3].upper() == "NOSAVE"):
   #         SAVE = 0
   #     else:
   #         print "ERROR: main: Bad save parameter"
   #         raise Exception, "Bad input parameters"
    #added by Nik to support the passing of the environment paramater for us in buildenv to set the logging level.
    elif(len(sys.argv) == 4):
        propFile = sys.argv[1]
        task = sys.argv[2]
	env = sys.argv[0].upper()
        if(sys.argv[3].upper() == "SAVE"):
            SAVE = 1
        elif(sys.argv[3].upper() == "NOSAVE"):
            SAVE = 0
        else:
            print "Exception: main: Bad save parameter"
            raise Exception, "Bad input parameters"
    #End of Nik's changes
    else:
        print "Exception: main: Usage: WSADMIN -lang jython -f main.py <ENV> <props.xml> <build/deploy/both/start/stop> [save/nosave]"
        raise Exception, "Bad input parameters"

    managerCheck()

    # Parse the XML properties files, using XERCES DOM parsing
    domDoc = parseXML(propFile)
    rootElement = domDoc.getDocumentElement()

    # Invoke the required task
    if(task.upper() == "BUILD"):
        buildTask(rootElement)
    elif(task.upper() == "DEPLOY"):
        appInstall(rootElement)
    elif(task.upper() == "BOTH"):
        buildTask(rootElement)
        appInstall(rootElement)
    elif(re.search(task.upper(), "START/STOP/JAVACORE/HEAPDUMP/STOPIMMEDIATE/RIPPLE/STATUS/RESTART") != None):
        appSvrNode = rootElement.getElementsByTagName("ApplicationServer").item(0)
        if(appSvrNode != None):
            clusterName = getTagValue(appSvrNode, 'ClusterName')
            clusterOp(clusterName, task)
        else:
            print "Exception: main: ClusterName node not found in XML property sheet"
            raise Exception, "Script raised exception, you are doing something wrong!!!"
    else:
        print "Exception: main: Bad input parameters"
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    #print "DEBUG: END: main"
except:
    print "Exception: ", sys.exc_type, sys.exc_value