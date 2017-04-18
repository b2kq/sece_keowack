#  To use:   functions called by mainV2.py
#  State:    work in progress, major revision first version
#  Purpose:  replacing buildEnv.py, attempt not to change prior functions
#    There is probably an existing working configuration, but may not be
#    A new build or deploy is being sumitted, this configuration is the target
#    Only the differences will be applied, we are trying to minimize work the 
#    deployment manager needs to do.
#  Assumptions:
#    x)  all dependancies already defined

codeVersion = '2.08'
printDebugLine(' '.join(['buildEnvV2',codeVersion]))
abend = 0 # flag to trigger abnormal end after all relavent information has been gathered
#  Programming notes:
#    x)  continue debug functions from mainV2.py
#    x)  omega is sumbited XML
#    x)  alpha is configuration as queried from existing configuration
#    x)  delta changes to make alpha into omega

import com.ibm.websphere.crypto.PasswordUtil as crypto 

buildEnvError = 0     ## to signal the build will not work
buildNotes = {}
for xmlVersion in ['alpha', 'delta', 'omega']: 
    buildNotes [xmlVersion] = {}

def getTagValue(node, tag):
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Original getTagValue function')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    value = ""
    if node != None:
        tagNode = node.getElementsByTagName(tag)
        if tagNode.length != 0:
            if tagNode.item(0).hasChildNodes(): 
                value = tagNode.item(0).firstChild.nodeValue
    printDebugLine('end')
    return value

