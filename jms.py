def createJmsProvider(scopeS, scopeN, provName, classpath, initContext, provURL):
    #print "DEBUG: START: createJmsProvider"

    nameAttr = ['name', provName]
    cpAttr = ['classpath', classpath]
    initCtxtAttr = ['externalInitialContextFactory', initContext]
    provURLAttr = ['externalProviderURL', provURL]
    attrs = [nameAttr, cpAttr, initCtxtAttr, provURLAttr]
    scope = getScopeString(scopeS, scopeN)
    provId = AdminConfig.getid(scope + 'JMSProvider:' + provName + '/')
    if(provId == ""):
        scopeId = getScopeID(scopeS, scopeN)
        provId = AdminConfig.create('JMSProvider', scopeId, attrs)
        print "INFO: createJmsProvider: Built " + provName + " at scope " + scope
    else:
        if((AdminConfig.showAttribute(provId, 'classpath') != classpath) & (classpath != "")):
            AdminConfig.modify(provId, [['classpath', classpath]])
            print "INFO: createJmsProvider: Modified classpath for JMSProvider " + provName
        if((AdminConfig.showAttribute(provId, 'externalInitialContextFactory') != initContext) & (initContext != "")):
            AdminConfig.modify(provId, [['externalInitialContextFactory', initContext]])
            print "INFO: createJmsProvider: Modified externalInitialContextFactory for JMSProvider " + provName + " to " + initContext
        if((AdminConfig.showAttribute(provId, 'externalProviderURL') != provURL) & (provURL != "")):
            AdminConfig.modify(provId, [['externalProviderURL', provURL]])
            print "INFO: createJmsProvider: Modified externalProviderURL for JMSProvider " + provName + " to " + provURL
        #AdminConfig.modify(provId, attrs)
        #print "INFO: createJmsProvider: Modified " + provName + " at scope " + scope

    #print "DEBUG: END: createJmsProvider"
    return provId

