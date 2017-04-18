def buildTask(rootElement):
    #print "DEBUG: START: buildTask"

    # Build/Modify J2C Auth entries if any
    securityNode = rootElement.getElementsByTagName("Security").item(0)
    if(securityNode != None):
        j2cNode = securityNode.getElementsByTagName("J2CAuthData").item(0)
        if(j2cNode != None):
            j2cList = j2cNode.getElementsByTagName("J2C")
            for jCt in range(j2cList.getLength()):
                j2cItem = j2cList.item(jCt)
                alias = getTagValue(j2cItem, "Alias")
                uName = getTagValue(j2cItem, "Username")
                pwd = getTagValue(j2cItem, "Password")
                desc = getTagValue(j2cItem, "Description")
                createJ2CAlias(alias, uName, pwd, desc)

    # Setup some global resource under "Environment"
    envNode = rootElement.getElementsByTagName("Environment").item(0)
    if(envNode != None):
        # Setup virtual hosts, always cell level
        #vhostList = envNode.getElementsByTagName("VirtualHost")
        #for i in range(vhostList.getLength()):
        #    vhost = vhostList.item(i)
        #    vhName = getTagValue(vhost, "VirtualHostName")
        #    vhId = setupVirtualHost(vhName)
        #    aliasList = vhost.getElementsByTagName("HostAlias")
        #    for j in range(aliasList.getLength()):
        #        aliasName = getTagValue(aliasList.item(j), "HostAliasName")
        #        aliasPort = getTagValue(aliasList.item(j), "HostAliasPort")
        #        setupVHAlias(vhId, aliasName, aliasPort)
        # Setup name space binding, at cell level, if required
        nameSpaceList = envNode.getElementsByTagName("NameSpace")
        namespace("", "", nameSpaceList)

    # Build cell level resources and properties if CellResources TAG exits
    cellResNode = rootElement.getElementsByTagName("CellResources").item(0)
    if(cellResNode != None):
            configResources("", "", cellResNode)

    # Build web servers if WebServer TAG exists
    webSvrNode = rootElement.getElementsByTagName("WebServer").item(0)
    if(webSvrNode != None):
        configWebServer(webSvrNode)

    nodeNode = rootElement.getElementsByTagName("Node").item(0)
    appSvrNode = rootElement.getElementsByTagName("ApplicationServer").item(0)
    if(appSvrNode != None):
        serverName = getTagValue(appSvrNode, 'ServerName')
        clusterName = getTagValue(appSvrNode, 'ClusterName')
        # Check if both ServerName and ClusterName tags are present
        if(((serverName == "") & (clusterName == "")) | ((serverName != "") & (clusterName != ""))):
            print "Exception: configJVM: Specify either a <ServerName> or a <ClusterName>"
            raise Exception, "Script raised exception, you are doing something wrong!!!"
        # Set the appropriate scope
        if(DMGR == "TRUE"):
            if(serverName == ""):
                CLUSTERED = "TRUE"
            else:
                CLUSTERED = "FALSE"
        else:
            CLUSTERED = "FALSE"

    # Build node resource and properties if Node TAG exits
    if(nodeNode != None):
        configNode(nodeNode)
        # Build cluster, JVM, jvm level resources, etc.
        if(appSvrNode != None):
            configJVM(nodeNode, appSvrNode, CLUSTERED)

    # Resources at cluster level
    if(appSvrNode != None):
        if(CLUSTERED == "TRUE"):
            clusterResNode = rootElement.getElementsByTagName("ClusterResources").item(0)
            if(clusterResNode != None):
                configResources(clusterName, "", clusterResNode)
    		#Added by Nik to add Wily to all new environments
                #if(clusterName != "PortalCluster"):
                #    wily("TRUE", clusterName)

    if(SAVE == 1):
        saveSync("sync")

    #print "DEBUG: END: buildTask"
    return

def configWebServer(webSvrNode):
    #print "DEBUG: START: configWebServer" 

    serverName = getTagValue(webSvrNode, 'Name')
    serverPort = getTagValue(webSvrNode, 'Port')
    if(serverPort == ""):
        print "Exception: configWebServer: Port tag missing"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    webRoot = getTagValue(webSvrNode, 'WebRoot')
    plgRoot = getTagValue(webSvrNode, 'PluginRoot')
    webConf = getTagValue(webSvrNode, 'WebConf')
    plgConf = getTagValue(webSvrNode, 'PluginConf')
    plgLog  = getTagValue(webSvrNode, 'PluginLog')
    svcName = getTagValue(webSvrNode, 'ServiceName')
    nodeList = webSvrNode.getElementsByTagName("Node")
    for i in range(nodeList.getLength()):
        nodeName = getTagValue(nodeList.item(i), "NodeName")
        hostName = getTagValue(nodeList.item(i), "HostName")
        nodeOS   = getTagValue(nodeList.item(i), "NodeOS")
        nodeId = buildUnmanagedNode(nodeName, hostName, nodeOS)
        buildWebServer(nodeName, serverName, serverPort, webRoot, webConf, svcName, plgRoot, plgLog, plgConf)

    #print "DEBUG: END: configWebServer"
    return

# Setup node level resources
def configNode(nodeNode):
    #print "DEBUG: START: configNode"

    # Run thru configuration for each node
    nodeList = nodeNode.getElementsByTagName("NodeName")
    for i in range(nodeList.getLength()):
        nodeName = nodeList.item(i).firstChild.nodeValue.strip()
        nodeCfg = nodeNode.getElementsByTagName("NodeConfig").item(0)
        if(nodeCfg != None):
            print "INFO: configNode: Working on node " + nodeName
            configResources("", nodeName, nodeCfg)
            print "INFO: configNode: Finished working on node " + nodeName

    #print "DEBUG: END: configNode"
    return

