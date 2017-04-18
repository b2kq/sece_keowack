def createJVM(jvmName, nodeName):
    #print "DEBUG: START: createJVM"
    nodeId = AdminConfig.getid('/Node:' + nodeName + '/')
    if(nodeId == ""):
        print "Exception: createJVM: Bad node name passed: " + nodeName
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    jvmId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + jvmName + '/')
    if(jvmId == ""):
        jvmId = AdminConfig.create('Server', nodeId, [['name', jvmName]])
        print "INFO: createJVM: Created JVM " + jvmName + " on node " + nodeName
    #else:
    #    print "INFO: createJVM: " + jvmName + " on node " + nodeName + " already exists"
    #print "DEBUG: END: createJVM"
    return jvmId

def createCoreGroup(coreGroup):
    #print "DEBUG: START: createCoreGroup"
    FLAG = AdminTask.doesCoreGroupExist('[-coreGroupName ' + coreGroup + ']')
    if (FLAG != 'true'):
        coreId = AdminTask.createCoreGroup('[-coreGroupName ' + coreGroup + ']')
        print 'INFO: createCoreGroup: Coregroup ' + coreGroup + ' built'
    #else:
    #    print 'INFO: createCoreGroup: Coregroup ' + coreGroup + ' already exists'
    #print "DEBUG: END: createCoreGroup"
    return

# Do not invoke this function without adding cluster members first, will do you no good
def changeClusterCoreGroup(clusterName, tCoreGroup):
    #print "DEBUG: START: changeClusterCoreGroup"
    changeCG = 0
    clusId = AdminConfig.getid('/Cell:' + cellName + '/ServerCluster:' + clusterName + '/')
    if(clusId == ""):
        print "Exception: clusterOp: Bad clusterName passed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    clusterMembers = AdminConfig.list('ClusterMember', clusId)
    for member in clusterMembers.split(lineSep):
        jvmName = AdminConfig.showAttribute(member, 'memberName')
        nodeName = AdminConfig.showAttribute(member, 'nodeName')
        curCoreGroup = AdminTask.getCoreGroupNameForServer('[-nodeName ' + nodeName + ' -serverName ' + jvmName + ']')
        if(curCoreGroup != tCoreGroup):
            changeCG = changeCG + 1
    clusterMBean = AdminControl.completeObjectName('WebSphere:type=Cluster,name=' + clusterName + ',*')
    if(clusterMBean != ""):
        state = AdminControl.getAttribute(clusterMBean, 'state')
    else:
        state = "websphere.cluster.stopped"
    if(changeCG > 0):
        if(state == "websphere.cluster.stopped"):
            AdminTask.moveClusterToCoreGroup('[-source ' + curCoreGroup + ' -target ' + tCoreGroup + ' -clusterName ' + clusterName + ']')
            print "INFO: changeClusterCoreGroup: Moved cluster " + clusterName + " to coregroup " + tCoreGroup
        else:
            print "WARNING: changeClusterCoreGroup: Cannot change cluster core group because the cluster is not stopped"
    #print "DEBUG: END: changeClusterCoreGroup"
    return

def createCluster(clusterName, replicate):
    #print "DEBUG: START: createCluster"
    if((replicate.upper() == "TRUE") or (replicate.upper() == "YES")):
        DRS = 'true'
    elif((replicate.upper() == "FALSE") or (replicate.upper() == "NO")):
        DRS = 'false'
    elif(replicate == ""):
        DRS = 'false'
    else:
        print "Exception: createCluster: Replication can only be TRUE/FALSE/YES/NO"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    exists = AdminConfig.getid('/ServerCluster:' + clusterName + '/')
    if(exists == ""):
        AdminTask.createCluster('[-clusterConfig [[' + clusterName + ' true "" ""]] -replicationDomain [[' + DRS + ']]]')
        print "INFO: createCluster: " + clusterName + " built"
    #else:
    #    print "INFO: createCluster: " + clusterName + " already exists"
    #print "DEBUG: END: createCluster"
    return

