def modifyConnectionPool(resourceId, connTimeout, maxConn, minConn, reapTime, unusedTimeout, agedTimeout, purgePolicy):
    #print "DEBUG: START: modifyConnectionPool"

    timeout = ['connectionTimeout', connTimeout]
    maxconn = ['maxConnections', maxConn]
    minconn = ['minConnections', minConn]
    reap = ['reapTime', reapTime]
    unused = ['unusedTimeout', unusedTimeout]
    aged = ['agedTimeout', agedTimeout]
    purgePol = ['purgePolicy', purgePolicy]
    props = [timeout, maxconn, minconn, reap, unused, aged, purgePol]
    if((resourceId == "") or (resourceId == None)):
        print "Exception: modifyConnectionPool: Resource ID passed is empty"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    poolId = AdminConfig.showAttribute(resourceId, 'connectionPool')
    if(poolId == ""):
        print "Exception: modifyConnectionPool: Resource ID passed is bad"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    resName = AdminConfig.showAttribute(resourceId, 'name')

    curConnTimeout = AdminConfig.showAttribute(poolId, 'connectionTimeout')
    if(curConnTimeout != connTimeout):
        AdminConfig.modify(poolId, [['connectionTimeout', connTimeout]])
        print "INFO: modifyConnectionPool: Modified connectionTimout for " + resName + " from " + curConnTimeout + " to " + connTimeout
    curMaxConn = AdminConfig.showAttribute(poolId, 'maxConnections')
    if(curMaxConn != maxConn):
        AdminConfig.modify(poolId, [['maxConnections', maxConn]])
        print "INFO: modifyConnectionPool: Modified maxConnections for " + resName + " from " + curMaxConn + " to " + maxConn
    curMinConn = AdminConfig.showAttribute(poolId, 'minConnections')
    if(curMinConn != minConn):
        AdminConfig.modify(poolId, [['minConnections', minConn]])
        print "INFO: modifyConnectionPool: Modified minConnections for " + resName + " from " + curMinConn + " to " + minConn
    curReapTime = AdminConfig.showAttribute(poolId, 'reapTime')
    if(curReapTime != reapTime):
        AdminConfig.modify(poolId, [['reapTime', reapTime]])
        print "INFO: modifyConnectionPool: Modified reapTime for " + resName + " from " + curReapTime + " to " + reapTime
    curUnusedTimeout = AdminConfig.showAttribute(poolId, 'unusedTimeout')
    if(curUnusedTimeout != unusedTimeout):
        AdminConfig.modify(poolId, [['unusedTimeout', unusedTimeout]])
        print "INFO: modifyConnectionPool: Modified unusedTimeout for " + resName + " from " + curUnusedTimeout + " to " + unusedTimeout
    curAgedTimeout = AdminConfig.showAttribute(poolId, 'agedTimeout')
    if(curAgedTimeout != agedTimeout):
        AdminConfig.modify(poolId, [['agedTimeout', agedTimeout]])
        print "INFO: modifyConnectionPool: Modified agedTimeout for " + resName + " from " + curAgedTimeout + " to " + agedTimeout
    curPurgePolicy = AdminConfig.showAttribute(poolId, 'purgePolicy')
    if(curPurgePolicy != purgePolicy):
        AdminConfig.modify(poolId, [['purgePolicy', purgePolicy]])
        print "INFO: modifyConnectionPool: Modified purgePolicy for " + resName + " from " + curPurgePolicy + " to " + purgePolicy

    #print "DEBUG: END: modifyConnectionPool"
    return

def modifyProperty(resourceId, props, propName, propValue):
    #print "DEBUG: START: modifyProperty"
    plist = props[1:len(props)-1].split(" ")
    # Modify if exists, and return
    for prop in plist:
        if(prop != ""):
            curPropName = AdminConfig.showAttribute(prop, 'name')
            curPropValue = AdminConfig.showAttribute(prop, 'value')
            if(curPropName == propName):
                if(curPropValue != propValue):
                    AdminConfig.modify(prop, [['value', propValue]])
                    #print "INFO: modifyProperty: Modified property " + propName + ", from " + curPropValue + " to " + propValue
                    print "INFO: modifyProperty: Modified property ",propName,", from ",curPropValue," to ",propValue
                return
    # Since it does not exist, throw an error message, and raise an exception
    print "Exception: modifyProperty: Property " + propName + " does not exist"
    raise Exception, "Script raised exception, you are doing something wrong!!!"
    #print "DEBUG: END: modifyProperty"
    return

def addModifyJ2EEResourceProperty(resourceId, props, propName, propValue):
    #print "DEBUG: START: addModifyJ2EEResourceProperty"
    plist = props[1:len(props)-1].split(" ")
    # Modify if exists, and return
    for prop in plist:
        if(prop != ""):
            curPropName = AdminConfig.showAttribute(prop, 'name')
            curPropValue = AdminConfig.showAttribute(prop, 'value')
            if(curPropName == propName):
                if(curPropValue != propValue):
                    AdminConfig.modify(prop, [['value', propValue]])
                    print "INFO: addModifyJ2EEResourceProperty: Modified property ",propName,", from ",curPropValue," to ",propValue
                return
    # Since it does not exist, create the property
    name = ['name', propName]
    value = ['value', propValue]
    prop = [name, value]
    AdminConfig.create('J2EEResourceProperty', resourceId, prop)
    print "INFO: addModifyJ2EEResourceProperty: Created property " + propName + ", " + propValue
    #print "DEBUG: END: addModifyJ2EEResourceProperty"
    return

def addModifyProperty(resourceId, props, propName, propValue):
    #print "DEBUG: START: addModifyProperty"
    plist = props[1:len(props)-1].split(" ")
    # Modify if exists, and return
    for prop in plist:
        if(prop != ""):
            curPropName = AdminConfig.showAttribute(prop, 'name')
            curPropValue = AdminConfig.showAttribute(prop, 'value')
            if(curPropName == propName):
                if(curPropValue != propValue):
                    AdminConfig.modify(prop, [['value', propValue]])
                    print "INFO: addModifyProperty: Modified property ",propName,", from ",curPropValue," to ",propValue
                return
    # Since it does not exist, create the property
    name = ['name', propName]
    value = ['value', propValue]
    prop = [name, value]
    AdminConfig.create('Property', resourceId, prop)
    print "INFO: addModifyProperty: Created property " + propName + ", " + propValue
    #print "DEBUG: END: addModifyProperty"
    return