def configJVM(nodeNode, appSvrNode, CLUSTERED):
    #print "DEBUG: START: configJVM"

    instanceList = appSvrNode.getElementsByTagName("Server")

    # Build the cluster
    if(CLUSTERED == "TRUE"):
        clusterName = getTagValue(appSvrNode, 'ClusterName')
        prsType = getTagValue(instanceList.item(0), "DistributedSessionType")
        if(prsType == "DATA_REPLICATION"):
            createCluster(clusterName, "TRUE")
        else:
            createCluster(clusterName, "FALSE")
    else:
        serverName = getTagValue(appSvrNode, 'ServerName')

    # Create jvms on each node, configure them
    nodeList = nodeNode.getElementsByTagName("NodeName")
    for i in range(nodeList.getLength()):
        nodeName = nodeList.item(i).firstChild.nodeValue.strip()
        # Build JVM on the node
        for j in range(instanceList.getLength()):
            instance = instanceList.item(j)
            if(CLUSTERED == "TRUE"):
                jvmName = clusterName.split("cluster")[0] + "_%s" % (i+1) + "_%s" % (j+1)
                addClusterMember(clusterName, jvmName, nodeName)
            else:
                jvmName = serverName
                createJVM(jvmName, nodeName)

            # Configure the JVM
            print "INFO: configJVM: Working on " + jvmName + " on node " + nodeName

            # Clean some default junk out
            if((DMGR == "TRUE") & (jvmName != 'nodeagent') & (jvmName != 'dmgr')):
                deleteChain(jvmName, nodeName, "WCInboundAdmin")
                deleteChain(jvmName, nodeName, "WCInboundAdminSecure")
                deleteEndPoint(jvmName, nodeName, "WC_adminhost")
                deleteEndPoint(jvmName, nodeName, "WC_adminhost_secure")
                disableTransportChain(jvmName, nodeName, "WCInboundDefaultSecure")
                disableTransportChain(jvmName, nodeName, "HttpQueueInboundDefault")
                disableTransportChain(jvmName, nodeName, "HttpQueueInboundDefaultSecure")
                #deleteEndPoint(jvmName, nodeName, "WC_defaulthost_secure")

	    #Added by Nik to change JVM Log Levels to Warning for UAT and PRD environments
	    if(((env == 'UATWAS') | (env == 'UATWAS8') | (env == 'PRODWAS') | (env == 'PRODWAS8')) & ((jvmName != 'nodeagent') & (jvmName != 'dmgr'))):
	   	jvmId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + jvmName + '/')
    		if(jvmId == ""):
       	            print "Exception: jvmTraceLevel: Bad server name passed: " + jvmName
                    raise Exception, "Script raised exception, you are doing something wrong!!!"
                tc = AdminConfig.list('TraceService', jvmId)
                curtc = AdminConfig.showAttribute(tc, 'startupTraceSpecification')
                if(curtc != "*=warning:com.ibm.*=info"):
                    AdminConfig.modify(tc, [['startupTraceSpecification', "*=warning:com.ibm.*=info"]])
                    print "INFO: jvmTraceLevel: Changed trace level from " + curtc + " to *=warning for " + jvmName + ", " + nodeName	
	    #End of Nik's change
	    
            # Change the HA manager settings; if the tags do not exist, it will be assumed false and turned off
            haMgrNode = instance.getElementsByTagName("HAManager").item(0)
            if(haMgrNode != None):
                haEnabledNode = haMgrNode.getElementsByTagName("Enabled").item(0)
                if(haEnabledNode != None):
                    haFlag = getTagValue(haMgrNode, "Enabled")
                    HAMTask(jvmName, nodeName, haFlag)
            else:
                haFlag = "false"
                HAMTask(jvmName, nodeName, haFlag)

            # Change End Points if required
            epNode = instance.getElementsByTagName("EndPoints").item(0)
            if(epNode != None):
                epList = epNode.getElementsByTagName("PortItem")
                for epC in range(epList.getLength()):
                    ep = epList.item(epC)
                    pName = getTagValue(ep, "PortName")
                    pHost = getTagValue(ep, "Host")
                    pPort = getTagValue(ep, "Port")
                    if(pName == "WC_defaulthost"):
                        modifyEndPoint(jvmName, nodeName, pName, pHost, pPort)
                    else:
                        print "Exception: configJVM: Only the end-point WC_defaulthost is supported"
                        raise Exception, "Script raised exception, you are doing something wrong!!!"

            # Modify Transaction service settings
            tranSvcNode = instance.getElementsByTagName("TransactionService").item(0)
            if(tranSvcNode != None):
                TotalTranLifetimeTimeout = getTagValue(tranSvcNode, "TotalTranLifetimeTimeout")
                PropogatedOrBMTTranLifetimeTimeout = getTagValue(tranSvcNode, "PropogatedOrBMTTranLifetimeTimeout")
                transactionSvcProps(jvmName, nodeName, TotalTranLifetimeTimeout, PropogatedOrBMTTranLifetimeTimeout)

            # Add/Modify ORB settings
            orbNode = instance.getElementsByTagName("ORBService").item(0)
            if(orbNode != None):
                # Add/modify custom properties
                orbPropsNode = orbNode.getElementsByTagName("CustomProperties").item(0)
                if(orbPropsNode != None):
                    orbProps = orbPropsNode.getElementsByTagName("Property")
                    for oCount in range(orbProps.getLength()):
                        orbProp = orbProps.item(oCount)
                        propName = getTagValue(orbProp, "Name")
                        propValue = getTagValue(orbProp, "Value")
                        modifyORBProperty(jvmName, nodeName, propName, propValue)

            # Add/modify WebContainer settings
            wcNode = instance.getElementsByTagName("WebContainer").item(0)
            if(wcNode != None):
                # Build the required internal (and/or) external transport, chains
                #chainList = wcNode.getElementsByTagName("TransportChain")
                #for k in range(chainList.getLength()):
                #    chain = chainList.item(k)
                #    tChainName = getTagValue(chain, "TransportChainName")
                #    tName = getTagValue(chain, "TransportName")
                #    tHost = getTagValue(chain, "TransportHost")
                #    tPort = getTagValue(chain, "TransportPort")
                #    tSSL = getTagValue(chain, "TransportsslEnable")
                #    createChainWithEndPoint(jvmName, nodeName, tChainName, tName, tHost, tPort, tSSL)

                # Modify session settings
                sessMgmtList = wcNode.getElementsByTagName("SessionManagement").item(0)
                if(sessMgmtList != None):
                    cookieName = getTagValue(sessMgmtList, "CookieName")
                    timeout = getTagValue(sessMgmtList, "SessionTimeout")
                    prsType = getTagValue(sessMgmtList, "DistributedSessionType")
                    rplDomain = getTagValue(sessMgmtList, "ReplicationDomain")
                    rplMode = getTagValue(sessMgmtList, "ReplicationMode")
                    changeJVMSessionSettings(jvmName, nodeName, cookieName, timeout, prsType, rplDomain, rplMode)

                # Add/modify custom properties
                wcPropsNode = wcNode.getElementsByTagName("CustomProperties").item(0)
                if(wcPropsNode != None):
                    wcProps = wcPropsNode.getElementsByTagName("Property")
                    for pCount in range(wcProps.getLength()):
                        wcProp = wcProps.item(pCount)
                        propName = getTagValue(wcProp, "Name")
                        propValue = getTagValue(wcProp, "Value")
                        modifyWCProperty(jvmName, nodeName, propName, propValue)

            # Add/modify Process Definiton settings
            processDefNode = instance.getElementsByTagName("ProcessDefinition").item(0)
            if(processDefNode != None):
                pdPropsNode = processDefNode.getElementsByTagName("CustomProperties").item(0)
                if(pdPropsNode != None):
                    pdProps = pdPropsNode.getElementsByTagName("Property")
                    for pdCount in range(pdProps.getLength()):
                        pdProp = pdProps.item(pdCount)
                        propName = getTagValue(pdProp, "Name")
                        propValue = getTagValue(pdProp, "Value")
                        modifyProcessDefProperty(jvmName, nodeName, propName, propValue)

            # Add/modify JVM settings
            jvmNode = instance.getElementsByTagName("JavaVirtualMachine").item(0)
            if(jvmNode != None):
                # Modify JVM classpath
                cpNode = jvmNode.getElementsByTagName("Classpath").item(0)
                if(cpNode != None):
                    classpath = getTagValue(jvmNode, "Classpath")
                    if(classpath != ""):
                        modifyClasspath(jvmName, nodeName, classpath, 0)

                # Toggle verbose GC
                #verbGCNode = jvmNode.getElementsByTagName("VerboseGarbageCollection").item(0)
                #if(verbGCNode != None):
                #    verboseGC = getTagValue(jvmNode, "VerboseGarbageCollection")
                #    toogleVerboseGC(jvmName, nodeName, verboseGC)

                # Modify JVM init heap size
                initHeapNode = jvmNode.getElementsByTagName("InitialHeapSize").item(0)
                if(initHeapNode != None):
                    minHeap = getTagValue(jvmNode, "InitialHeapSize")
                    modifyMinHeap(jvmName, nodeName, minHeap)

                # Modify JVM max heap size
                maxHeapNode = jvmNode.getElementsByTagName("MaximumHeapSize").item(0)
                if(maxHeapNode != None):
                    maxHeap = getTagValue(jvmNode, "MaximumHeapSize")
                    modifyMaxHeap(jvmName, nodeName, maxHeap)
                else:
                    print"WARNING: configJVM: MaximumHeapSize TAG not found in the XML property sheet"
                    print"WARNING: configJVM: Running JVMs without specifying an MaximumHeapSize is stupid"
                    print"WARNING: configJVM: Are you sure you know what you are doing?"

                # Modify JVM generic arguments
                gaNode = jvmNode.getElementsByTagName("GenericJVMArguments").item(0)
                if(gaNode != None):
                    genericArgs = getTagValue(jvmNode, "GenericJVMArguments")
                    if(genericArgs != ""):
                        setGenericJVMArgs(jvmName, nodeName, genericArgs)
		
                # Modify JVM custom properties
                jvmPropsNode = jvmNode.getElementsByTagName("CustomProperties").item(0)
                if(jvmPropsNode != None):
                    jvmProps = jvmPropsNode.getElementsByTagName("Property")
                    for jpCount in range(jvmProps.getLength()):
                        jvmProp = jvmProps.item(jpCount)
                        propName = getTagValue(jvmProp, "Name")
                        propValue = getTagValue(jvmProp, "Value")
                        modifyJVMProperty(jvmName, nodeName, propName, propValue)
            else:
                print"WARNING: configJVM: JavaVirtualMachine TAG not found in the XML property sheet"
                print"WARNING: configJVM: This is the TAG where you define the JVM heap size properties, etc."
                print"WARNING: configJVM: Are you sure you know what you are doing?"

            # Add/Modify message listener service settings
            msgListenerNode = instance.getElementsByTagName("MessageListenerService").item(0)
            if(msgListenerNode != None):
                listenerNode = msgListenerNode.getElementsByTagName("ListenerPorts").item(0)
                if(listenerNode != None):
                    portList = listenerNode.getElementsByTagName("Port")
                    for portCount in range(portList.getLength()):
                        portItem = portList.item(portCount)
                        portName = getTagValue(portItem, "Name")
                        #initState = getTagValue(portItem, "InitialState")
                        cfJNDI = getTagValue(portItem, "CFJNDI")
                        dJNDI = getTagValue(portItem, "DestinationJNDI")
                        maxSess = getTagValue(portItem, "MaxSessions")
                        maxRetry = getTagValue(portItem, "MaxRetries")
                        maxMsg = getTagValue(portItem, "MaxMessages")
                        createMsgListenerPort(jvmName, nodeName, portName, cfJNDI, dJNDI, maxSess, maxRetry, maxMsg)

            # Modify JVM monitoring policy
            monitorList = instance.getElementsByTagName("MonitoringPolicy").item(0)
            if(monitorList != None):
                startupAtmp = getTagValue(monitorList, "maximumStartupAttempts")
                pingInt = getTagValue(monitorList, "pingInterval")
                pingTime = getTagValue(monitorList, "pingTimeout")
                autoRstrt =  getTagValue(monitorList, "autoRestart")
                svrState = getTagValue(monitorList, "serverRestartState")
                monitorSettings(jvmName, nodeName, startupAtmp, pingInt, pingTime, autoRstrt, svrState)

            # Add/modify Custom Services
            cSvcNode = instance.getElementsByTagName("CustomServices").item(0)
            if(cSvcNode != None):
                cSvcList = cSvcNode.getElementsByTagName("CustomService")
                for svcCount in range(cSvcList.getLength()):
                    cSvc = cSvcList.item(svcCount)
                    sStartup = getTagValue(cSvc, "EnableStartup")
                    sClassname = getTagValue(cSvc, "Classname")
                    sDispName = getTagValue(cSvc, "DisplayName")
                    sDesc = getTagValue(cSvc, "Description")
                    sClasspath = getTagValue(cSvc, "Classpath")
                    cServiceId = customService(jvmName, nodeName, sDispName, sClassname, sClasspath, sStartup, sDesc)
                    sCustomPropsNode = cSvc.getElementsByTagName("CustomProperties").item(0)
                    if(sCustomPropsNode != None):
                        sCustomPropsList = sCustomPropsNode.getElementsByTagName("Property")
                        for sCPCount in range(sCustomPropsList.getLength()):
                            sCP = sCustomPropsList.item(sCPCount)
                            sPropName = getTagValue(sCP, "Name")
                            sPropValue = getTagValue(sCP, "Value")
                            modifyCustomServiceProperty(cServiceId, sPropName, sPropValue)                       

            # Modify JVM stdin/stdout logging policy
            logList = instance.getElementsByTagName("JVMLogs").item(0)
            if(logList != None):
                # Modify JVM SystemOut policy
                location = getTagValue(logList, "JVMLogsSystemOutFileLocation")
                format = getTagValue(logList, "JVMLogsSystemOutFileFormat")
                rollType = getTagValue(logList, "JVMLogsSystemOutRolloverType")
                noBkp = getTagValue(logList, "JVMLogsSystemOutNumberOfBackupFiles")
                rollSize = getTagValue(logList, "JVMLogsSystemOutRolloverSize")
                baseHr = getTagValue(logList, "JVMLogsSystemOutBaseHour")
                rollPrd = getTagValue(logList, "JVMLogsSystemOutRolloverPeriod")
                fmtW = getTagValue(logList, "JVMLogsSystemOutFormatWrites")
                supW = getTagValue(logList, "JVMLogsSystemOutsuppresWrites")
                supST = getTagValue(logList, "JVMLogsSystemOutsuppressStackTrace")
                type = "out"
                JVMLogSettings(jvmName, nodeName, type, location, format, rollType, noBkp, rollSize, baseHr, rollPrd, fmtW, supW, supST)

                # Modify JVM SystemError policy
                location = getTagValue(logList, "JVMLogsSystemErrorFileLocation")
                format = getTagValue(logList, "JVMLogsSystemErrorFileFormat")
                rollType = getTagValue(logList, "JVMLogsSystemErrorRolloverType")
                noBkp = getTagValue(logList, "JVMLogsSystemErrorNumberOfBackupFiles")
                rollSize = getTagValue(logList, "JVMLogsSystemErrorRolloverSize")
                baseHr = getTagValue(logList, "JVMLogsSystemErrorBaseHour")
                rollPrd = getTagValue(logList, "JVMLogsSystemErrorRolloverPeriod")
                fmtW = getTagValue(logList, "JVMLogsSystemErrorFormatWrites")
                supW = getTagValue(logList, "JVMLogsSystemErrorsuppresWrites")
                supST = getTagValue(logList, "JVMLogsSystemErrorsuppressStackTrace")
                type = "err"
                JVMLogSettings(jvmName, nodeName, type, location, format, rollType, noBkp, rollSize, baseHr, rollPrd, fmtW, supW, supST)

            # Now setup resources at jvm level
            configResources(jvmName, nodeName, instance)

            print "INFO: configJVM: Finished working on " + jvmName + " on node " + nodeName

    # Change the cluster core group
    if(nodeName.find("was") == -1):
        print "INFO: configJVM: Will not change core group setting for a non shared env"
        return
    if((jvmName != 'nodeagent') & (jvmName != 'dmgr')):
        nodeVersion = AdminTask.getNodeBaseProductVersion('[-nodeName ' + nodeName + ']')
        nodeShortVersion = int(nodeVersion[0]+nodeVersion[2])
        nodeId = AdminConfig.getid("/Node:" + nodeName)
        nodeHostName = AdminConfig.showAttribute(nodeId, 'hostName')
        if(nodeShortVersion == 70):
            #hostNumber = int(nodeHostName[9]+nodeHostName[10])
            # Changed to the following -- RShen 2011 09 14
            hostNumber = int(nodeHostName[nodeHostName.find('was')+3:nodeHostName.find('was')+5])
            if(haFlag.upper() == "TRUE"):
                if(((hostNumber >= 90) & (hostNumber <= 99)) | ((hostNumber >= 40) & (hostNumber <= 49))):
                    tCoreGroup = "CORE_HA_ON_V70"
                    print "ERROR: configJVM: coregroup service availability in the CORE network zone for SYS, INT, UAT & PROD has not been planed for yet."
                    print "ERROR: configJVM: Create a coregroup for the core zone, setup preferred co-ordinators and come back."
                    raise Exception, "Script raised exception, exiting now!!!"
                elif(((hostNumber >= 70) & (hostNumber <= 79)) | ((hostNumber >= 30) & (hostNumber <= 39))):
                    tCoreGroup = "SERVICE_HA_ON_V70"
                elif((hostNumber >= 80) & (hostNumber <= 89)):
                    tCoreGroup = "CORE_HA_ON_V70"
                else:
                    tCoreGroup = "DefaultCoreGroup"
            elif(haFlag.upper() == "FALSE"):
                if(((hostNumber >= 90) & (hostNumber <= 99)) | ((hostNumber >= 40) & (hostNumber <= 49))):
                    tCoreGroup = "CORE_HA_OFF_V70"
                elif(((hostNumber >= 70) & (hostNumber <= 79)) | ((hostNumber >= 30) & (hostNumber <= 39))):
                    tCoreGroup = "SERVICE_HA_OFF_V70"
                elif((hostNumber >= 80) & (hostNumber <= 89)):
                    tCoreGroup = "CORE_HA_OFF_V70"
                else:
                    tCoreGroup = "DefaultCoreGroup"
            else:
                print "INFO: configJVM: Bad HA-MGR task"
                raise Exception, "Script raised exception, you are doing something wrong!!!"
            changeClusterCoreGroup(clusterName, tCoreGroup)
        elif(nodeShortVersion == 85):
            if(haFlag.upper() == "TRUE"):
                tCoreGroup = "SERVICE_HA_ON_V85"
            elif(haFlag.upper() == "FALSE"):
                tCoreGroup = "SERVICE_HA_OFF_V85"
            else:
                print "INFO: configJVM: Bad HA-MGR task"
                raise Exception, "Script raised exception, you are doing something wrong!!!"
            changeClusterCoreGroup(clusterName, tCoreGroup)

    #print "DEBUG: END: configJVM"
    return

