def installJCA(nodeName, jcaName, rarPath):
    #print "DEBUG: START: installJCA"
    adapterId = AdminConfig.getid('/Node:' + nodeName + '/J2CResourceAdapter:' + jcaName + '/')
    if(adapterId == ""):
        options = '[-rar.name ' + jcaName + ']'
        adapterId = AdminConfig.installResourceAdapter(rarPath, nodeName, options)
        print "INFO: installJCA: Installed " + jcaName
    #else:
    #    print "INFO: installJCA: " + jcaName + " already exists, continuing..."
    #print "DEBUG: END: installJCA"
    return adapterId

def copyJCA(scopeS, scopeN, jcaName, fromJcaName, fromNodeName, deep):
    #print "DEBUG: START: copyJCA"
    fromScope = getScopeString("", fromNodeName)
    fromJcaID = AdminConfig.getid(fromScope + 'J2CResourceAdapter:' + fromJcaName + '/')
    if(fromJcaID == ""):
        print "Exception: copyJCA: No Resource Adapter found by name " + fromJcaName + " at scope " + fromNodeName
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    scope = getScopeString(scopeS, scopeN)
    adapterId = AdminConfig.getid(scope + 'J2CResourceAdapter:' + jcaName + '/')
    if(adapterId == ""):
        scopeId = getScopeID(scopeS, scopeN)
        adapterId = AdminTask.copyResourceAdapter(fromJcaID, '[-scope ' + scopeId + ' -name ' + jcaName + ' -useDeepCopy ' + deep + ']')
        print "INFO: copyJCA: Built " + jcaName + " at scope " + scope
    #else:
    #    print "INFO: copyJCA: " + jcaName + " already exists, continuing..."
    #print "DEBUG: END: copyJCA"
    return adapterId

def createJ2CConnFactory(adapterId, name, jndi, interface, compAuthAlias):
    #print "DEBUG: START: createJ2CConnFactory"
    j2cfList = AdminConfig.list('J2CConnectionFactory', adapterId)
    new = j2cfList.find(name)
    if(new == -1):
        if((interface == "") & (compAuthAlias == "")):
            j2cfId = AdminTask.createJ2CConnectionFactory(adapterId, '[-name "' + name + '" -jndiName ' + jndi + ']')
        if((interface == "") & (compAuthAlias != "")):
            j2cfId = AdminTask.createJ2CConnectionFactory(adapterId, '[-name "' + name + '" -jndiName ' + jndi + ' -authDataAlias ' + compAuthAlias + ']')
        if((interface != "") & (compAuthAlias == "")):
            j2cfId = AdminTask.createJ2CConnectionFactory(adapterId, '[-connectionFactoryInterface ' + interface + ' -name "' + name + '" -jndiName ' + jndi + ']')
        if((interface != "") & (compAuthAlias != "")):
            j2cfId = AdminTask.createJ2CConnectionFactory(adapterId, '[-connectionFactoryInterface ' + interface + ' -name "' + name + '" -jndiName ' + jndi + ' -authDataAlias ' + compAuthAlias + ']')
        print "INFO: createJ2CConnFactory: Created J2C connection factory " + name
    else:
        for j2cfId in j2cfList.split(lineSep):
            j2cjndi = AdminConfig.showAttribute(j2cfId, 'jndiName')
            if(j2cjndi == jndi):
                #print "INFO: createJ2CConnFactory: J2C connection factory " + name + " already exists, continuing..."
                break
    #print "DEBUG: END: createJ2CConnFactory"
    return j2cfId

def createActivationSpec(adapterId, name, jndi, listenerType, compAuthAlias):
    #print "DEBUG: START: createActivationSpec"
    j2cListenerList = AdminConfig.list('J2CActivationSpec', adapterId)
    new = j2cListenerList.find(name)
    if(new == -1):
        if((listenerType == "") & (compAuthAlias == "")):
            j2cLId = AdminTask.createJ2CActivationSpec(adapterId, '[-name "' + name + '" -jndiName ' + jndi + ']')
        if((listenerType == "") & (compAuthAlias != "")):
            j2cLId = AdminTask.createJ2CActivationSpec(adapterId, '[-name "' + name + '" -jndiName ' + jndi + ' -authenticationAlias ' + compAuthAlias + ']')
        if((listenerType != "") & (compAuthAlias == "")):
            j2cLId = AdminTask.createJ2CActivationSpec(adapterId, '[-name "' + name + '" -jndiName ' + jndi + ' -messageListenerType ' + listenerType + ']')
        if((listenerType != "") & (compAuthAlias != "")):
            j2cLId = AdminTask.createJ2CActivationSpec(adapterId, '[-name "' + name + '" -jndiName ' + jndi + ' -messageListenerType ' + listenerType + ' -authenticationAlias ' + compAuthAlias + ']')
        print "INFO: createActivationSpec: Created J2C Activation Spec " + name
    else:
        for j2cLId in j2cListenerList.split(lineSep):
            j2cLjndi = AdminConfig.showAttribute(j2cLId, 'jndiName')
            if(j2cLjndi == jndi):
                #print "INFO: createActivationSpec: J2C Activation Spec " + name + " already exists, continuing..."
                break
    #print "DEBUG: END: createActivationSpec"
    return j2cLId

def modifyRAProperty(dsId, propName, propValue):
    #print "DEBUG: START: modifyRAProperty"
    if((dsId == None) | (dsId == "")):
        print "Exception: modifyRAProperty: Resource ID passed is bad"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    psId = AdminConfig.showAttribute(dsId, 'propertySet')
    if(psId == ""):
        print "Exception: modifyRAProperty: Resource ID passed is bad"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    props = AdminConfig.showAttribute(psId, 'resourceProperties')
    # Call the function in common.py
    modifyProperty(dsId, props, propName, propValue)
    #print "DEBUG: END: modifyRAProperty"
    return

def modifyRAResourceProperty(dsId, propName, propValue):
    #print "DEBUG: START: modifyRAResourceProperty"
    if((dsId == None) | (dsId == "")):
        print "Exception: modifyRAProperty: Resource ID passed is bad"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    props = AdminConfig.showAttribute(dsId, 'resourceProperties')
    # Call the function in common.py
    modifyProperty(dsId, props, propName, propValue)
    #print "DEBUG: END: modifyRAResourceProperty"
    return