def HAMTask(jvmName, nodeName, task):
    #print "DEBUG: START: HAMTask"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    if(jvmId == ""):
        print "Exception: HAMTask: Bad jvmName, or nodeName passed"
        return
    hamId = AdminConfig.list("HAManagerService", jvmId)
    currentStatus = AdminConfig.showAttribute(hamId, 'enable')
    if(task.lower() != currentStatus):
        AdminConfig.modify(hamId, [["enable", task]])
        print "INFO: HAMTask: Changed HA manager service enable for " + jvmName + ", " + nodeName + " from " + currentStatus + " to " + task
    #print "DEBUG: END: HAMTask"
    return

def addClusterMember(clusterName, jvmName, nodeName):
    #print "DEBUG: START: addClusterMember"
    jvmId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + jvmName + '/')
    if(jvmId == ""):
        clusId = AdminConfig.getid('/Cell:' + cellName + '/ServerCluster:' + clusterName + '/')
        nodeId = AdminConfig.getid('/Node:' + nodeName + '/')
        if(nodeId == ""):
            print "Exception: addClusterMember: The nodename you have specified is incorrect"
            raise Exception, "Script raised exception, you are doing something wrong!!!"
        name = ['memberName', jvmName]
        attrs = [name]
        jvmId = AdminConfig.createClusterMember(clusId, nodeId, attrs)
        print "INFO: addClusterMember: Member " + jvmName + ", " + nodeName + " built"
    #else:
    #    print "INFO: addClusterMember: Member already exists, " + jvmName + ", " + nodeName
    #print "DEBUG: END: addClusterMember"
    return

# prsType: DATA_REPLICATION, DATABASE, NONE(default)
# cookieName: JSESSIONID(default)
# timeout: 30(default)
def changeJVMSessionSettings(jvmName, nodeName, cookieName, timeout, prsType, rplDomain, rplMode):
    #print "DEBUG: START: changeJVMSessionSettings"
    dCookieName = 'JSESSIONID'
    dPersistanceType = 'NONE'
    dSessionTimout = '30'
    if(prsType == "DATABASE"):
        print "Exception: changeJVMSessionSettings: This script does not support DATABASE session persistance!!!"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    if(prsType == ""):
        prsType = dPersistanceType
    if(cookieName == ""):
        cookieName = dCookieName
    if(timeout == ""):
        timeout = dSessionTimout
    jvmId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + jvmName + '/')
    smgr = AdminConfig.list('SessionManager', jvmId)
    drsId = AdminConfig.list('DRSSettings', smgr)

    #attr1 = ['sessionPersistenceMode', prsType]
    #attr2 = ['enableCookies', 'true']
    #attr3 = ['invalidationTimeout', timeout]
    #tuningParmsDetailList = [attr3]
    #tuningParamsList = ['tuningParams', tuningParmsDetailList]
    #kuki = ['name', cookieName]
    #cookie = [kuki]
    #cookieSettings = ['defaultCookieSettings', cookie]
    #drsCluster = ['messageBrokerDomainName', rplDomain]
    #drsPropList = [drsCluster]
    #drsSettings = ['sessionDRSPersistence', drsPropList]
    #AdminConfig.modify(smgr, [attr1, attr2, tuningParamsList, cookieSettings, drsSettings])
    #print "INFO: changeJVMSessionSettings: Finished modifying SESSION MGMT settings"

    cookieId = AdminConfig.list('Cookie', smgr)
    curkukiname = AdminConfig.showAttribute(cookieId, 'name')
    if(curkukiname != cookieName):
        AdminConfig.modify(cookieId, [['name', cookieName]])
        print "INFO: changeJVMSessionSettings: Changed " + jvmName + ", " + nodeName + " cookie name from " + curkukiname + " to " + cookieName

    tuningParmsId = AdminConfig.list('TuningParams', smgr)
    AdminConfig.modify(tuningParmsId, [['allowOverflow', 'false']])
    print "INFO: changeJVMSessionSettings: Changed " + jvmName + ", " + nodeName + " to disable allowOverflow"
    curinvalidationTimeout = AdminConfig.showAttribute(tuningParmsId, 'invalidationTimeout')
    if(curinvalidationTimeout != timeout):
        AdminConfig.modify(tuningParmsId, [['invalidationTimeout', timeout]])
        print "INFO: changeJVMSessionSettings: Changed " + jvmName + ", " + nodeName + " session invalidation timeout from " + curinvalidationTimeout + " to " + timeout

    cursessionPersistenceMode = AdminConfig.showAttribute(smgr, 'sessionPersistenceMode')
    if(cursessionPersistenceMode != prsType):
        AdminConfig.modify(smgr, [['sessionPersistenceMode', prsType]])
        print "INFO: changeJVMSessionSettings: Changed " + jvmName + ", " + nodeName + " sessionPersistenceMode from " + cursessionPersistenceMode + " to " + prsType

    if(prsType == "DATA_REPLICATION"):
        curRplDomain = AdminConfig.showAttribute(drsId, 'messageBrokerDomainName')
        if(curRplDomain != rplDomain):
            drdId = AdminConfig.getid('/DataReplicationDomain:' + rplDomain + '/')
            if(drdId == ""):
                print "ERROR: changeJVMSessionSettings: Data replication domain " + rplDomain + " does not exist"
                print "ERROR: changeJVMSessionSettings: This script does not yet support creating data replication domains"
                print "ERROR: changeJVMSessionSettings: Please create the domain manually, and rerun the script"
                raise Exception, "Script raised exception, fix the above error and come back again!!!"
            AdminConfig.modify(drsId, [['messageBrokerDomainName', rplDomain]])
            print "INFO: changeJVMSessionSettings: Changed " + jvmName + ", " + nodeName + " data replication domain from " + curRplDomain + " to " + rplDomain
        curRplMode = AdminConfig.showAttribute(drsId, 'dataReplicationMode')
        if(curRplMode != rplMode):
            AdminConfig.modify(drsId, [['dataReplicationMode', rplMode]])
            print "INFO: changeJVMSessionSettings: Changed " + jvmName + ", " + nodeName + " data replication mode from " + curRplMode + " to " + rplMode

    #print "DEBUG: END: changeJVMSessionSettings"
    return

