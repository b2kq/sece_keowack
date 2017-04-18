# This is a stand-alone script

def jvmLogLevel(jvmName, nodeName, logLevel):
    jvmId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + jvmName + '/')
    if(jvmId == ""):
        print "ERROR: jvmLogLevel: Bad server name passed: " + jvmName
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    tc = AdminConfig.list('TraceService', jvmId)
    curtc = AdminConfig.showAttribute(tc, 'startupTraceSpecification')
    if(curtc != logLevel):
        AdminConfig.modify(tc, [['startupTraceSpecification', logLevel]])
        print "INFO: jvmLogLevel: Changed log level from " + curtc + " to " + logLevel + " for " + jvmName + ", " + nodeName
    inptstrg = 'type=TraceService,process=' + jvmName + ',*'
    objNameString = AdminControl.completeObjectName(inptstrg)
    curTraceSpec = AdminControl.getAttribute(objNameString, 'traceSpecification')
    if(curTraceSpec != logLevel):
        AdminControl.setAttribute(objNameString, 'traceSpecification', logLevel)
        print "INFO: jvmLogLevel: Changed run-time log level to " + logLevel + " for " + jvmName + ", " + nodeName
    return

def toogleVerboseGC(jvmName, nodeName, enable):
    #print "DEBUG: START: toogleVerboseGC"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    processDef = AdminConfig.list('JavaVirtualMachine', jvmId)
    curMode = AdminConfig.showAttribute(processDef, 'verboseModeGarbageCollection')
    if(curMode != enable.lower()):
        AdminConfig.modify(processDef, [['verboseModeGarbageCollection', enable]])
        print "INFO: toogleVerboseGC: Toogled verbose GC mode from " + curMode + " to " + enable + " for " + jvmName + ", " + nodeName
    inptstrg = 'type=JVM,process=' + jvmName + ',node=' + nodeName + ',*'
    objNameString = AdminControl.completeObjectName(inptstrg)
    if(objNameString != ""):
        AdminControl.invoke(objNameString, 'setVerbose', '[false]', '[boolean]')
        print "INFO: toogleVerboseGC: Toogled verbose GC run-time mode to " + enable + " for " + jvmName + ", " + nodeName
    #print "DEBUG: END: toogleVerboseGC"
    return

def ALL():
    hamList = AdminConfig.list("HAManagerService")
    for ham in hamList.split(lineSep):
        temp = ham.split("/")[5]
        jvmName = temp.split("|")[0]
        nodeName = ham.split("/")[3]
        #if((jvmName == "dmgr") | (jvmName == "nodeagent")):
        #    print "INFO: ALL: Skipping " + jvmName + " " + nodeName
        #else:
            ###jvmLogLevel(jvmName, nodeName, "*=info:com.kahg.*=warning:com.usg.*=warning")
            #jvmLogLevel(jvmName, nodeName, "*=warning:com.ibm.*=info")
        toogleVerboseGC(jvmName, nodeName, "false")
    return

lineSep  = java.lang.System.getProperty('line.separator')
#ALL()
#AdminConfig.save()