def configResources(serverScope, nodeScope, resNode):
    #print "DEBUG: START: configResources"

    # Setup JMS resources
    jmsAdapterList = resNode.getElementsByTagName("Provider")
    jmsAdapter(serverScope, nodeScope, jmsAdapterList)

    # Setup Resource Adapters, ex. IMS, CICS, SONIC
    radapterList = resNode.getElementsByTagName("Adapter")
    radapter(serverScope, nodeScope, radapterList)

    # Setup WebSphere variables
    varList = resNode.getElementsByTagName("Variable")
    variables(serverScope, nodeScope, varList)

    # Create DB2 provider, datasources
    db2Prov = resNode.getElementsByTagName("DB2Provider").item(0)
    if(db2Prov != None):
        dataSource(serverScope, nodeScope, db2Prov, "DB2")

    # Create SQL Server provider, datasources
    sqlProv = resNode.getElementsByTagName("SQLProvider").item(0)
    if(sqlProv != None):
        dataSource(serverScope, nodeScope, sqlProv, "SQL Server")

    # Commenting out this section; will use sqljdbc4.jar for all apps
    # assuming only WAS 7 builds forward 3/27/21012 - Dev D
    # Create SQL Server provider for WebSphere Version 7.x, datasources
    # kahcxs 4/22/09 - this sectino added for WebSphere 7.x support
    #sqlProv = resNode.getElementsByTagName("SQL7Provider").item(0)
    #if(sqlProv != None):
    #    dataSource(serverScope, nodeScope, sqlProv, "SQL Server Version 7")

    # Create Oracle provider, datasource
    oraProv = resNode.getElementsByTagName("OracleProvider").item(0)
    if(oraProv != None):
        dataSource(serverScope, nodeScope, oraProv, "Oracle")

    # Build the mail providers
    mailList = resNode.getElementsByTagName("MailSessions")
    mail(serverScope, nodeScope, mailList)

    # Build URL providers
    urlList = resNode.getElementsByTagName("URL")
    url(serverScope, nodeScope, urlList)

    # Setup NameSpace bindings
    nameSpaceList = resNode.getElementsByTagName("NameSpace")
    namespace(serverScope, nodeScope, nameSpaceList)

    # Setup SIB Resources
    sibNode = resNode.getElementsByTagName("SIBResource")
    buildSIB(serverScope, nodeScope, sibNode)

    #print "DEBUG: END: configResources"
    return

