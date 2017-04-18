# This is an stand-alone script

def monitorSettings(svrState):
    jvmIdList = AdminTask.listServers('[-serverType APPLICATION_SERVER]')
    for jvmId in jvmIdList.split(lineSep):
        jvmName = AdminConfig.showAttribute(jvmId, 'name')
        nodeName = jvmId.split('/')[3]
        jvmObjId = jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
        if(jvmObjId == ""):
            print "Exception: monitorSettings: Bad jvmName, or nodeName passed"
            raise Exception, "Script raised exception, you are doing something wrong!!!"
        objName = AdminConfig.getObjectName(jvmObjId)
        if(objName == ""):
            print objName
            monitor = AdminConfig.list('MonitoringPolicy', jvmId)
            state = AdminConfig.showAttribute(monitor, 'nodeRestartState')
            print "INFO: monitorSettings: Node restart state " + jvmName + ", " + nodeName + ": " + state
            AdminConfig.modify(monitor, [['nodeRestartState', svrState]])
            state = AdminConfig.showAttribute(monitor, 'nodeRestartState')
            print "INFO: monitorSettings: Changed to state: " + state
    return

lineSep  = java.lang.System.getProperty('line.separator')
monitorSettings("PREVIOUS")