def modifyORBProperty(jvmName, nodeName, propName, propValue):
    #print "DEBUG: START: modifyORBProperty"
    jvmId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
    orbId = AdminConfig.list('ObjectRequestBroker', jvmId)
    props = AdminConfig.showAttribute(orbId, 'properties')
    # Call the function in common.py
    addModifyProperty(orbId, props, propName, propValue)
    #print "DEBUG: END: modifyORBProperty"
    return

def modifyWCProperty(jvmName, nodeName, propName, propValue):
    #print "DEBUG: START: modifyWCProperty"
    serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
    webContainerId = AdminConfig.list("WebContainer", serverId)
    props = AdminConfig.showAttribute(webContainerId, 'properties')
    # Call the function in common.py
    addModifyProperty(webContainerId, props, propName, propValue)
    #print "DEBUG: END: modifyWCProperty"
    return

def modifyProcessDefProperty(jvmName, nodeName, propName, propValue):
    #print "DEBUG: START: modifyProcessDefProperty"
    serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
    processDef = AdminConfig.list('JavaProcessDef', serverId)
    props = AdminConfig.showAttribute(processDef, 'environment')
    # Call the function in common.py
    addModifyProperty(processDef, props, propName, propValue)
    #print "DEBUG: END: modifyProcessDefProperty"
    return

# Will modify if property already exists, or create new if it does not
def modifyJVMProperty(jvmName, nodeName, propName, propValue):
    #print "DEBUG: START: modifySystemProps"
    serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
    processDef = AdminConfig.list('JavaVirtualMachine', serverId)
    props = AdminConfig.showAttribute(processDef, 'systemProperties')
    # Call the function in common.py
    addModifyProperty(processDef, props, propName, propValue)
    #print "DEBUG: END: modifySystemProps"
    return