def dataSource(scopeS, scopeN, provNode, dbType):
    #print "DEBUG: START: dataSource"
    # Create the datasource provider
    provName = getTagValue(provNode, "ProviderName")
    provId = createDatabaseProvider(scopeS, scopeN, dbType, provName)
    dsList = provNode.getElementsByTagName("DataSource")
    dsCount = dsList.getLength()
    for i in range(dsCount):
        ds = dsList.item(i)
        # Create the datasource
        dsName = getTagValue(ds, "DataSourceName")
        dsJNDI = getTagValue(ds, "DataSourceJNDIName")
        dsCompAlias = getTagValue(ds, "ComponentManagedAuthAlias")
        dsStmtCache = getTagValue(ds, "StatementCacheSize")
        dsConnTest = getTagValue(ds, "PretestConnectionEnable")
        dsId = createDataSource(scopeS, scopeN, dbType, provId, dsName, dsJNDI, dsCompAlias, dsStmtCache, dsConnTest)
        if(dbType == "DB2"):
            modifyDSProperty(dsId, "databaseName", getTagValue(ds, "DataBaseName"))
            modifyDSProperty(dsId, "portNumber", getTagValue(ds, "PortNumber"))
            modifyDSProperty(dsId, "driverType", getTagValue(ds, "DataBaseDriverType"))
            modifyDSProperty(dsId, "serverName", getTagValue(ds, "DataBaseServerName"))
        if(dbType == "Oracle"):
            modifyDSProperty(dsId, "portNumber", getTagValue(ds, "portNumber"))
            modifyDSProperty(dsId, "URL", getTagValue(ds, "DataSourceURL"))
        if(dbType == "SQL Server"):
            modifyDSProperty(dsId, "databaseName", getTagValue(ds, "DataBaseName"))
            modifyDSProperty(dsId, "portNumber", getTagValue(ds, "PortNumber"))
            modifyDSProperty(dsId, "serverName", getTagValue(ds, "DataBaseServerName"))
        if(dbType == "SQL Server Version 7"):
            modifyDSProperty(dsId, "databaseName", getTagValue(ds, "DataBaseName"))
            modifyDSProperty(dsId, "portNumber", getTagValue(ds, "PortNumber"))
            modifyDSProperty(dsId, "serverName", getTagValue(ds, "DataBaseServerName"))
        # Modify the connection pool
        dsPTimeOut = getTagValue(ds, "ConnectionPoolTimeout")
        dsPMaxCon = getTagValue(ds, "ConnectionPoolMaxConnections")
        dsPMinCon = getTagValue(ds, "ConnectionPoolMinConnections")
        dsPReapTime = getTagValue(ds, "ConnectionPoolReapTime")
        dsPUnusedTime = getTagValue(ds, "ConnectionPoolUnusedTimeout")
        dsPAgedTime = getTagValue(ds, "ConnectionPoolagedTimeout")
        dsPPurge = getTagValue(ds, "ConnectionPoolPurgePolicy")
        modifyConnectionPool(dsId, dsPTimeOut, dsPMaxCon, dsPMinCon, dsPReapTime, dsPUnusedTime, dsPAgedTime, dsPPurge)
        # Modify the PRE-TEST SQL string
        modifyDSProperty(dsId, "preTestSQLString", getTagValue(ds, "PretestSQLString"))
        # Modify reqd. custom properties
        customProps = ds.getElementsByTagName("CustomProperties").item(0)
        if(customProps != None):
            propsList = customProps.getChildNodes()
            for j in range(propsList.getLength()):
                child = propsList.item(j)
                if(child.getNodeType() == 1):
                    modifyDSProperty(dsId, child.getNodeName(), child.firstChild.nodeValue.strip())
    #print "DEBUG: END: dataSource"
    return