def createJmsConnectionFactory(scopeS, scopeN, provId, name, jndi, externalJndi, type, CmpMngAls, CntMngAls):
    #print "DEBUG: START: createJmsConnectionFactory"

    nameAttr = ['name', name]
    jndiAttr = ['jndiName', jndi]
    extJndiAttr = ['externalJNDIName', externalJndi]
    typeAttr = ['type', type]
    descAttr = ['description', '']

    #Added by Nik to include the configuration of Auth Alias in Connection Factory
    foundCmpAuth = 0
    foundCntAuth = 0
    compAuth = ['authDataAlias', ""]

    jaasAuthList = AdminConfig.list('JAASAuthData')
    if(jaasAuthList != ""):
        manager = AdminControl.getNode()
        for jaasAuth in jaasAuthList.split(lineSep):
            authAlias = AdminConfig.showAttribute(jaasAuth, 'alias')
            if((authAlias == CmpMngAls) or (authAlias == (manager + '/' + CmpMngAls))):
                compAuth = ['authDataAlias', authAlias]
                foundCmpAuth = 1
                break
        for jaasAuth in jaasAuthList.split(lineSep):
            authAlias = AdminConfig.showAttribute(jaasAuth, 'alias')
            if((authAlias == CntMngAls) or (authAlias == (manager + '/' + CntMngAls))):
                contAuth = authAlias
                foundCntAuth = 1
                break
    if((foundCmpAuth == 1) & (foundCntAuth == 1)):
        print "WARNING: createJmsConnectionFactory: You have specified both component and container managed authentication aliases for " + name
        print "WARNING: createJmsConnectionFactory: We typically only use either, you might want to re-check your property xml for errors"
    if((foundCmpAuth == 0) & (foundCntAuth == 0)):
        print "WARNING: createJmsConnectionFactory: No component or container managed authentication alias match found for " + name
        print "WARNING: createJmsConnectionFactory: Your connection factory might not work properly, continuing..."

    attrs = [nameAttr, jndiAttr, extJndiAttr, typeAttr, descAttr, compAuth]
    #End of Nik's changes

    scope = getScopeString(scopeS, scopeN)
    provName = AdminConfig.showAttribute(provId, 'name')
    factoryId = AdminConfig.getid(scope + 'JMSProvider:' + provName + '/GenericJMSConnectionFactory:' + name + '/')
    if(factoryId != ""):
        curJNDI = AdminConfig.showAttribute(factoryId, 'jndiName')
        if(curJNDI != jndi):
            AdminConfig.modify(factoryId, [['jndiName', jndi]])
            print "INFO: createJmsConnectionFactory: Modified JNDI name for CF " + name + " from " + curJNDI + " to " + jndi
        curExtJNDI = AdminConfig.showAttribute(factoryId, 'externalJNDIName')
        if(curExtJNDI != externalJndi):
            AdminConfig.modify(factoryId, [['externalJNDIName', externalJndi]])
            print "INFO: createJmsConnectionFactory: Modified external JNDI for CF " + name + " from " + curExtJNDI + " to " + externalJndi
        curType = AdminConfig.showAttribute(factoryId, 'type')
        if(curType != type):
            AdminConfig.modify(factoryId, [['type', type]])
            print "INFO: createJmsConnectionFactory: Modified type for CF " + name + " from " + curType + " to " + type
        curAuthAlias = AdminConfig.showAttribute(factoryId, 'authDataAlias')
        if((curAuthAlias != CmpMngAls) & (foundCmpAuth == 1)):
            AdminConfig.modify(factoryId, [['authDataAlias', CmpMngAls]])
            print "INFO: createJmsConnectionFactory: Modified component-managed auth alias for CF " + name + " from " + str(curAuthAlias) + " to " + CmpMngAls
    else:
        # Find the template ID
        tmplName = 'Generic QueueConnectionFactory for Windows'
        tmplList = AdminConfig.listTemplates('GenericJMSConnectionFactory', tmplName)
        if(tmplList == ""):
            print "Exception: createJmsConnectionFactory: Could not find a JMS Provider Template of type " + tmplName
            raise Exception, "Script raised exception, you are doing something wrong!!!"
        for tmplId in tmplList.split(lineSep):
            curName = AdminConfig.showAttribute(tmplId, 'name')
            if(curName == tmplName):
                break
        factoryId = AdminConfig.createUsingTemplate('GenericJMSConnectionFactory', provId, attrs, tmplId)
        print "INFO: createJmsConnectionFactory: Built generic jms factory " + name + ", type " + type

    #Etien's changes to allow for Container-managed authentication -- this sets the value to either the empty string, or what was passed in if it exists.
    if(foundCntAuth == 1):
        mappingId = AdminConfig.showAttribute(factoryId, 'mapping')
        if(mappingId == None):
            mappingId = AdminConfig.create('MappingModule', factoryId, [['authDataAlias', contAuth]])
            print "INFO: createJmsConnectionFactory: Created mapping module and added container managed auth alias " + CntMngAls
        else:
            curAuthAlias = AdminConfig.showAttribute(mappingId, 'authDataAlias')
            if(curAuthAlias != contAuth):
                AdminConfig.modify(mappingId, [['authDataAlias', contAuth]])
                print "INFO: createJmsConnectionFactory: Modified container-managed auth alias for CF " + name + " from " + str(curAuthAlias) + " to " + CntMngAls
    #End Etien's changes

    #print "DEBUG: END: createJmsConnectionFactory"
    return factoryId