def customService(jvmName, nodeName, svcName, className, classPath, startupEnabled, description):
    #print "DEBUG: START: customService"
    # Create the property list
    CSdisplayName = ['displayName', svcName]
    CSclassname = ['classname', className]
    CSclasspath = ['classpath', classPath]
    CSdescription = ['description', description]
    CSenable = ['enable', startupEnabled]
    CSattributes =  [CSdisplayName, CSclassname, CSclasspath, CSdescription, CSenable]
    # Add/modify the customer service
    serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
    cServices = AdminConfig.list('CustomService', serverId)
    found = 0
    for cService in cServices.split("\r\n"):
        if(cService != ""):
            oServiceName = AdminConfig.showAttribute(cService, 'displayName')
            if(oServiceName == CSdisplayName[1]):
                AdminConfig.modify(cService, CSattributes)
                found = 1
                print "INFO: customService: Modified custom service: " + oServiceName
    if(found == 0):
        cService = AdminConfig.create('CustomService', serverId, CSattributes)
        print "INFO: customService: Added custom service: " + svcName

    #print "DEBUG: END: customService"
    return cService

def modifyCustomServiceProperty(cService, propName, propValue):
    #print "DEBUG: START: modifyCustomServiceProperty"
    props = AdminConfig.showAttribute(cService, 'properties')
    # Call the function in common.py
    addModifyProperty(cService, props, propName, propValue)
    #print "DEBUG: END: modifyCustomServiceProperty"
    return

# appendFlag = 0 or 1 (does not work for WAS 6, always appends)
def modifyClasspath(jvmName, nodeName, appendPath, appendFlag):
    #print "DEBUG: START: modifyClasspath"
    serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
    processDef = AdminConfig.list('JavaVirtualMachine', serverId)
    curCPath = AdminConfig.showAttribute(processDef, 'classpath')
    if(appendFlag == 1):
        exists = curCPath.find(appendPath)
        if(exists == -1):
            newCPath = curCPath + ';' + appendPath
        else:
            newCPath = curCPath
    else:
        newCPath = appendPath
    classPath = ['classpath', newCPath]
    classPath = [classPath]
    AdminConfig.modify(processDef, classPath)
    print "INFO: modifyClasspath: Modified classpath to " + newCPath
    #print "DEBUG: END: modifyClasspath"
    return

#########################################################################################
#		   Old function; new function is found below
#########################################################################################
# Whatever is the value of args will be the target value, so fill args will all the stuff
#def setGenericJVMArgs(jvmName, nodeName, args):
    #print "DEBUG: START: setGenericJVMArgs"
#    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
#    processDef = AdminConfig.list('JavaVirtualMachine', jvmId)
#    AdminConfig.modify(processDef, [['genericJvmArguments', args]])
#    print "INFO: setGenericJVMArgs: Modified generic JVM args to " + args
    #print "DEBUG: END: setGenericJVMArgs"
#    return
##########################################################################################

def setGenericJVMArgs(jvmName, nodeName, args):
    #print "DEBUG: START: setGenericJVMArgs"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    processDef = AdminConfig.list('JavaVirtualMachine', jvmId)
    origJVMArgs = AdminConfig.showAttribute(processDef, 'genericJvmArguments')

    #Keep existing parameters (if any)
    if(origJVMArgs != None):
        if(origJVMArgs.find(args) < 0):
            args = origJVMArgs + " " + args
            AdminConfig.modify(processDef, [['genericJvmArguments', args]])
            print "INFO: setGenericJVMArgs: Modified generic JVM args to " + args
    else:
        AdminConfig.modify(processDef, [['genericJvmArguments', args]])
        print "INFO: setGenericJVMArgs: Modified generic JVM args to " + args

    #print "DEBUG: END: setGenericJVMArgs"
    return