def buildSIB(scopeS, scopeN, sibNode):
    #print "DEBUG: START: buildSIB"
    for i in range(sibNode.getLength()):
        sibItem = sibNode.item(i)
        busName = getTagValue(sibItem, "SIBusName")
        busId = createSIBus(busName)
        memberJNDI = getTagValue(sibItem, "SIBDsJndi")
        addSIBusMember(scopeS, scopeN, busName, memberJNDI)
        sibDestNodes = sibItem.getElementsByTagName("SIBDestination")
        for j in range(sibDestNodes.getLength()):
            sibDest = sibDestNodes.item(j)
            name = getTagValue(sibDest, "Name")
            type = getTagValue(sibDest, "Type")
            createSIBDestination(scopeS, scopeN, name, type, busName)
        sibActNodes = sibItem.getElementsByTagName("SIBActivationSpec")
        for l in range(sibActNodes.getLength()):
            sibAct = sibActNodes.item(l)
            name = getTagValue(sibAct, "Name")
            jndi = getTagValue(sibAct, "JNDIName")
            destType = getTagValue(sibAct, "DestinationType")
            destJndi = getTagValue(sibAct, "DestinationJNDI")
            createSIBJMSActivationSpec(scopeS, scopeN, name, jndi, destType, destJndi, busName)
        sibJMSQCFNodes = sibItem.getElementsByTagName("SIBJMSCF")
        for k in range(sibJMSQCFNodes.getLength()):
            sibJMSQCF = sibJMSQCFNodes.item(k)
            name = getTagValue(sibJMSQCF, "Name")
            jndi = getTagValue(sibJMSQCF, "JNDIName")
            xa = getTagValue(sibJMSQCF, "XA")
            type = getTagValue(sibJMSQCF, "Type")
            createSIBJMSConnetionFactory(scopeS, scopeN, name, jndi, xa, type, busName)
        sibJMSQNodes = sibItem.getElementsByTagName("SIBJMSQueue")
        for m in range(sibJMSQNodes.getLength()):
            sibJMSQ = sibJMSQNodes.item(m)
            name = getTagValue(sibJMSQ, "Name")
            jndi = getTagValue(sibJMSQ, "JNDIName")
            qname = getTagValue(sibJMSQ, "QName")
            createSIBJMSQueue(scopeS, scopeN, name, jndi, qname, busName)
        sibJMSTNodes = sibItem.getElementsByTagName("SIBJMSTopic")
        for n in range(sibJMSTNodes.getLength()):
            sibJMSTopic = sibJMSTNodes.item(n)
            name = getTagValue(sibJMSTopic, "Name")
            jndi = getTagValue(sibJMSTopic, "JNDIName")
            tname = getTagValue(sibJMSTopic, "TopicName")
            createSIBJMSTopic(scopeS,scopeN, name, jndi, tname, busName)
    #print "DEBUG: END: buildSIB"
    return

