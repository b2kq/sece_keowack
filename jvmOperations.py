def getJVMMBean(jvmName, nodeName, type):
    #print "DEBUG: START: getJVMMBean"

    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    if(jvmId == ""):
        print "Exception: getJVMMBean: Bad jvmName, or nodeName passed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    iter = [1,2,3,4]
    for x in iter:
        jvmMBean = AdminControl.completeObjectName('WebSphere:type=' + type + ',node=' + nodeName + ',process=' + jvmName + ',*')
        if((jvmMBean == "") & (x == 2)):
            print "WARNING: getJVMMBean: Could not get JVM MBean"
            return
        if(jvmMBean != ""):
            break
        sleep(60)

    #print "DEBUG: END: getJVMMBean"
    return jvmMBean

def threadDump(jvmName, nodeName):
    #print "DEBUG: START: threadDump"

    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    if(jvmId == ""):
        print "Exception: threadDump: Bad jvmName, or nodeName passed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    jvmMBean = AdminControl.completeObjectName('WebSphere:type=JVM,node=' + nodeName + ',process=' + jvmName + ',*')
    if(jvmMBean == ""):
        print "Exception: threadDump: " + jvmName + " on " + nodeName + " does not appear to be started, thread dump not possible"
    else:
        print "INFO: threadDump: Dumping threads for " + jvmName + " " + nodeName
        AdminControl.invoke(jvmMBean, "dumpThreads")

    #print "DEBUG: END: threadDump"
    return

def heapDump(jvmName, nodeName):
    #print "DEBUG: START: heapDump"

    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    if(jvmId == ""):
        print "Exception: heapDump: Bad jvmName, or nodeName passed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    jvmMBean = AdminControl.completeObjectName('WebSphere:type=JVM,node=' + nodeName + ',process=' + jvmName + ',*')
    if(jvmMBean == ""):
        print "Exception: heapDump: " + jvmName + " on " + nodeName + " does not appear to be started, heap dump not possible"
    else:
        print "INFO: heapDump: Generating HEAPDUMP for " + jvmName + " " + nodeName
        AdminControl.invoke(jvmMBean, 'generateHeapDump')

    #print "DEBUG: END: heapDump"
    return

def stopJVM(jvmName, nodeName, checkStatus):
    #print "DEBUG: START: stopJVM"

    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    if(jvmId == ""):
        print "Exception: stopJVM: Bad jvmName, or nodeName passed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    #jvmMBean = AdminControl.completeObjectName('WebSphere:type=Server,node=' + nodeName + ',process=' + jvmName + ',*')
    jvmMBean = getJVMMBean(jvmName, nodeName, "Server")

    if((jvmMBean == "") | (jvmMBean == None)):
        print "INFO: stopJVM: " + jvmName + " on " + nodeName + " is already stopped!!!"
    else:
        if(checkStatus == 0):
            print "INFO: stopJVM: " + jvmName + " on " + nodeName + " is currently started, issuing a stop"
            AdminControl.stopServer(jvmName, nodeName)
        elif(checkStatus == 1):
            print "INFO: stopJVM: " + jvmName + " on " + nodeName + " is currently started, issuing a stop with 300 sec max wait"
            try:
                AdminControl.invoke(jvmMBean, 'stop')
            except:
                AdminControl.stopServer(jvmName, nodeName, 'terminate')
            else:
                print "INFO: stopJVM: Waiting for stop completion..."
                sleepCounter = 0
                while(jvmMBean != ""):
                    if(sleepCounter < 300):
                        time.sleep(5)
                        sleepCounter = sleepCounter + 5
                        jvmMBean = AdminControl.queryNames("type=Server,node=" + nodeName + ",name=" + jvmName + ",*")
                    else:
                        print "WARNING: stopJVM: The JVM did not stop within 300 sec, issuing terminate"
                        AdminControl.stopServer(jvmName, nodeName, 'terminate')
                        return
                print "INFO: stopJVM: " + jvmName + " on " + nodeName + " is now stopped, took approx. " + str(sleepCounter) + " sec to stop"
        else:
            print "Exception: stopJVM: Bad checkStatus option passed, " + checkStatus

    #print "DEBUG: END: stopJVM"
    return