def createJmsDestination(scopeS, scopeN, provId, name, jndi, externalJndi, type):
    #print "DEBUG: START: createJmsDestination"

    nameAttr = ['name', name]
    jndiAttr = ['jndiName', jndi]
    extJndiAttr = ['externalJNDIName', externalJndi]
    typeAttr = ['type', type]
    descAttr = ['description', '']
    attrs = [nameAttr, jndiAttr, extJndiAttr, typeAttr, descAttr]

    scope = getScopeString(scopeS, scopeN)
    provName = AdminConfig.showAttribute(provId, 'name')
    destId = AdminConfig.getid(scope + 'JMSProvider:' + provName + '/GenericJMSDestination:'       + name + '/')
    if(destId == ""):
        # Find the template ID
        tmplName = 'Example.JMS.Generic.Win.Queue'
        tmplList = AdminConfig.listTemplates('GenericJMSDestination', tmplName)
        if(tmplList == ""):
            print "Exception: createJmsConnectionFactory: Could not find a JMS Provider Template of type " + tmplName
            raise Exception, "Script raised exception, you are doing something wrong!!!"
        for tmplId in tmplList.split(lineSep):
            curName = AdminConfig.showAttribute(tmplId, 'name')
            if(curName == tmplName):
                break
        destId = AdminConfig.create('GenericJMSDestination', provId, attrs)
        print "INFO: createJmsDestination: Built generic jms destination " + name + ", type " + type
    else:
        curJNDI = AdminConfig.showAttribute(destId, 'jndiName')
        if(curJNDI != jndi):
            AdminConfig.modify(destId, [['jndiName', jndi]])
            print "INFO: createJmsDestination: Modified JNDI name for " + name + " from " + curJNDI + " to " + jndi
        curExtJNDI = AdminConfig.showAttribute(destId, 'externalJNDIName')
        if(curExtJNDI != externalJndi):
            AdminConfig.modify(destId, [['externalJNDIName', externalJndi]])
            print "INFO: createJmsDestination: Modified externalJNDIName for " + name + " from " + curExtJNDI + " to " + externalJndi
        curType = AdminConfig.showAttribute(destId, 'type')
        if(curType != type):
            AdminConfig.modify(destId, [['type', type]])
            print "INFO: createJmsDestination: Modified type for " + name + " from " + curType + " to " + type

    #print "DEBUG: END: createJmsDestination"
    return destId

def createMsgListenerPort(jvmName, nodeName, name, cfjndi, dstjndi, maxSess, maxRetry, maxMsg):
    #print "DEBUG: START: createMsgListenerPort"

    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    mlsId = AdminConfig.list('MessageListenerService', jvmId)
    portList = AdminConfig.list('ListenerPort', mlsId)

    found = 0
    if(portList != ""):
        for portId in portList.split(lineSep):
            curName = AdminConfig.showAttribute(portId, 'name')
            if(curName == name):
                found = 1
                break

    if(found == 0):
        nameAttr = ['name', name]
        cfjndiAttr = ['connectionFactoryJNDIName', cfjndi]
        dstjndiAttr = ['destinationJNDIName', dstjndi]
        attrs = [nameAttr, cfjndiAttr, dstjndiAttr]
        portId = AdminConfig.create('ListenerPort', mlsId, attrs)
        print "INFO: createMsgListenerPort: Created message listener port " + name + " on " + jvmName

    curCFJndi = AdminConfig.showAttribute(portId, 'connectionFactoryJNDIName')
    if(curCFJndi != cfjndi):
        AdminConfig.modify(portId, [['connectionFactoryJNDIName', cfjndi]])
        print "INFO: createMsgListenerPort: Modified connectionFactoryJNDIName for " + name + " from " + curCFJndi + " to " + cfjndi
    curDestJndi = AdminConfig.showAttribute(portId, 'destinationJNDIName')
    if(curDestJndi != dstjndi):
        AdminConfig.modify(portId, [['destinationJNDIName', dstjndi]])
        print "INFO: createMsgListenerPort: Modified destinationJNDIName for " + name + " from " + curDestJndi + " to " + dstjndi
    curMaxMsg = AdminConfig.showAttribute(portId, 'maxMessages')
    if((curMaxMsg != maxMsg) & maxMsg.isdigit()):
        AdminConfig.modify(portId, [['maxMessages', maxMsg]])
        print "INFO: createMsgListenerPort: Modified max message count for " + name + " from " + curMaxMsg + " to " + maxMsg
    curMaxRetry = AdminConfig.showAttribute(portId, 'maxRetries')
    if((curMaxRetry != maxRetry) & maxRetry.isdigit()):
        AdminConfig.modify(portId, [['maxRetries', maxRetry]])
        print "INFO: createMsgListenerPort: Modified max retry count for " + name + " from " + curMaxRetry + " to " + maxRetry
    curMaxSess = AdminConfig.showAttribute(portId, 'maxSessions')
    if((curMaxSess != maxSess) & maxSess.isdigit()):
        AdminConfig.modify(portId, [['maxSessions', maxSess]])
        print "INFO: createMsgListenerPort: Modified max sessions count for " + name + " from " + curMaxSess + " to " + maxSess

    #print "DEBUG: END: createMsgListenerPort"
    return portId