def jmsAdapter(scopeS, scopeN, jmsAdapterList):
    #print "DEBUG: START: jmsAdapter"
    for i in range(jmsAdapterList.getLength()):
        jmsItem = jmsAdapterList.item(i)
        # Build the adapter
        provName = getTagValue(jmsItem, "Name")
        classpath = getTagValue(jmsItem, "ClassPath")
        initCtx = getTagValue(jmsItem, "ExtInitCtxFactory")
        extProvURL = getTagValue(jmsItem, "ExtProviderURL")
        provId = createJmsProvider(scopeS, scopeN, provName, classpath, initCtx, extProvURL)
        # Add/Modify the custom properties for the adapter
        propSet = AdminConfig.showAttribute(provId, 'propertySet')
        if(propSet == None):
            propSet = AdminConfig.create('J2EEResourcePropertySet', provId, [])
        resProps = AdminConfig.showAttribute(propSet, 'resourceProperties')
        customProps = jmsItem.getElementsByTagName("CustomProperties").item(0)
        if(customProps != None):
            pdProps = customProps.getElementsByTagName("Property")
            for pdCount in range(pdProps.getLength()):
                pdProp = pdProps.item(pdCount)
                propName = getTagValue(pdProp, "Name")
                propValue = getTagValue(pdProp, "Value")
                addModifyJ2EEResourceProperty(propSet, resProps, propName, propValue)

        # Create the JMS connection factories now
        cfList = jmsItem.getElementsByTagName("ConnectionFactory")
        for n in range(cfList.getLength()):
            cfItem = cfList.item(n)
            # Build the CF
            cfName = getTagValue(cfItem, "Name")
            cfType = getTagValue(cfItem, "Type")
            cfJNDI = getTagValue(cfItem, "JNDI")
            cfExtJNDI = getTagValue(cfItem, "ExtJNDI")
	    #Added by Nik to include the Auth Alias as part of the COnnection Factory build.
	    #This was put in place so Sonic could use the Alias for authentication instaed of cstm props.
	    dsCmpMngAls = getTagValue(cfItem, "ComponentManagedAuthAlias")
	    #The following line has been added by Etien to allow for container-managed auth alias
	    dsCntMngAls = getTagValue(cfItem, "ContainerManagedAuthAlias")
            cfId = createJmsConnectionFactory(scopeS, scopeN, provId, cfName, cfJNDI, cfExtJNDI, cfType, dsCmpMngAls, dsCntMngAls)
	    #End of Nik's Changes
        # Create the JMS destinations
        destList = jmsItem.getElementsByTagName("JMSDestination")
        for m in range(destList.getLength()):
            destItem = destList.item(m)
            # Build the destination
            dName = getTagValue(destItem, "Name")
            dType = getTagValue(destItem, "Type")
            dJNDI = getTagValue(destItem, "JNDI")
            dExtJNDI = getTagValue(destItem, "ExtJNDI")
            destId = createJmsDestination(scopeS, scopeN, provId, dName, dJNDI, dExtJNDI, dType)
            # Add/Modify the customer properties
            propSet = AdminConfig.showAttribute(destId, 'propertySet')
            if(propSet == None):
                propSet = AdminConfig.create('J2EEResourcePropertySet', destId, [])
            resProps = AdminConfig.showAttribute(propSet, 'resourceProperties')
            customProps = destItem.getElementsByTagName("CustomProperties").item(0)
            if(customProps != None):
                pdProps = customProps.getElementsByTagName("Property")
                for pdCount in range(pdProps.getLength()):
                    pdProp = pdProps.item(pdCount)
                    propName = getTagValue(pdProp, "Name")
                    propValue = getTagValue(pdProp, "Value")
                    addModifyJ2EEResourceProperty(propSet, resProps, propName, propValue)
            
    #print "DEBUG: END: jmsAdapter"
    return