def startJVM(jvmName, nodeName, checkStatus):
    #print "DEBUG: START: startJVM"

    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    if(jvmId == ""):
        print "Exception: startJVM: Bad jvmName, or nodeName passed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    processDef = AdminConfig.list('JavaVirtualMachine', jvmId)
    ojvmParm = AdminConfig.showAttribute(processDef, 'genericJvmArguments')

    #Modifed faulty if-statement - empty generic JVM args should not prevent the JVM from starting up.
    #if((ojvmParm == None) | (ojvmParm != "")):
    if((ojvmParm != None) & (ojvmParm != "")):
        if((ojvmParm.find("DONTSTART") != -1) | (ojvmParm.find("DONOTSTART") != -1)):
            print "INFO: startJVM: Will not attempt to start " + jvmName + " on " + nodeName
            return
            
    jvmMBean = AdminControl.completeObjectName('WebSphere:type=Server,node=' + nodeName + ',process=' + jvmName + ',*')
    #jvmMBean = getJVMMBean(jvmName, nodeName, "Server")
    if(jvmMBean == ""):
        #nodeObj = AdminControl.completeObjectName('type=NodeSync,node=' + nodeName + ',*')
        #if(len(nodeObj) == 0):
        #    print "Exception: startJVM: mbean is not running for node " + nodeName
        #    print "Exception: startJVM: Cannot perform start operation on JVM " + jvmName
        #    return
        if(checkStatus == 0):
            print "INFO: startJVM: " + jvmName + " on " + nodeName + " is currently stopped, issuing a start"
            AdminControl.startServer(jvmName, nodeName)
        elif(checkStatus == 1):
            print "INFO: startJVM: " + jvmName + " on " + nodeName + " is currently stopped, issuing a start with 1200 sec max wait"
            AdminControl.startServer(jvmName, nodeName, 1)
            print "INFO: startJVM: Waiting for start completion..."
            sleepCounter = 0
	    if(jvmName == "ClaimCenter_1_1"):
		timeout = 2400
		print "INFO: startJVM: The timeout has been increased to 2400 seconds."
	    else:
	    	timeout = 1200
		print "INFO: startJVM: The timeout has been retained at 1200 seconds."
            while(jvmMBean == ""):
		print "DEBUG: Counter: " + str(sleepCounter) + " seconds."
                if(sleepCounter < timeout):
                    time.sleep(5)
                    sleepCounter = sleepCounter + 5
                    jvmMBean = AdminControl.queryNames("type=Server,node=" + nodeName + ",name=" + jvmName + ",*")
                else:
                    print "Exception: startJVM: Quit waiting since startup did not finish within 1200 sec"
                    raise Exception, "Script raised exception!!!"
            print "INFO: startJVM: " + jvmName + " on " + nodeName + " is now started, took approx. " + str(sleepCounter) + " sec to start"
        else:
            print "Exception: startJVM: Bad checkStatus option passed, " + checkStatus
    else:
        print "INFO: startJVM: " + jvmName + " on " + nodeName + " is already started!!!"

    #print "DEBUG: END: startJVM"
    return

def JVMOp(jvmName, nodeName, op):
    #print "DEBUG: START: JVMOp"

    if(op.upper() == "STOP"):
        stopJVM(jvmName, nodeName, 1)
    elif(op.upper() == "START"):
        startJVM(jvmName, nodeName, 1)
    elif(op.upper() == "RESTART"):
        stopJVM(jvmName, nodeName, 1)
        startJVM(jvmName, nodeName, 1)
    elif(op.upper() == "JAVACORE"):
        threadDump(jvmName, nodeName)
    elif(op.upper() == "HEAPDUMP"):
        heapDump(jvmName, nodeName)
    else:
        print "Exception: JVMOp: Bad JVM operation parameter"
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    #print "DEBUG: END: JVMOp"
    return