def buildTask(alphaDOM, omegaDOM):
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Function buildTask(alphaDOM, omegaDOM)')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    cellId    = AdminConfig.getid(''.join(['/Cell:',AdminControl.getCell(),'/']))
    clusterId = '' # AdminConfig.getid('/ServerCluster:' + clusterName + '/')
    nodeId    = '' # AdminConfig.getid('/Node:'          + nodeName    + '/')
    serverId  = '' # AdminConfig.getid('/Server:'        + serverName  + '/')
    # Program flow:
    #    --- populate alpha and omega buildNotes walking through their XML DOMs
    #    --- derive delta = omega - alpha, ie alpha + delta = omega
    #    --- for delta:
    #    +++ --- create/change cell J2CAuthentication
    #    +++ --- create/change cell resource
    #    +++ --- create/change node
    #        +++ --- create/change node resource
    #    +++ --- create/change cluster 
    #        +++ --- create/change server
    #            +++ --- create/change server resources
    #            +++ --- create/change jvm 
    #                +++ --- add to cluster
    #                +++ --- create/change HA Manager
    #                +++ --- create/change (TCP) End Points
    #                +++ --- create/change Transaction service settings
    #                +++ --- create/change ORB (Object Request Broker)
    #                +++ --- Web Container settings
    #                    +++ --- create/change session settings
    #                    +++ --- create/change web container custom properties
    #                +++ --- create Process Definition
    #                +++ --- JVM settings
    #                    +++ --- create/change classpath
    #                    +++ --- set heap and garbage collection parameters
    #                    +++ --- create/change generic arguments
    #                    +++ --- create/change message listener service
    #                    +++ --- set monitoring policy
    #                    +++ --- create/change jvm custom services
    #                    +++ --- logging
    #                        +++ --- change stdout, SystemOut
    #                        +++ --- change stderr, SystemError
    #                    +++ --- create/change jvm resources
    #            +++ --- create/change cluster resources
    #    +++ --- create/change core group  

    printInfoLine(' '.join(['function buildTask(alphaDOM, omegaDOM) from buildEnvV2.py',codeVersion])) 
    # Architecture supports multiple WAS and even multiple EnterpriseApplication elements in the XML
    # This architecture's broad support could easily overwhelm the memory resources to execute this task 
    # 'alpha' is current, 'omega' is target, 'delta' are the differences
    # need the following to support privious block that supports original calls for WebServer
    rootElement = omegaDOM
    if alphaDOM == None :
        buildNotes['alpha']['DOM'] = None
    else:
        alphaDOM = alphaDOM.getElementsByTagName('WAS').item(0)
    if omegaDOM == None : return
    omegaDOM = omegaDOM.getElementsByTagName('WAS').item(0)
    #for xmlVersion in ['alpha', 'omega']:
    for xmlVersion in ['omega']:
        buildNotes[xmlVersion]['DOM'] = parseDOM(eval(xmlVersion + 'DOM'))
        buildNotes[xmlVersion]['DOM'] = buildNotes[xmlVersion]['DOM'][0]['EnterpriseApplication'][0]['WAS'][0]
        if buildNotes[xmlVersion]['DOM'] != None:
            for cluster in range(len(buildNotes[xmlVersion]['DOM']['Cluster'])):
                serverDOM = buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['Server'][0]
                buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['Server'] = []
                for node in range(len(buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['Node'][0]['NodeName'])):
                    # guessing cluster server name...
                    serverName = '_'.join([buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['ClusterName'][0],str(node + 1),'1'])
                    nodeName = buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['Node'][0]['NodeName'][node]
                    buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['Server'].append({'NodeName':[nodeName]})
                    buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['Server'][node]['ServerName'] = [serverName]
                    for key in serverDOM.keys():
                        buildNotes[xmlVersion]['DOM']['Cluster'][cluster]['Server'][node][key] = serverDOM[key]
    if buildNotes['omega']['DOM'] == None:
        printSevereLine('buildTask: aborting, invalid passed XML DOM')
        printDebugLine('end')
        return    # buildTask aborting

    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Find application and EAR file name')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    for xmlVersion in ['alpha', 'omega']:
        if  buildNotes[xmlVersion]['DOM'] == None:  continue
        buildNotes[xmlVersion]['appName'] = buildNotes[xmlVersion]['DOM']['ear-info'][0]['app-name'][0]
        buildNotes[xmlVersion]['earName'] = buildNotes[xmlVersion]['DOM']['ear-info'][0]['ear-name'][0]
        printDebugLine(' '.join([xmlVersion,'application name is', buildNotes[xmlVersion]['appName']]))
        printDebugLine(' '.join([xmlVersion,'.ear   file name is', buildNotes[xmlVersion]['earName']]))
    printDebugLine('end')

    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Parse out modules')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    for xmlVersion in ['alpha', 'omega']:
        if  buildNotes[xmlVersion]['DOM'] == None: continue
        for mod in buildNotes[xmlVersion]['DOM']['mod-info'][0].keys():
            # mod is war, ear, or jar
            buildNotes[xmlVersion][mod] = {}
            for index in buildNotes[xmlVersion]['DOM']['mod-info'][0][mod]:
                # 'web' used below is to support deployment/install with old code
                if  mod == 'web':
                    fileName = index['war-file-name'][0]
                else:
                    fileName = index[''.join([mod,'-file-name'])][0]
                displayName = index['display-name'][0]
                buildNotes[xmlVersion][mod][fileName] = displayName
                printDebugLine(' '.join([xmlVersion,mod,'module',displayName,',',fileName]))
                # 'web' used below is to support deployment/install with old code
                if mod == 'war' or mod =='web':
                    buildNotes[xmlVersion][mod][fileName] = [displayName, index['virtual-host'][0]]
                    printDebugLine(''.join(['  and virtual host ',buildNotes[xmlVersion][mod][fileName][1]]))
                    if index.has_key('server-name'):
                        buildNotes[xmlVersion][mod][fileName].append(index['server-name'][0])
                        printDebugLine(''.join(['  and has server name ',buildNotes[xmlVersion][mod][fileName][2]]))
    printDebugLine('end')

    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Parse out security')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    for xmlVersion in ['alpha', 'omega']:
        if  buildNotes[xmlVersion]['DOM'] == None: continue
        # when the cluster has no J2C entries, parser returns white space, so skip
        if  type(buildNotes[xmlVersion]['DOM']['Security'][0]['J2CAuthData'][0]) == type('\n\t\t\t'):  continue
        buildNotes[xmlVersion]['J2C'] = {}
        for elements in buildNotes[xmlVersion]['DOM']['Security'][0]['J2CAuthData'][0]['J2C']:
            if  elements['Password'][0][:4] == '{xor}':
                buildNotes[xmlVersion]['J2C'][elements['Alias'][0]] = [elements['Username'][0], crypto.decode(elements['Password'][0])]
            else:
                buildNotes[xmlVersion]['J2C'][elements['Alias'][0]] = [elements['Username'][0], elements['Password'][0]]
        if debug: 
            for alias in buildNotes[xmlVersion]['J2C'].keys():
                printDebugLine(''.join([xmlVersion,' J2C ', alias, ': ', 
                                        buildNotes[xmlVersion]['J2C'][alias][0], ', ***', 
                                        crypto.encode(buildNotes[xmlVersion]['J2C'][alias][0])[5:9], '***']))
    printDebugLine('end')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Parse out clusters')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    for xmlVersion in ['alpha', 'omega']:
        if  buildNotes[xmlVersion]['DOM'] == None: continue
        buildNotes[xmlVersion]['Cluster'] = {}
        processStage.append(' '.join(['Parse',xmlVersion,'version']))
        printDebugLine('start')
        for clusterIndex in range(len(buildNotes[xmlVersion]['DOM']['Cluster'])):
            cluster = buildNotes[xmlVersion]['DOM']['Cluster'][clusterIndex] 
            clusterName = cluster['ClusterName'][0]
            buildNotes[xmlVersion]['Cluster'][clusterName] = {}
            buildNotes[xmlVersion]['Cluster'][clusterName]['Server'] = {}
            processStage.append(' '.join([xmlVersion,'cluster', clusterName]))
            printDebugLine('start')
            for serverIndex in range(len(cluster['Server'])):
                server = cluster['Server'][serverIndex]['ServerName'][0]
                node   = cluster['Server'][serverIndex]['NodeName'][0]
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server] = {}
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['NodeName'] = node
                processStage.append(' '.join(['server',server,'node',node]))
                printDebugLine('start')
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['HAManager'] = cluster['Server'][serverIndex]['HAManager'][0]['Enabled'][0]
                printDebugLine(''.join(['HAManager Enabled = ',buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['HAManager']]))
                endPoints = cluster['Server'][serverIndex]['TCPEndPoints']
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TCPEndPoint'] = {}
                for endPoint in range(len(endPoints)):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TCPEndPoint']['Name'] = endPoints[endPoint]['PortItem'][0]['PortName'][0]
                    buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TCPEndPoint']['Host'] = endPoints[endPoint]['PortItem'][0]['Host'][0]
                    buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TCPEndPoint']['Port'] = endPoints[endPoint]['PortItem'][0]['Port'][0]
                    printDebugLine(''.join(['TCP end point name:host:port = ',
                        buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TCPEndPoint']['Name'], ':',
                        buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TCPEndPoint']['Host'], ':',
                        buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TCPEndPoint']['Port']]))
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer'] = {}
                webContainer = cluster['Server'][serverIndex]['WebContainer']
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['ServletCaching'] = webContainer[0]['ServletCaching'][0]
                printDebugLine(' '.join(['WebContainer with ServletCaching set to',
                                        buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['ServletCaching']]))
                sessions = webContainer[0]['SessionManagement']
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['SessionManagement'] = {}
                for sessionIndex in range(len(sessions)):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['SessionManagement']['CookieName']             = sessions[sessionIndex]['CookieName'][0]
                    buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['SessionManagement']['SessionTimeout']         = sessions[sessionIndex]['SessionTimeout'][0]
                    buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['SessionManagement']['DistributedSessionType'] = sessions[sessionIndex]['DistributedSessionType'][0]
                    printDebugLine('SessionManagement: CookieName, SessionTmeout, DistributedSessionType') 
                    printDebugLine(''.join(['  ',buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['SessionManagement']['CookieName'],", ",
                        buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['SessionManagement']['SessionTimeout'], ", ", 
                        buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['WebContainer']['SessionManagement']['DistributedSessionType']]))
                transactionService = cluster['Server'][serverIndex]['TransactionService'][0]
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TransactionService'] = {}
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TransactionService']['TotalTranLifetimeTimeout']            = transactionService['TotalTranLifetimeTimeout'][0]
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TransactionService']['PropogatedOrBMTTransLifetimeTimeout'] = transactionService['PropogatedOrBMTTransLifetimeTimeout'][0]
                printDebugLine('TransactionService:') 
                printDebugLine(''.join(['  TotalTranLifetimeTimeout .............. ',
                                       buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TransactionService']['TotalTranLifetimeTimeout']])) 
                printDebugLine(''.join(['  PropogatedOrBMTTransLifetimeTimeout ... ',
                                       buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['TransactionService']['PropogatedOrBMTTransLifetimeTimeout']]))
                jvm = cluster['Server'][serverIndex]['JavaVirtualMachine'][0]
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm'] = {}
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap'] = {}
                #buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap']['vgc'] = jvm['verboseModeGarbageCollection'][0]
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap']['vgc'] = 'false'
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap']['min'] = jvm['initialHeapSize'][0]
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap']['max'] = jvm['maximumHeapSize'][0]
                printDebugLine(''.join(['JVM heap: verbose = ',
                                       buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap']['vgc'],
                                       ', initial/maximum: ',
                                       buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap']['min'],
                                       "/", 
                                       buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['heap']['max']]))
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['args'] = jvm['genericJvmArguments']
                if debug: 
                    printDebugLine('JVM generic arguments:')
                    for jvmArg in buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['jvm']['args']:
                        printDebugLine(''.join(['  ',jvmArg]))
                customServices = cluster['Server'][serverIndex]['customServices'][0]
                buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['CustomServices'] = [{}]
                propertyIndex = 0
                for property in customServices['Property']:
                    #buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['CustomServices'].append([])
                    #buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['CustomServices'][propertyIndex] = {}
                    for element in property.keys():
                        #buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['CustomServices'][propertyIndex].append([element, property[element][0]])
                        buildNotes[xmlVersion]['Cluster'][clusterName]['Server'][server]['CustomServices'][propertyIndex][element] = property[element][0] 
                        printDebugLine(''.join(['  ',element, ': \t', property[element][0]]))
                    propertyIndex = propertyIndex + 1
                printDebugLine('end') # end cluster server loop
                buildNotes[xmlVersion]['Cluster'][clusterName]['JDBC'] = {}
                if  cluster.has_key('JDBC'):
                    for jdbc in cluster['JDBC']:
                        printDebugLine('JDBC providers:')
                        for provider in jdbc.keys():
                            buildNotes[xmlVersion]['Cluster'][clusterName]['JDBC'][provider] = []
                            for jdbcProvider in jdbc[provider]:
                                collection = []
                                for element in jdbcProvider.keys():
                                    collection.append([element, jdbcProvider[element]])
                                    if debug:
                                        if element == 'name': printDebugLine('  ' + jdbcProvider[element][0])
                                        if element == 'ProviderName': printDebugLine('  ' + jdbcProvider[element][0])
                                buildNotes[xmlVersion]['Cluster'][clusterName]['JDBC'][provider].append(collection)
                if  cluster.has_key('ResourceAdapters'):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['ResourceAdapters'] = cluster['ResourceAdapters'][0]
                    printDebugLine('Resource adapters:')
                    for adapter in buildNotes[xmlVersion]['Cluster'][clusterName]['ResourceAdapters']['Adapter']:
                        printDebugLine(''.join(['  ',adapter['ProviderName'][0], ': ', adapter['J2CConnFactory'][0]['Name'][0]]))
                if  cluster.has_key('MailResources'):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['MailResources'] = cluster['MailResources'][0]
                    printDebugLine('Mail resources:')
                    for session in buildNotes[xmlVersion]['Cluster'][clusterName]['MailResources']['MailSessions']:
                        printDebugLine(''.join(['  ',session['MailSessionName'][0]]))
                if  cluster.has_key('URLResources'):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['URLResources'] = cluster['URLResources'][0]
                    printDebugLine('URL resources:')
                    for url in buildNotes[xmlVersion]['Cluster'][clusterName]['URLResources']['URL']:
                        printDebugLine(''.join(['  ',url['URLName'][0]]))
                if  cluster.has_key('JMS'):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['JMS'] = cluster['JMS'][0]
                    printDebugLine('JMS:')
                    for provider in buildNotes[xmlVersion]['Cluster'][clusterName]['JMS']['Provider']:
                        printDebugLine(''.join(['  ',provider['Name'][0]]))
                if  cluster.has_key('NameSpaceBindings'):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['NameSpaceBindings'] = cluster['NameSpaceBindings'][0]
                    printDebugLine('Name space bindings:')
                    for space in buildNotes[xmlVersion]['Cluster'][clusterName]['NameSpaceBindings']['NameSpace']:
                        printDebugLine(''.join(['  ',space['NameSpaceIdentifier'][0]]))
                if  cluster.has_key('SharedLibraries'):
                    buildNotes[xmlVersion]['Cluster'][clusterName]['SharedLibraries'] = cluster['SharedLibraries'][0]
                    buildNotes[xmlVersion]['Cluster'][clusterName]['SharedLibraries'] = cluster['SharedLibraries']
                    for library in buildNotes[xmlVersion]['Cluster'][clusterName]['SharedLibraries']:
                        printDebugLine(''.join(['  ',library['Library'][0]['name'][0]]))
            printDebugLine('end') # end cluster loop
        printDebugLine('end') # all clustes done
    printDebugLine('end')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
                        
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Compose delta, changes to get to omega from alpha')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    buildNotes['delta'] = computeDelta(buildNotes)
    printDebugLine('end')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

    printInfoLine(' ')
    printInfoLine('#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#')
    printInfoLine('#== Configuration profiles read, now to create and modify ... ==#')
    printInfoLine('#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#')
    printInfoLine(' ')

    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Creation of J2C security credentials')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    printInfoLine('security takes a long time ...')
    nodeName = AdminControl.getNode()
    # for speed, set up dictionary, and assume we do not have the form nodeName/alias
    if  buildNotes['delta'].has_key('J2C') :
        j2cEntries = {}
        j2cCellId  = None # save time from rare call to AdminConfig.getid('/Cell:' + cellName + '/Security:/')
        for j2cEntry in AdminConfig.list('JAASAuthData').split():
            j2cEntries[AdminConfig.showAttribute(j2cEntry, 'alias')] = j2cEntry 
        for j2cAlias in buildNotes['delta']['J2C'].keys():
            j2cUser   = buildNotes['delta']['J2C'][j2cAlias][0]
            j2cPass   = buildNotes['delta']['J2C'][j2cAlias][1]
            j2cDesc   = ''  # not populating this at this time
            # the following obscures the password
            printDebugLine(''.join(['  J2C: ',j2cAlias,', ',j2cUser,', *',j2cPass[:2],'*',j2cPass[-2:],'*']))
            # look for existing entry
            if j2cEntries.has_key(j2cAlias):
                printInfoLine(''.join(['managed authentication entry, ',j2cAlias,', already exists.'])) 
                j2cAttributes = [['password', j2cPass]]  
                # when j2cUser is coded, we assume it is different
                if  j2cUser != None : j2cAttributes.append(['userId', j2cUser])
                # as noted above, we are not doing descriptions
                #if  j2cDesc != None : j2cAttributes.append(['description', j2cDesc])
                AdminConfig.modify(j2cEntry, j2cAttributes)
                AdminConfig.modify(j2cEntries[j2cAlias], j2cAttributes)
                printInfoLine(''.join(['  modified managed authentication entry ',j2cAlias, '.']))
            else:
                # create when managed authentication entry is not found
                if j2cCellId == None : j2cCellId = AdminConfig.getid(''.join(['/Cell:',cellName,'/Security:/']))
                j2cEntries[j2cAlias] = AdminConfig.create('JAASAuthData', j2cCellId,
                    [['alias', j2cAlias], ['userId', j2cUser], ['password', j2cPass], ['description', j2cDesc]])
                printInfoLine(''.join(['  created managed authentication entry ',j2cAlias, '.']))
    printInfoLine('Cell security changes completed.')
    printDebugLine('end')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Creation of cell resources')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    printDebugLine('Poperty sheet generator, WASquery.py does not provide')
    printDebugLine('  ... cell resources information, it must be put edited manually')
    printDebugLine('end')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    # summary of what follows...
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    # loop through clusters which loop through servers which loop through nodes
    # configure nodes
        # configure node resources
    # configue clusters
        # configure cluster resources
                # configure JDBC  
                # configure adapter
                # configure mail
                # configure url
                # configure jms
                # configure name space binding
                # configure shared libraries
        # configure servers
            # configure server resources
                # cutting this out, trying to make all resources at cluster level
            # configure jvm
                # add to cluster
                # configure HA Manager
                # configure (TCP) End Points
                # configure Transaction service settings
                # ignore ORB (Object Request Broker) <-- WAS now handles this
                # configure Web Container settings
                    # configure session settings
                    # configure custom properties
                # configure Process Definition
                # configure JVM settings
                    # configure classpath
                    # configure heap and garbage collection parameters
                    # configure message listener service
                    # configure monitoring policy
                    # configure logging
                        # configure stdout, SystemOut
                        # configure stderr, SystemError
                # configure custom services
    # configure core group
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
               
    # configure nodes
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Configure nodes')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    abend = 0
    for clusterName in buildNotes['delta']['Cluster'].keys():
        clusterId = AdminConfig.getid('/ServerCluster:' + clusterName + '/')
        for serverName in buildNotes['delta']['Cluster'][clusterName]['Server'].keys():
            nodeName = buildNotes['delta']['Cluster'][clusterName]['Server'][serverName]['NodeName']
            nodeId   = AdminConfig.getid(''.join(['/Node:',nodeName,'/']))
            if  nodeId == '':
                printSevereLine(' '.join(['Node name',nodeName,
                                          'not found, beyond this script\'s scope to create cell nodes.']))
                abend = 1
            else:
                printInfoLine(' '.join(['node',nodeName,'found.']))
    if abend: 
        raise Exception, 'Node name(s) not found, script aborting.'
        return
    printDebugLine('Requested nodes found, ready to continue.')
    printDebugLine('end')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

    # configue clusters
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Configure each cluster')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    for clusterName in buildNotes['delta']['Cluster'].keys():
        CLUSTERED = 'TRUE'
        clusterId = AdminConfig.getid(''.join(['/ServerCluster:',clusterName,'/']))
        # Cluster-->Server-->WebContainer-->SessionManagement-->DistributedSessionType != 'DATA_REPLICATION',
        # for now, -replicationDomain will always be false
        # Create cluster as needed
        if  clusterId == '':
            clusterId = AdminTask.createCluster(''.join(['[-clusterConfig [[',clusterName,
                                                         ' true "" ""]] -replicationDomain [[false]]]']))
            clusterState = 'created'
        else:
            clusterState = 'existing'
        printDebugLine(' '.join([clusterState,'cluster',clusterName,'...',clusterId[clusterId.rfind('#')+1:-1]]))

        # configure JDBC providers
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Creation (Cluster) JDBC providers')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        #Original method just isnt going to work reliably, I have no way of deriving the 
        #templates that create the JDBC provider and data sources can use any provider
        #IBM utilities have AdminJDBC.py which creates both provider and data source but 
        #it looks to use user provided template names
        #We could use only use the description or the name to find a template name, 
        #but the names have to match exactly to use it
        #jdbcProviderList = AdminConfig.list('JDBCProvider', clusterId).split('\r\n')
        #for jdbcIndex in range(len(buildNotes['delta']['Cluster'][clusterName]['JDBC']['JDBCProvider'])):
        #    jdbc = {}
        #    jdbc['classpath'] = []
        #    for element in buildNotes['delta']['Cluster'][clusterName]['JDBC']['JDBCProvider'][jdbcIndex]:
        #        if element[0] == 'classpath':
        #            for elementSubIndex in range(len(element[1])):
        #                if elementSubIndex == 0 : jdbc['classpath'] = element[1][0]
        #                else: jdbc['classpath'] = jdbc['classpath'] + ';' + element[1][elementSubIndex]
        #        else:
        #            jdbc[element[0]] = element[1][0]
        #    providerId = ''
        #    for  listItem in jdbcProviderList:
        #        if  AdminConfig.showAttribute(listItem, 'name') == jdbc['name']: 
        #            providerId = listItem
        #            break
        #    if  providerId == '':
        #        printDebugLine('JDBC provider ' + jdbc['name'] + ' not found, looking for template ' + jdbc['providerType'] + ' ... ')
        #        jdbcTemplate = ''
        #        attributes = [['name', jdbc['name']], ['classpath', jdbc['classpath']]]
        #        # only looking for templates .... and only looking for non XA templates
        #        for  template in AdminConfig.list('JDBCProvider', ' Only(templates/system').split('\r\n'):
        #            if AdminConfig.showAttribute(template, 'name') == (jdbc['providerType'] + ' Only'):
        #                providerId = AdminConfig.createUsingTemplate('JDBCProvider', clusterId, attributes, template)
        #        if  providerId == '':  
        #            raise Exception, 'Unable to create missing JDBC provider.'
        #            continue
        #    printDebugLine('JDBC provider ' + jdbc['name'])
        
        # This script is very limited, it works with the following assumptions
        #    1) All clusters (even if they dont use them) will have a basic set of providers.
        #       Additions or customization of this script to accomodate exceptions are not currently expected.
        #       DB2_JDBC_PROVIDER, DB2 Universal JDBC Driver Provider Only, named 
        #       ORACLE_JDBC_PROVIDER, Oracle JDBC Driver Provider Only
        #       SQL_JDBC_PROVIDER, Microsoft SQL Server JDBC Driver Provider
        #       SQL7_JDBC_PROVIDER, MicroSoft SQL Server v7 JDBC Driver Provider aka cp=${MICROSOFT_JDBC_DRIVER_PATH}/sqljdbc4.jar
        #    2) Only non XA providers are built
        #    3) WAS has cell or node scope environmental variables defined:
        #       ${DB2UNIVERSAL_JDBC_DRIVER_PATH}
        #       ${UNIVERSAL_JDBC_DRIVER_PATH} for UDB/DB2
        #       ${ORACLE_JDBC_DRIVER_PATH}
        #       ${WAS_LIBS_DIR} for MS/SQL
        #       ${MICROSOFT_JDBC_DRIVER_PATH}
        #       ${MICROSOFT_JDBC_DRIVER_NATIVEPATH}
        #       ${CONNECTJDBC_JDBC_DRIVER_PATH} for MS/SQL
        #jdbcProviders = {}
        #for providerId in AdminConfig.list('JDBCProvider', clusterId).splitlines():
        #    jdbcProviders[AdminConfig.showAttribute(providerId,'name')] = providerId
        #providerId = AdminConfig.createUsingTemplate('JDBCProvider', clusterId, attributes, template)
        #printDebugLine('end')

        # configure JDBC data source(s)
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Creation DB2, SQL, and Oracle data sources')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        for provider in buildNotes['delta']['Cluster'][clusterName]['JDBC'].keys():
            if  provider == 'JDBCProvider': continue
            for jdbcIndex in range(len(buildNotes['delta']['Cluster'][clusterName]['JDBC'][provider])):
                jdbc = {}
                jdbc = buildNotes['delta']['Cluster'][clusterName]['JDBC'][provider][jdbcIndex][0][1][0]
                dataSourceId = ''
                for dataSource in AdminConfig.list('DataSource', clusterId).splitlines():
                    if AdminConfig.showAttribute(dataSource, 'name') == jdbc['DataSourceName'][0]:
                        dataSourceId = dataSource
                        printDebugLine(' '.join(['found',jdbc['DataSourceName'][0],'...']))
                        break
                if  dataSourceId == '':
                    printDebugLine(' '.join(['creating',
                                            {'DB2Provider':   'DB2',
                                             'OracleProvider':'Oracle',
                                             'SQLProvider':   'MS SQL'}[provider],
                                            'data source',jdbc['DataSourceName'][0], '...']))
                    # TODO something is not right here, how are non DB2 data sources created?
                    dataSourceId = createDataSource(clusterId, None, 'DB2', providerId, 
                        jdbc['DataSourceName'][0], 
                        jdbc['DataSourceJNDIName'][0], 
                        jdbc['ComponentManagedAuthAlias'][0], '', '')
                        #jdbc['WASDataSourceProperties'][0]['StatementCacheSize'][0], 
                        #jdbc['WASDataSourceProperties'][0]['PretestConnectionEnable'][0])
                if  jdbc.has_key('WASDataSourceProperties') :
                    printDebugLine('  ... now applying customization')
                    #for dsProperty in jdbc['WASDataSourceProperties'][0].keys():
                        #modifyDSProperty(dsProperty(dataSourceId, dsProperty, jdbc['WASDataSourceProperties'][0][dsProperty][0]))
                #modifyDSProperty(dataSourceId, "preTestSQLString", jdbc['WASDataSourceProperties'][0]['PretestSQLString'][0])
                # oracle has URL others have serverName and databaseName
                # only db2 has driverType and all others have portNumber
                if  provider == 'OracleProvider':
                    modifyDSProperty(dataSourceId,'URL', jdbc['DataSourceURL'][0])
                else:
                    modifyDSProperty(dataSourceId,"serverName",jdbc['DataBaseServerName'][0])
                    modifyDSProperty(dataSourceId,"databaseName",jdbc['DataBaseName'][0])
                    modifyDSProperty(dataSourceId,"portNumber",jdbc['PortNumber'][0])
                if  provider == 'DB2Provider':
                    modifyDSProperty(dataSourceId,"driverType",jdbc['DataBaseDriverType'][0])
                # Modify the connection pool
                printDebugLine('  ... then connection pool properties ...')
                modifyConnectionPool(dataSourceId,
                    jdbc['ConnectionPoolProperties'][0]['ConnectionPoolTimeout'][0],
                    jdbc['ConnectionPoolProperties'][0]['ConnectionPoolMaxConnections'][0],
                    jdbc['ConnectionPoolProperties'][0]['ConnectionPoolMinConnections'][0],
                    jdbc['ConnectionPoolProperties'][0]['ConnectionPoolReapTime'][0],
                    jdbc['ConnectionPoolProperties'][0]['ConnectionPoolUnusedTimeout'][0],
                    jdbc['ConnectionPoolProperties'][0]['ConnectionPoolagedTimeout'][0],
                    jdbc['ConnectionPoolProperties'][0]['ConnectionPoolPurgePolicy'][0])
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        #printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure mail
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure mail')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        if  buildNotes['delta']['Cluster'][clusterName].has_key('MailResources') :
            mailSession = buildNotes['delta']['Cluster'][clusterName]['MailResources']['MailSessions'][0]
            for serverName in buildNotes['delta']['Cluster'][clusterName]['Server'].keys():
                mailProviderId = AdminConfig.list('MailProvider', clusterId)
                mailSessions = AdminConfig.list('MailSession', mailProviderId).splitlines()
                mailSessionExists = 0
                for loopSession in mailSessions:
                    if loopSession == '' : continue
                    mailSessionExists = mailSessionExists or (mailSession['MailSessionName'][0] == 
                                                              AdminConfig.showAttribute(loopSession, 'name'))
                    if mailSessionExists :
                        printDebugLine(''.join(['applying changes to mail session ',mailSession['MailSessionName'][0],'.']))
                        #TODO fix the following repeative tests
                        if mailSession['MailSessionJNDIName'][0] != AdminConfig.showAttribute(loopSession, 'jndiName'):
                            AdminConfig.modify(loopSession, [['jndiName', mailSession['MailSessionJNDIName'][0]]])
                        if mailSession['MailTransportHost'][0]   != AdminConfig.showAttribute(loopSession, 'mailTransportHost'):
                            AdminConfig.modify(loopSession, [['jndiName', mailSession['MailTransportHost'][0]]])
                        if mailSession['MailFromAddress'][0]     != AdminConfig.showAttribute(loopSession, 'mailFrom'):
                            AdminConfig.modify(loopSession, [['jndiName', mailSession['MailFromAddress'][0]]])
                        break # no need to check further mailSessions
                if mailSessionExists : continue # skipping any update, no good reason, probably should be changed
                attributesCommon =     [['name',              mailSession['MailSessionName'][0]]]
                attributesCommon.append(['jndiName',          mailSession['MailSessionJNDIName'][0]])
                attributesCommon.append(['mailTransportHost', mailSession['MailTransportHost'][0]])
                attributesCommon.append(['mailTransportUser', ''])
                attributesCommon.append(['mailTransportPassword', ''])
                attributesCommon.append(['mailFrom',          mailSession['MailFromAddress'][0]])
                attributesCommon.append(['strict', 'false'])
                attributesCommon.append(['debug', 'false'])
                attributes = AttributesCommon
                for protocol in AdminConfig.showAttribute(mailProviderId, 'protocolProviders')[1:-1].split():
                    if (AdminConfig.showAttribute(protocol, 'protocol') == 'smtp'):
                        attributes.append(['mailTransportProtocol', protocol])
                    if (AdminConfig.showAttribute(protocol, 'protocol') == 'pop3'):
                        attributes.append(['mailStoreProtocol', protocol])
                printInfoLine(''.join(['creating mail session ',mailSession['MailSessionName'][0],'.']))
                AdminConfig.create('MailSession',mailProviderId,attributes)
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure url
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure URL(s)')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        if  buildNotes['delta']['Cluster'][clusterName].has_key('URLResources') :
            urlProv = AdminConfig.list('URLProvider',clusterId).splitlines()[0]
            urlList = AdminConfig.list('URL',clusterId)
            urls = {}
            for url in AdminConfig.list('URL',clusterId).splitlines():
                urls[AdminConfig.showAttribute(url,'name')]=url
            for url in buildNotes['delta']['Cluster'][clusterName]['URLResources']['URL']:
                if urls.has_key(url['URLName'][0]):
                    if  AdminConfig.showAttributes(urls[url['URLName'][0]],'jndiName') != url['URLJNDIName'][0]:
                        printDebugLine(' '.join(['modifying URL',url['URLName'][0],'JNDI to',url['URLJNDIName'][0]]))
                        AdminConfig.modify(urls[url['URLName'][0]],[['jndiName',url['URLJNDIName'][0]]])
                    if  AdminConfig.showAttributes(urls[url['URLName'][0]],'spec') != url['URLspec'][0]:
                        printDebugLine(' '.join(['modifying URL',url['URLName'][0],'spec to',url['URLspec'][0]]))
                        AdminConfig.modify(urls[url['URLName'][0]],[['spec',url['URLspec'][0]]])
                else:
                    printDebugLine(' '.join(['creating URL',url['URLName'][0]]))
                    AdminConfig.create('URL',urlProv,[['name',    url['URLName'][0]],
                                                      ['jndiName',url['URLJNDIName'][0]],
                                                      ['spec',    url['URLSpec'][0]]])
                #printDebugLine(' '.join(['passsing URL',url['URLName'][0],'to resources.py(setupURL()).']))
                #setupURL(clusterName, None, url['URLName'][0], url['URLJNDIName'][0], url['URLSpec'][0], '')
#                scopeId = getScopeID(scopeS, scopeN)
#                name = ['name', uName]
#                jndi = ['jndiName', uJNDI]
#                spec = ['spec', uSpec]
#                desc = ['description', uDesc]
#                attrs = [name, jndi, spec, desc]
#            
#                urlProvList = AdminConfig.list('URLProvider', scopeId)
#                for urlProv in urlProvList.split(lineSep):
#                    if(AdminConfig.showAttribute(urlProv, 'name') == "Default URL Provider"):
#                        urlList = AdminConfig.list('URL', urlProv)
#                        if(urlList != ""):
#                            for url in urlList.split(lineSep):
#                                #curname = AdminConfig.showAttribute(url, 'name')
#                                curjndi = AdminConfig.showAttribute(url, 'jndiName')
#                                curspec = AdminConfig.showAttribute(url, 'spec')
#                                if(curjndi == uJNDI):
#                                    if(curspec != uSpec):
#                                        AdminConfig.modify(url, [['spec', uSpec]])
#                                        print "INFO: setupURL: URL " + uJNDI + " specfication modified from " + curspec + " to " + uSpec
#                                    return
#                        AdminConfig.create('URL', urlProv, attrs)
#                print "INFO: setupURL: URL " + uJNDI + " created"
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure jms
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure JMS')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        if  buildNotes['delta']['Cluster'][clusterName].has_key('JMS') :
            for provider in buildNotes['delta']['Cluster'][clusterName]['JMS']['Provider']:
                classpath = ';'.join(provider['ClassPath'])
                providerId = createJmsProvider(clusterName, None, provider['Name'][0], classpath, 
                    provider['ExtInitCtxFactory'][0], provider['ExtProviderURL'][0])
                propertySet = AdminConfig.showAttribute(providerId, 'propertySet')
                if  propertySet == None:
                    propertySet = AdminConfig.create('J2EEResourcePropertySet', providerId, [])
                resourceProperties = AdminConfig.showAttribute(propertySet, 'resourceProperties')
                for customProperty in provider['CustomProperties'][0]['Property']:
                    addModifyJ2EEResourceProperty(propertySet, resourceProperties, 
                        customProperty['Name'][0], customProperty['Value'][0])
                for connectionFactory in provider['ConnectionFactory']:
                    printDebugLine('Nik\'s change for JMS managed authentication model...')
                    if connectionFactory.has_key('ComponentManagedAuthAlias') :
                        authDataAlias = connectionFactory['ComponentManagedAuthAlias'][0]
                    else :
                        authDataAlias = ''
                    printDebugLine('invoking jms.py(createJmsConnectionFactory()).')
                    connectionFactoryId = createJmsConnectionFactory(clusterName, None, providerId, 
                        connectionFactory['Name'][0],    connectionFactory['JNDI'][0], 
                        connectionFactory['ExtJNDI'][0], connectionFactory['Type'][0], 
                        authDataAlias)
                if  provider.has_key('JMSDestination'):
                    for destination in provider['JMSDestination']:
                        printDebugLine('invoking jms.py(createJmsDestination()).')
                        destinationId = createJmsDestination(clusterName, None, providerId, destination['Name'][0],
                            destination['JNDI'][0], destination['ExtJNDI'][0], destination['Type'][0])
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure name space binding
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure name space bindings')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        if  buildNotes['delta']['Cluster'][clusterName].has_key('NameSpaceBindings') :
            for nameSpace in buildNotes['delta']['Cluster'][clusterName]['NameSpaceBindings']['NameSpace']:
                printDebugLine(''.join(['configuring name space ',
                                       nameSpace['NameSpaceIdentifier'][0],
                                       ', resource.py(setupNameSpaceString)).']))
                setupNameSpaceString(clusterName, None, nameSpace['NameSpaceIdentifier'][0],
                    nameSpace['NameSpaceName'][0], nameSpace['NameSpaceStringValue'][0])
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure name shared libraries
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure shared libraries')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        #AdminConfig.create('Library', AdminConfig.getid('/Cell:KAHDEV/ServerCluster:ContentMgmt/'), 
        #                   '[[nativePath "rcs test nativelibpath"] [name "rcs"] [isolatedClassLoader false] [description "rcs test description"] [classPath "rcs test classpath"]]') 
        #                    [isolatedClassLoader "true"]
        if  buildNotes['delta']['Cluster'][clusterName].has_key('SharedLibraries'):
            for library in buildNotes['delta']['Cluster'][clusterName]['SharedLibraries']:
                libraryAttributes=''
                for attribute in library['Library'][0].keys():
                    libraryAttributes = ' '.join([libraryAttributes, '[%s "%s"]' % (attribute, library['Library'][0][attribute][0])])
                printToDoLine('Fix shared library issues, duplicate entries, empty description')
                printDebugLine('creating shared library, %s.' % library['Library'][0]['name'][0])
                AdminConfig.create('Library', clusterId, '[%s]'%libraryAttributes[1:])
                printDebugLine('creating shared library reference to %s.' % library['Library'][0]['name'][0])
                libraryId = AdminConfig.create("LibraryRef", 
                    AdminConfig.showAttribute(AdminConfig.showAttribute(
                        AdminConfig.getid("/Deployment:"+appName+"/"), "deployedObject"), "classloader"), 
                    [["libraryName", library['Library'][0]['name'][0]], ["sharedClassloader", "true"]] )
                
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure servers
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure of servers')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        for serverName in buildNotes['delta']['Cluster'][clusterName]['Server'].keys():
            server   = buildNotes['delta']['Cluster'][clusterName]['Server'][serverName]
            nodeName = server['NodeName']
            nodeId   = AdminConfig.getid(''.join(['/Node:',nodeName,'/']))
            printDebugLine(''.join(['cluster ',clusterName,', server/node ',serverName,'/',nodeName]))
            # configure jvm
            serverId = AdminConfig.getid(''.join(['/Server:',serverName,'/']))
            if  serverId == '':
                printDebugLine(' '.join(['server',serverName,'not found, need to create.']))
                #serverId = AdminConfig.create('Server', nodeId, [['name', serverName]])
                printDebugLine('adding server to cluster')
                addClusterMember(clusterName, serverName, nodeName)
                serverId = AdminConfig.getid(''.join(['/Server:',serverName,'/']))
                # cleaning out junky defaults
                try:
                    deleteChain(          serverId, nodeName, 'WCInboundAdmin')
                    deleteChain(          serverId, nodeName, 'WCInboundAdminSecure')
                except:
                    printWarningLine('transport.py.deleteChain() has issues.')
                try:
                    deleteEndPoint(       serverId, nodeName, 'WC_adminhost')
                    deleteEndPoint(       serverId, nodeName, 'WC_adminhost_secure')
                    #deleteEndPoint(       serverId, nodeName, 'WC_defaulthost_secure')
                except:
                    printWarningLine('transport.py.deleteEndPoint() has issues.')
                try:
                    disableTransportChain(serverId, nodeName, 'WCInboundDefaultSecure')
                    disableTransportChain(serverId, nodeName, 'HttpQueueInboundDefault')
                    disableTransportChain(serverId, nodeName, 'HttpQueueInboundDefaultSecure')
                except:
                    printWarningLine('transport.py.disableTransportChain() has issues.')
            else:
                printDebugLine(''.join(['existing server: ',serverName,'...',serverId[serverId.rfind('#')+1:-1]]))

            # configure HA Manager
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure HA Manager')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  buildNotes['delta']['Cluster'][clusterName]['Server'][serverName].has_key('HAManager'):
                AdminConfig.modify(AdminConfig.list('HAManagerService', serverId),
                                   [['enable', buildNotes['delta']['Cluster'][clusterName]['Server'][serverName]['HAManager']]]) 
                printDebugLine(' '.join(['HA Manager attribute enable set to',
                                        buildNotes['delta']['Cluster'][clusterName]['Server'][serverName]['HAManager']]))
            else:
                printDebugLine('HA Manager tag not found, no change')
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
                
            # configure (TCP) End Points
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure TCP end point')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if buildNotes['delta']['Cluster'][clusterName]['Server'][serverName].has_key('TCPEndPoint'):
                tcpEndPoint = buildNotes['delta']['Cluster'][clusterName]['Server'][serverName]['TCPEndPoint']
                printDebugLine(''.join(['configuring TCP end point ',tcpEndPoint['Name'],
                                       ' =  ',tcpEndPoint['Host'],':',tcpEndPoint['Port'],'.']))
                modifyEndPoint(serverName,nodeName,tcpEndPoint['Name'],tcpEndPoint['Host'],tcpEndPoint['Port'])
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure Transaction service settings
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure Transaction service settings')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            transactionService = buildNotes['delta']['Cluster'][clusterName]['Server'][serverName]['TransactionService']
            printDebugLine('calling jvm.py(transactionSvcProps()).')
            transactionSvcProps(serverName,nodeName,transactionService['TotalTranLifetimeTimeout'], 
                transactionService['PropogatedOrBMTTransLifetimeTimeout'])
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure ORB (Object Request Broker)
            # obsolete ... since 7.0 WAS automatically configureds this
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure Web Container settings
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure web container')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  server.has_key('WebContainer'):
                createChainWithEndPoint(serverName,nodeName,'WCInboundDefault','WCInboundDefault', 
                    '*', server['TCPEndPoint']['Port'],'false')
                #createChainWithEndPoint(jvmName, nodeName, chainName, endPointName, host, port, ssl)
                #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
                processStage.append('Configure web container session settings')
                printDebugLine('start')
                #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
                # configure session settings
                sessionManagement = server['WebContainer']['SessionManagement']
                printDebugLine('apparently, we no assume domain replication now.')
                printDebugLine('calling jvm.py(changeJVMSessionSettings()).')
                changeJVMSessionSettings(serverName,nodeName,sessionManagement['CookieName'], 
                    sessionManagement['SessionTimeout'],sessionManagement['DistributedSessionType'],"","BOTH")
                #changeJVMSessionSettings(jvmName, nodeName, cookieName, timeout, prsType, rplDomain, rplMode)
                printDebugLine('end')
                #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    
                #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
                processStage.append('Configure custom properties within web container')
                printDebugLine('start')
                #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
                printDebugLine('not sure if we need this anymore, WASQuery.py provides it, not well tested.')
                if  server['WebContainer'].has_key('CustomProperties') :
                    printDebugLine('looping through properties calling jvm.py(modifyWCProperty()).')
                    for customProperty in server['WebContainer']['CustomProperties'][0]['Property']:
                        modifyWCProperty(serverName,nodeName,customProperty['Name'][0],customProperty['Value'][0])
                        #modifyWCProperty(jvmName, nodeName, propertyName, propertyValue)
                printDebugLine('end')
                #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure Process Definition
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure process definition')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  server.has_key('ProcessDefinition') :
                if  server['ProcessDefinition'].has_keys('CustomProperties'):
                    printDebugLine('calling jvm.py(modifyProcessDefProperty())')
                    for customProperty in server['ProcessDefinition']['CustomProperties'][0]['Property']:
                        modifyProcessDefProperty(serverName,nodeName, 
                            customProperty['Name'][0], customProperty['Value'][0])
                        #modifyProcessDefProperty(jvmName, nodeName, propName, propValue)
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure JVM settings
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure JVM settings')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure classpath
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure classpath')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  server['jvm'].has_key('classpath'):
                printDebugLine('calling jvm.py(modifyClasspath())')
                modifyClasspath(serverName,nodeName,';'.join(server['jvm']['classpath']), 0)
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure heap parameters
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure heap and garbage collection parameters')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  server['jvm'].has_key('heap'):
                printDebugLine('calling jvm.py(toogleVerboseGC()).  Note that I didnt spell it, just use it - RShen')
                toogleVerboseGC(serverName, nodeName, server['jvm']['heap']['vgc'])
                printDebugLine('calling jvm.py(modifyMinHeap())')
                modifyMinHeap(serverName, nodeName, server['jvm']['heap']['min'])
                printDebugLine('calling jvm.py(modifyMaxHeap())')
                modifyMaxHeap(serverName, nodeName, server['jvm']['heap']['max'])
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure generic arguments
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure generic arguments')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  server['jvm'].has_key('args'):
                printDebugLine('calling jvm.py(setGenericJVMArgs())')
                setGenericJVMArgs(serverName, nodeName, ' '.join(server['jvm']['args']))
                #setGenericJVMArgs(jvmName, nodeName, args)
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure message listener service
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure listener service')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  server.has_key('MessageListenerService'):
                for messageListenerService in server['MessageListenerService']:
                    for messageListenerPort in messageListenerService:
                        printDebugLine('calling jvm.py(createMsgListenerPort()).')
                        createMsgListenerPort(serverName, nodeName, 
                            messageListenerPort['name'],
                            messageListenerPort['connectionFactoryJNDIName'],
                            messageListenerPort['destinationJNDIName'],
                            messageListenerPort['maxSessions'],
                            messageListenerPort['maxRetries'],
                            messageListenerPort['maxSessions'],
                            messageListenerPort['maxMessage'])
                        #createMsgListenerPort(jvmName, nodeName, portName, cfJNDI, dJNDI, maxSess, maxRetry, maxMsg)
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure monitoring policy
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure JVM monitoring policy')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if  server.has_key('MonitoringPolicy'):
                printDebugLine('calling jvm.py(monitorSettings()).')
                monitorSettings(serverName, nodeName, 
                    server['MonitorPolicy']['maximumStartupAttempts'],
                    server['MonitorPolicy']['pingInterval'],
                    server['MonitorPolicy']['pingTimeout'],
                    server['MonitorPolicy']['autoRestart'],
                    server['MonitorPolicy']['nodeRestartState'])
                #monitorSettings(jvmName, nodeName, startupAtmp, pingInt, pingTime, autoRstrt, svrState)
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure logging
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure JVM logging')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if server['jvm'].has_key('logs'):
                for log in server['jvm']['logs']:
                    printDebugLine('calling jvm.py(JVMLogSettings()).')
                    JVMLogSettings(serverName, nodeName,
                        log['Type'], log['Location'], log['Format'], log['RolloverType'],
                        log['BackupFiles'], log['RolloverSize'], log['BaseHour'], 
                        log['RolloverPeriod'], log['FormatWrites'], log['suppresWrites'],
                        log['suppressStackTrace'])
                    #JVMLogSettings(jvmName, nodeName, type, location, format, rollType, noBkp, rollSize, baseHr, rollPrd, fmtW, supW, supST)
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # configure custom services
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure custom services')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            if server.has_key('CustomServices'):
                for service in server['CustomServices']:
                    printDebugLine('calling jvm.py(customService()).')
                    customServiceId = customService(serverName, nodeName, service['displayName'],
                        service['classname'], service['classpath'],
                        service['enable'], service['description'])
                    if  service.has_key('properties'):
                        for property in service['properties']:
                            printDebugLine('calling jvm.py(modifyCustomServiceProperty()).')
                            modifyCustomServiceProperty(customServiceId, property['name'], property['value']) 
                #customService(jvmName, nodeName, svcName, className, classPath, startupEnabled, description)
                #modifyCustomServiceProperty(cService, propName, propValue)
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            #configResources(jvmName, nodeName, instance)
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            processStage.append('Configure JVM resources')
            printDebugLine('start')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

            # end JVM section
            printDebugLine('end')
            #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
 
        # end serverName loop
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure cluster resources
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure cluster resources')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure adapter
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Creation of special CICS, IMS, and other resource adapters')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        # might as well hard code CICS and IMS until they are sunsetted
        ### Setup Resource Adapters, ex. IMS, CICS, SONIC
        ###radapterList = resNode.getElementsByTagName("Adapter")
        ####radapter(serverScope, nodeScope, radapterList)
        if  buildNotes['delta']['Cluster'][clusterName].has_key('ResourceAdapters') :
            for adapterIndex in range(len(buildNotes['delta']['Cluster'][clusterName]['ResourceAdapters']['Adapter'])):
                providerName = buildNotes['delta']['Cluster'][clusterName]['ResourceAdapters']['Adapter'][adapterIndex]['ProviderName'][0]
                adapterId = AdminConfig.getid(''.join(['/ServerCluster:',clusterName,'/J2CResourceAdapter:',providerName,'/']))
                if  adapterId == '':
                    rarPath = 'invalid'
                    if  providerName == 'CICS':
                        rarPath = 'C:/Installs/IBM/CICS/6.1.0.1/cicseci.rar'
                        printWarningLine(''.join(['CICS rar path and file name hardcoded to ',rarPath,'.']))
                    elif providerName == 'IMS':
                        rarPath = 'C:/Installs/IBM/IMS/ICO101/V1020/JCA15/ims1020.rar'
                        printWarningLine(''.join(['IMS rar path and file name hardcoded to ',rarPath,'.']))
                    else:
                        printWarningLine(''.join(['Cluster resource neither CICS or IMS, ',providerName,
                                                  ', will need to be defined manually.']))
                    if rarPath != 'invalid' :
                        adapterId = AdminConfig.installResourceAdapter(rarPath,nodeName,
                                                                       ''.join(['[-rar.name ',providerName,']']))
                        continue # skip the rest, continue with next adapter
                printDebugLine(''.join(['J2CResourceAdapter: ',providerName,'...',adapterId[adapterId.rfind('#')+1:-1]]))
                ## Now build the required J2C Connection Factories
                j2ccf = buildNotes['delta']['Cluster'][clusterName]['ResourceAdapters']['Adapter'][adapterIndex]['J2CConnFactory'][0]
                # IBM bug: AdminConfig.getid('/ServerCluster:RPW6FrontEnd/J2CConnectionFactory:plisconn/') returns ''
                # .... have to do this the hard way ... and significantly delays processing ... assumes one object returned
                j2ccfId = AdminConfig.list('J2CConnectionFactory',''.join([j2ccf['Name'][0],
                                                                           '(*/clusters/',clusterName,'|*']))
                if  j2ccfId == '' :
                    j2ccfParameters = ''.join(['-name "',j2ccf['Name'][0],'" -jndiName "',j2ccf['JNDIName'][0],'"']) 
                    j2ccfInterface  = j2ccf['Interface'][0]
                    if  j2ccfInterface != '' : 
                        j2ccfParameters = ''.join(['-connectionFactoryInterface ',j2ccfInterface,' ',j2ccfParameters])
                    if  j2ccf.has_key('ComponentManagedAuthAlias') : 
                        j2ccfParameters = ''.join([j2ccfParameters,' -authDataAlias ',j2ccf['ComponentManagedAuthAlias'][0]])
                    j2ccfParameters = j2ccfParameters.join(['[',']'])
                    printDebugLine(' '.join(['J2C connection factory parameters =',j2ccfParameters]))
                    j2ccfId = AdminTask.createJ2CConnectionFactory(adapterId, j2ccfParameters) 
                printDebugLine(''.join(['J2CConnectionFactory ',j2ccf['Name'][0],'...',j2ccfId[j2ccfId.rfind('#')+1:-1]]))
                j2ccfConnectionPoolProperties = []
                for key in j2ccf['ConnectionPoolProperties'][0].keys():
                    parameter = re.search(r'^ConnectionPool(.*)', key).group(1)
                    # the following gyrations is due to our inconsistencies in parameter names
                    if  parameter in ['MaxConnections','MinConnections','PurgePolicy','UnusedTimeout','ReapTime']: 
                        parameter = parameter[0].lower() + parameter[1:]
                    if parameter == 'Timeout' : parameter = 'connectionTimeout'
                    # while parameter == 'agedTimeout' is valid 
                    j2ccfConnectionPoolProperties.append([parameter,j2ccf['ConnectionPoolProperties'][0][key][0]])
                if len(parameter) > 0 : 
                    AdminConfig.modify(AdminConfig.showAttribute(j2ccfId,'connectionPool'),j2ccfConnectionPoolProperties) 
                j2ccfResourceProperties = AdminConfig.showAttribute(AdminConfig.showAttribute(j2ccfId,'propertySet'),
                                                                    'resourceProperties')[1:-1].split()
                j2ccfResourcePropertyNames = []
                for resourceProperty in j2ccfResourceProperties:
                    j2ccfResourcePropertyNames.append(AdminConfig.showAttribute(resourceProperty, 'name'))
                for customPropertySet in range(len(j2ccf['CustomProperties'])):
                    for j2ccfCustomProperty in j2ccf['CustomProperties'][customPropertySet].keys():
                        if  j2ccfCustomProperty in j2ccfResourcePropertyNames:
                            AdminConfig.modify(j2ccfResourceProperties[j2ccfResourcePropertyNames.index(j2ccfCustomProperty)], 
                                [['value', j2ccf['CustomProperties'][customPropertySet][j2ccfCustomProperty][0]]])
                        else:
                            printSevereLine(j2ccfCustomProperty.join(['J2C ConnectionFactory custom property ',
                                                                      ' not recognized, check spelling if not derived.']))
                            raise Exception,'J2C ConnectionFactory custom property not in list of resource properties of the factory.' 
            # end adapterIndex loop
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # end cluster resources
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

        # configure core group
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        processStage.append('Configure core group')
        printDebugLine('start')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
        # Change cluster core group
        ha = 'OFF'
        if  buildNotes['delta']['Cluster'][clusterName]['Server'][serverName].has_key('HAManager') :
            if  buildNotes['delta']['Cluster'][clusterName]['Server'][serverName]['HAManager'] == 'true' :
                ha = 'ON'
        nodeVersion = AdminTask.getNodeBaseProductVersion(nodeName.join(['[-nodeName ',']']))
        hostName    = AdminConfig.showAttribute(nodeId, 'hostName')
        nodeVersion = int(nodeVersion[0] + nodeVersion[2])
        hostNumber  = int(hostName[9] + hostName[10]) 
        clusterCoreGroup = 'DefaultCoreGroup'
        if  nodeVersion == 70 :
            if    (hostNumber > 89  &  hostNumber < 100) | (hostNumber > 39  &  hostNumber < 50):
                clusterCoreGroup = ha.join(['CORE_HA_','_70'])
            elif  (hostNumber > 69  &  hostNumber <  80) | (hostNumber > 29  &  hostNumber < 40):
                clusterCoreGroup = ha.join(['SERVICE_HA_','_70'])
        printDebugLine('calling jvm.py(changeClusterCoreGroup()) ... only works if cluster is stopped ... and can take a while ...')
        try:
            changeClusterCoreGroup(clusterName, clusterCoreGroup)
        except:
            printDebugLine('  ... like so, continueing ...')
        printDebugLine('end')
        #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

    # end clusterName loop
    printDebugLine('end')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

    printDebugLine('end')
    return     
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    #end function buildTask
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

def computeDelta(buildNotes) :
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    processStage.append('Function computeDelta(buildNotes)')
    printDebugLine('start')
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    if (buildNotes['alpha']['DOM'] == None):
        buildNotes['delta'] = buildNotes['omega']
        del buildNotes['omega']['DOM']
    else:
        buildNotes['remove'] = {}
        for component in buildNotes['omega'].keys() :
            buildNotes['remove']['component'] = walkTheLine(component, buildNotes['omega'], buildNotes['alpha'])
    return buildNotes['delta']
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
    #end function buildTask
    #===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

def walkTheLine(component, omega, alpha) :
    for subComponent in omega[component] :
        if  type(subComponent) == type({}) :
            for  yaSubComponent in subComponent.keys() :
                alpha[component][subComponent][yaSubComponent] = walkTheLine(yaSubComponent, omega[subComponent][yaSubComponent], alpha[subComponent][yaSubComponet])
        elif type(subComponent) == type([]) :
            for  yaSubComponent in buildNotes[subComponent] :
                return
        elif type(subComponent) == type('') :
            return
        return alpha
    
def walkTheList(component, buildNotesBranch) :
    return