def radapter(scopeS, scopeN, radapterList):
    #print "DEBUG: START: radapter"
    for i in range(radapterList.getLength()):
        radapterItem = radapterList.item(i)
        # Build the resource adapter
        provName = getTagValue(radapterItem, "ProviderName")
        rarPath = getTagValue(radapterItem, "RARLocation")
        copyFromAdapter = getTagValue(radapterItem, "CopyFromAdapter")
        copyFromNode = getTagValue(radapterItem, "CopyFromNode")
        deepCopy = getTagValue(radapterItem, "DeepCopy")
        if(rarPath == ""):
            if((copyFromAdapter == "") & (copyFromNode == "") & (deepCopy == "")):
                print "Exception: radapter: You must either build/copy a J2C Resource Adapter"
                raise Exception, "Script raised exception, you are doing something wrong!!!"
            elif((copyFromAdapter != "") & (copyFromNode != "") & (deepCopy != "")):
                adapterId = copyJCA(scopeS, scopeN, provName, copyFromAdapter, copyFromNode, deepCopy)
            else:
                print "Exception: radapter: You must specify all three of CopyFromAdapter, CopyFromNode, DeepCopy"
                raise Exception, "Script raised exception, you are doing something wrong!!!"
        else:
            if((copyFromAdapter == "") & (copyFromNode == "") & (deepCopy == "")):
                adapterId = installJCA(scopeN, provName, rarPath)
            elif((copyFromAdapter != "") & (copyFromNode != "") & (deepCopy != "")):
                print "Exception: radapter: You cannot specify CopyFromAdapter, CopyFromNode, or DeepCopy with a RARPath"
                raise Exception, "Script raised exception, you are doing something wrong!!!"
            else:
                print "Exception: radapter: You cannot specify CopyFromAdapter, CopyFromNode, or DeepCopy with a RARPath"
                raise Exception, "Script raised exception, you are doing something wrong!!!"

        # Build J2C Activation Specifications
        j2cASList = radapterItem.getElementsByTagName("J2CActivationSpec")
        for n in range(j2cASList.getLength()):
            j2cASItem = j2cASList.item(n)
            # Build the activation spec
            asName = getTagValue(j2cASItem, "Name")
            jndi = getTagValue(j2cASItem, "JNDIName")
            interface = getTagValue(j2cASItem, "Interface")
            authAlias = getTagValue(j2cASItem, "ComponentManagedAuthAlias")
            j2cASId = createActivationSpec(adapterId, asName, jndi, interface, authAlias)
            # Modify required custom properties
            customProps = j2cASItem.getElementsByTagName("CustomProperties").item(0)
            propsList = customProps.getChildNodes()
            for m in range(propsList.getLength()):
                child = propsList.item(m)
                if(child.getNodeType() == 1):
                    modifyRAResourceProperty(j2cASId, child.getNodeName(), child.firstChild.nodeValue.strip())

        # Now build the required J2C Connection Factories
        j2cfList = radapterItem.getElementsByTagName("J2CConnFactory")
        for k in range(j2cfList.getLength()):
            j2cfItem = j2cfList.item(k)
            # Build the J2C connection factory
            cfName = getTagValue(j2cfItem, "Name")
            jndi = getTagValue(j2cfItem, "JNDIName")
            interface = getTagValue(j2cfItem, "Interface")
            authAlias = getTagValue(j2cfItem, "ComponentManagedAuthAlias")
            j2cfId = createJ2CConnFactory(adapterId, cfName, jndi, interface, authAlias)
            # Modify the connection pool
            dsPTimeOut = getTagValue(j2cfItem, "ConnectionPoolTimeout")
            dsPMaxCon = getTagValue(j2cfItem, "ConnectionPoolMaxConnections")
            dsPMinCon = getTagValue(j2cfItem, "ConnectionPoolMinConnections")
            dsPReapTime = getTagValue(j2cfItem, "ConnectionPoolReapTime")
            dsPUnusedTime = getTagValue(j2cfItem, "ConnectionPoolUnusedTimeout")
            dsPAgedTime = getTagValue(j2cfItem, "ConnectionPoolagedTimeout")
            dsPPurge = getTagValue(j2cfItem, "ConnectionPoolPurgePolicy")
            modifyConnectionPool(j2cfId, dsPTimeOut, dsPMaxCon, dsPMinCon, dsPReapTime, dsPUnusedTime, dsPAgedTime, dsPPurge)
            # Modify required custom properties
            customProps = j2cfItem.getElementsByTagName("CustomProperties").item(0)
            propsList = customProps.getChildNodes()
            for j in range(propsList.getLength()):
                child = propsList.item(j)
                if(child.getNodeType() == 1):
                    modifyRAProperty(j2cfId, child.getNodeName(), child.firstChild.nodeValue.strip())

    #print "DEBUG: END: radapter"
    return