def JVMLogSettings(jvmName, nodeName, type, location, format, rollType, noBkp, rollSize, baseHr, rollPrd, fmtW, supW, supST):
    #print "DEBUG: START: JVMLogSettings"
    serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
    if(type == "out"):
        log = AdminConfig.showAttribute(serverId, 'outputStreamRedirect')
        if(location == ""):
            location = "$(LOG_ROOT)/$(SERVER)/SystemOut.log"
    else:
        log = AdminConfig.showAttribute(serverId, 'errorStreamRedirect')
        if(location == ""):
            location = "$(LOG_ROOT)/$(SERVER)/SystemErr.log"

    #fileName = ["fileName", location]
    #messageFormatKind = ["messageFormatKind", format]
    #rolloverType = ["rolloverType", rollType]
    #maxNumberOfBackupFiles = ["maxNumberOfBackupFiles", noBkp]
    #rolloverSize = ["rolloverSize", rollSize]
    #baseHour = ["baseHour", baseHr]
    #rolloverPeriod = ["rolloverPeriod", rollPrd]
    #formatWrites = ["formatWrites", fmtW]
    #suppressWrites = ["suppressWrites", supW]
    #suppressStackTrace = ["suppressStackTrace", supST]
    #attrs = []
    #attrs.append(fileName)
    #attrs.append(rolloverType)
    #attrs.append(maxNumberOfBackupFiles)
    #attrs.append(rolloverSize)
    #attrs.append(baseHour)
    #attrs.append(rolloverPeriod)
    #attrs.append(formatWrites)
    #attrs.append(suppressWrites)
    #attrs.append(suppressStackTrace)
    #AdminConfig.modify(log, attrs)
    #print "INFO: JVMLogSettings: Modified JVM logging setting for " + jvmName + ", " + nodeName

    curRollOverType = AdminConfig.showAttribute(log, 'rolloverType')
    if(curRollOverType != rollType.upper()):
        AdminConfig.modify(log, [['rolloverType', rollType.upper()]])
        print "INFO: JVMLogSettings: Modified JVM System" + type + " rolloverType from " + curRollOverType + " to " + rollType

    curBackupFiles = AdminConfig.showAttribute(log, 'maxNumberOfBackupFiles')
    if(curBackupFiles != noBkp):
        AdminConfig.modify(log, [['maxNumberOfBackupFiles', noBkp]])
        print "INFO: JVMLogSettings: Modified JVM System" + type + " maxNumberOfBackupFiles from " + curBackupFiles + " to " + noBkp

    currolloverSize = AdminConfig.showAttribute(log, 'rolloverSize')
    if(currolloverSize != rollSize):
        AdminConfig.modify(log, [['rolloverSize', rollSize]])
        print "INFO: JVMLogSettings: Modified JVM System" + type + " rolloverSize from " + currolloverSize + " to " + rollSize

    curbaseHour = AdminConfig.showAttribute(log, 'baseHour')
    if(curbaseHour != baseHr):
        AdminConfig.modify(log, [['baseHour', baseHr]])
        print "INFO: JVMLogSettings: Modified JVM System" + type + " baseHour from " + curbaseHour + " to " + baseHr

    currolloverPeriod = AdminConfig.showAttribute(log, 'rolloverPeriod')
    if(currolloverPeriod != rollPrd):
        AdminConfig.modify(log, [['rolloverPeriod', rollPrd]])
        print "INFO: JVMLogSettings: Modified JVM System" + type + " rolloverPeriod from " + currolloverPeriod + " to " + rollPrd

    #print "DEBUG: END: JVMLogSettings"

def monitorSettings(jvmName, nodeName, startupAtmp, pingInt, pingTime, autoRstrt, svrState):
    #print "DEBUG: START: monitorSettings"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    monitor = AdminConfig.list('MonitoringPolicy', jvmId)

    curmaximumStartupAttempts = AdminConfig.showAttribute(monitor, 'maximumStartupAttempts')
    if(curmaximumStartupAttempts != startupAtmp):
        AdminConfig.modify(monitor, [['maximumStartupAttempts', startupAtmp]])
        print "INFO: monitorSettings: Modified " + jvmName + ", " + nodeName + " maximumStartupAttempts from " + curmaximumStartupAttempts + " to " + startupAtmp

    curpingInterval = AdminConfig.showAttribute(monitor, 'pingInterval')
    if(curpingInterval != pingInt):
        AdminConfig.modify(monitor, [['pingInterval', pingInt]])
        print "INFO: monitorSettings: Modified " + jvmName + ", " + nodeName + " pingInterval from " + curpingInterval + " to " + pingInt

    curpingTimeout = AdminConfig.showAttribute(monitor, 'pingTimeout')
    if(curpingTimeout != pingTime):
        AdminConfig.modify(monitor, [['pingTimeout', pingTime]])
        print "INFO: monitorSettings: Modified " + jvmName + ", " + nodeName + " pingTimeout from " + curpingTimeout + " to " + pingTime

    curautoRestart = AdminConfig.showAttribute(monitor, 'autoRestart')
    if(curautoRestart != autoRstrt.lower()):
        AdminConfig.modify(monitor, [['autoRestart', autoRstrt]])
        print "INFO: monitorSettings: Modified " + jvmName + ", " + nodeName + " autoRestart from " + curautoRestart + " to " + autoRstrt

    curnodeRestartState = AdminConfig.showAttribute(monitor, 'nodeRestartState')
    if(curnodeRestartState != svrState.upper()):
        AdminConfig.modify(monitor, [['nodeRestartState', svrState.upper()]])
        print "INFO: monitorSettings: Modified " + jvmName + ", " + nodeName + " nodeRestartState from " + curnodeRestartState + " to " + svrState

    #print "DEBUG: END: monitorSettings"
    return