def clusterOp(clusterName, op):
    #print "DEBUG: START: clusterOp"

    clusId = AdminConfig.getid('/Cell:' + cellName + '/ServerCluster:' + clusterName + '/')
    if(clusId == ""):
        print "Exception: clusterOp: Bad clusterName passed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    # Refresh the cluster manager MBean
    clusterMgrMBean = AdminControl.queryNames('cell=' + cellName + ',type=ClusterMgr,*')
    AdminControl.invoke(clusterMgrMBean, 'retrieveClusters')

    clusterMembers = AdminConfig.list('ClusterMember', clusId)
    clusterMBean = AdminControl.completeObjectName('WebSphere:type=Cluster,name=' + clusterName + ',*')
    if(clusterMBean == ""):
        print "Exception: clusterOp: Looks like you are working off of a temporary/unsable config"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    state = AdminControl.getAttribute(clusterMBean, 'state')

    if(op.upper() == "STOP"):
        #AdminControl.invoke(clusterMBean, 'stop')
        for member in clusterMembers.split(lineSep):
            jvmName = AdminConfig.showAttribute(member, 'memberName')
            nodeName = AdminConfig.showAttribute(member, 'nodeName')
            stopJVM(jvmName, nodeName, 1)
    elif(op.upper() == "START"):
        #AdminControl.invoke(clusterMBean, 'start')
        for member in clusterMembers.split(lineSep):
            jvmName = AdminConfig.showAttribute(member, 'memberName')
            nodeName = AdminConfig.showAttribute(member, 'nodeName')
            startJVM(jvmName, nodeName, 1)
    elif(op.upper() == "RIPPLE"):
        #AdminControl.invoke(clusterMBean, 'rippleStart')
        for member in clusterMembers.split(lineSep):
            jvmName = AdminConfig.showAttribute(member, 'memberName')
            nodeName = AdminConfig.showAttribute(member, 'nodeName')
            stopJVM(jvmName, nodeName, 1)
            startJVM(jvmName, nodeName, 1)
            #jvmMBean = AdminControl.completeObjectName('WebSphere:type=Server,node=' + nodeName + ',process=' + jvmName + ',*')
            #AdminControl.invoke(jvmMBean, "restart")
            #print "INFO: clusterOp: Issued restart to " + jvmName + " on node " + nodeName
            #clusterMgr = AdminControl.queryNames('cell=' + cellName + ',type=ClusterMgr,*')
            #AdminControl.invoke(clusterMgr, 'retrieveClusters')
            #clusMName = AdminControl.queryNames('mbeanIdentifier=' + clusterName + ',type=Cluster,cell=' + cellName + ',*')
            #AdminControl.invoke(clusMName, 'rippleStart')
            #print "INFO: clusterOp: Issued ripple start, please verify all your JVMs have restarted"
    elif(op.upper() == "RESTART"):
        for member in clusterMembers.split(lineSep):
            jvmName = AdminConfig.showAttribute(member, 'memberName')
            nodeName = AdminConfig.showAttribute(member, 'nodeName')
            stopJVM(jvmName, nodeName, 1)
        for member in clusterMembers.split(lineSep):
            jvmName = AdminConfig.showAttribute(member, 'memberName')
            nodeName = AdminConfig.showAttribute(member, 'nodeName')
            startJVM(jvmName, nodeName, 1)
    elif(op.upper() == "STOPIMMEDIATE"):
        print "INFO: clusterOp: Immediate stopping cluster: " + clusterName
        AdminControl.invoke(clusterMBean, 'stop', 'stopImmediate')
    elif(op.upper() == "JAVACORE"):
        for member in clusterMembers.split(lineSep):
            jvmName = AdminConfig.showAttribute(member, 'memberName')
            nodeName = AdminConfig.showAttribute(member, 'nodeName')
            threadDump(jvmName, nodeName)
    elif(op.upper() == "HEAPDUMP"):
        for member in clusterMembers.split(lineSep):
            jvmName = AdminConfig.showAttribute(member, 'memberName')
            nodeName = AdminConfig.showAttribute(member, 'nodeName')
            heapDump(jvmName, nodeName)
    else:
        print "Exception: clusterOp: Bad cluster operation parameter: "  + op.upper()
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    #print "DEBUG: END: clusterOp"
    return