def variables(scopeS, scopeN, varList):
    #print "DEBUG: START: variables"
    for y in range(varList.getLength()):
        varName = getTagValue(varList.item(y), "VariableName")
        varValue = getTagValue(varList.item(y), "VariableValue")
        setupVariable(scopeS, scopeN, varName, varValue)
    #print "DEBUG: END: variables"
    return

def mail(scopeS, scopeN, mailList):
    #print "DEBUG: START: mail"
    for i in range(mailList.getLength()):
        mail = mailList.item(i)
        mName = getTagValue(mail, "MailSessionName")
        mJNDI = getTagValue(mail, "MailSessionJNDIName")
        mHost = getTagValue(mail, "MailTransportHost")
        mUID  = getTagValue(mail, "MailTransportUserID")
        mPWD  = getTagValue(mail, "MailTransportPassword")
        mFROM = getTagValue(mail, "MailFromAddress")
        mailSetup(scopeS, scopeN, mName, mJNDI, mHost, mUID, mPWD, mFROM)
    #print "DEBUG: END: mail"
    return

def url(scopeS, scopeN, urlList):
    #print "DEBUG: START: url"
    for i in range(urlList.getLength()):
        url = urlList.item(i)
        uName = getTagValue(url, "URLName")
        uJNDI = getTagValue(url, "URLJNDIName")
        uSpec = getTagValue(url, "URLSpec")
        uDesc = getTagValue(url, "URLDesc")
        setupURL(scopeS, scopeN, uName, uJNDI, uSpec, uDesc)
    #print "DEBUG: END: url"
    return

def namespace(scopeS, scopeN, nameSpaceList):
    #print "DEBUG: START: namespace"
    for x in range(nameSpaceList.getLength()):
        nsType = getTagValue(nameSpaceList.item(x), "NameSpaceType")
        nsIdent = getTagValue(nameSpaceList.item(x), "NameSpaceIdentifier")
        nsName = getTagValue(nameSpaceList.item(x), "NameSpaceName")
        nsString = getTagValue(nameSpaceList.item(x), "NameSpaceStringValue")
        if(nsType == "String"):
            setupNameSpaceString(scopeS, scopeN, nsIdent, nsName, nsString)
        else:
            print "Exception: namespace: NameSpace type String only permitted"
            raise Exception, "Script raised exception, you are doing something wrong!!!"
    #print "DEBUG: END: namespace"
    return