def modifyMinHeap(jvmName, nodeName, minHeap):
    #print "DEBUG: START: modifyMinHeap"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    processDef = AdminConfig.list('JavaVirtualMachine', jvmId)
    curInitHeap = AdminConfig.showAttribute(processDef, 'initialHeapSize')
    if(curInitHeap != minHeap):
        AdminConfig.modify(processDef, [['initialHeapSize', minHeap]])
        print "INFO: modifyMinHeap: Modified JVM initial heap size from " + curInitHeap + " to " + minHeap
    #print "DEBUG: END: modifyMinHeap"
    return

def modifyMaxHeap(jvmName, nodeName, maxHeap):
    #print "DEBUG: START: modifyMaxHeap"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    processDef = AdminConfig.list('JavaVirtualMachine', jvmId)
    curMaxHeap = AdminConfig.showAttribute(processDef, 'maximumHeapSize')
    if(curMaxHeap != maxHeap):
        AdminConfig.modify(processDef, [['maximumHeapSize', maxHeap]])
        print "INFO: modifyMaxHeap: Modified JVM maximum heap size from " + curMaxHeap + " to " + maxHeap
    #print "DEBUG: END: modifyMaxHeap"
    return

# enable: true/false
def toogleVerboseGC(jvmName, nodeName, enable):
    #print "DEBUG: START: toogleVerboseGC"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    processDef = AdminConfig.list('JavaVirtualMachine', jvmId)
    curMode = AdminConfig.showAttribute(processDef, 'verboseModeGarbageCollection')
    if(curMode != enable.lower()):
        AdminConfig.modify(processDef, [['verboseModeGarbageCollection', enable]])
        print "INFO: toogleVerboseGC: Toogled verbose GC mode from " + curMode + " to " + enable
    #print "DEBUG: END: toogleVerboseGC"
    return

def transactionSvcProps(jvmName, nodeName, ttlt, pobtlt):
    #print "DEBUG: START: transactionSvcProps"
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    transactionSvcId = AdminConfig.list('TransactionService', jvmId)
    curTranLife = AdminConfig.showAttribute(transactionSvcId, 'totalTranLifetimeTimeout')
    if((ttlt != curTranLife) & (ttlt != "") & (ttlt != 0)):
        AdminConfig.modify(transactionSvcId, [['totalTranLifetimeTimeout', ttlt]])
        print "INFO: transactionSvcProps: Modified TotalTranLifetimeTimeout from " + curTranLife + " to " + ttlt
    curBMT = AdminConfig.showAttribute(transactionSvcId, 'propogatedOrBMTTranLifetimeTimeout')
    if((pobtlt != curBMT) & (pobtlt != "") & (pobtlt != 0)):
        AdminConfig.modify(transactionSvcId, [['propogatedOrBMTTranLifetimeTimeout', pobtlt]])
        print "INFO: transactionSvcProps: Modified PropogatedOrBMTTranLifetimeTimeout from " + curBMT + " to " + pobtlt
    #print "DEBUG: END: transactionSvcProps"
    return