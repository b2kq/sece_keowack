def createDatabaseProvider(scopeS, scopeN, dbType, provName):
    #print "DEBUG: START: createDatabaseProvider"

    name = ['name', provName]
    attrs = [name]

    if(dbType == 'DB2'):
        tmplName = "DB2 Universal JDBC Driver Provider Only"
    elif(dbType == 'Oracle'):
        tmplName = "Oracle JDBC Driver Provider Only"
    elif(dbType == 'SQL Server'):
        # Changing SQL Server to use sqljdbc4.jar for all apps
        # assuming only WAS 7 builds forward 3/27/21012 - Dev D
        # Charles Smith 4/20/09 - Modified template name for WebSphere 6.1 support for this driver was added in release 6.1.0.15
        tmplName = "Microsoft SQL Server JDBC Driver Provider Only"
        driverPath = ['classpath', "${MICROSOFT_JDBC_DRIVER_PATH}/sqljdbc4.jar"]
        attrs = [name, driverPath]
    #elif(dbType == 'SQL Server Version 7'):
    #    # Charles Smith 4/20/09 - This elif section added template name and classpath for WebSphere 7.0 support for this driver was added in release 6.1.0.15
    #    tmplName = "Microsoft SQL Server JDBC Driver Provider Only"
    #    driverPath = ['classpath', "${MICROSOFT_JDBC_DRIVER_PATH}/sqljdbc4.jar"]
    #    attrs = [name, driverPath]
    else:
        print "Exception: createDatabaseProvider: Database type " + dbType + " not supported"
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    tmplList = AdminConfig.listTemplates('JDBCProvider', tmplName)
    if(tmplList == ""):
        print "Exception: createDatabaseProvider: Could not find a JDBC Provider Template of type " + tmplName
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    for tmplId in tmplList.split(lineSep):
        curName = AdminConfig.showAttribute(tmplId, 'name')
        if(curName == tmplName):
            break

    scopeId = getScopeID(scopeS, scopeN)
    provList = AdminConfig.list('JDBCProvider', scopeId)
    for provId in provList.split(lineSep):
        if(provList != ""):
            name = AdminConfig.showAttribute(provId, "name")
            if(provName == name):
                break
            else:
                provId = ""

    if((provId == "") or (provId == None)):
        provId = AdminConfig.createUsingTemplate('JDBCProvider', scopeId, attrs, tmplId)
        print "INFO: createDatabaseProvider: Created provider for " + provName
    #else:
    #    print "INFO: createDatabaseProvider: Provider " + provName + " exists, continuing"

    #print "DEBUG: END: createDatabaseProvider"
    return provId

def createDataSource(scopeS, scopeN, dbType, provId, dsName, dsJNDI, dsCompAlias, dsStmtCache, dsConnTest):
    #print "DEBUG: START: createDataSource"

    name = ['name', dsName]
    jndi = ['jndiName', dsJNDI]
    compAuth = ['authDataAlias', ""]
    jaasAuthList = AdminConfig.list('JAASAuthData')
    if(jaasAuthList != ""):
        for jaasAuth in jaasAuthList.split(lineSep):
            authAlias = AdminConfig.showAttribute(jaasAuth, 'alias')
            manager = AdminControl.getNode()
            if((authAlias == dsCompAlias) or (authAlias == (manager + '/' + dsCompAlias))):
                compAuth = ['authDataAlias', authAlias]
                break
    if(compAuth[1] == ""):
        print "WARNING: createDataSource: No component authentication alias match found for " + dsName + ", continuing..."
    statementCacheSizeAttr = ["statementCacheSize", dsStmtCache]
    if(dbType == 'Oracle'):
        helperClass = ['datasourceHelperClassname', 'com.ibm.websphere.rsadapter.Oracle11gDataStoreHelper']
        attrs = [name, jndi, compAuth, statementCacheSizeAttr, helperClass]
    else:
        attrs = [name, jndi, compAuth, statementCacheSizeAttr]

    if((dsConnTest.upper() == "TRUE") or (dsConnTest.upper() == "YES")):
        testConn = 'true'
    elif((dsConnTest.upper() == "FALSE") or (dsConnTest.upper() == "NO")):
        testConn = 'false'
    else:
        print "Exception: createDataSource: PretestConnectionEnable can only be TRUE/FALSE/YES/NO"
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    scope = getScopeString(scopeS, scopeN)
    provName = AdminConfig.showAttribute(provId, 'name')
    dsId = AdminConfig.getid(scope + 'JDBCProvider:' + provName + '/DataSource:' + dsName + '/')
    if(dsId == ""):
        if(dbType == 'DB2'):
            tmplName = "DB2 Universal JDBC Driver DataSource"
        elif(dbType == 'Oracle'):
            tmplName = "Oracle JDBC Driver DataSource"
        elif(dbType == 'SQL Server'):
            # Charles Smith 4/20/09 - Modified template name for WebSphere 7.0 support for this driver was added in release 6.1.0.15
            tmplName = "Microsoft SQL Server JDBC Driver - DataSource"
        elif(dbType == 'SQL Server Version 7'):
            # Charles Smith 4/20/09 - Modified template name for WebSphere 7.0 support for this driver was added in release 6.1.0.15
            tmplName = "Microsoft SQL Server JDBC Driver - DataSource"
        else:
            print "Exception: createDataSource: Database type " + dbType + " not supported"
            raise Exception, "Script raised exception, you are doing something wrong!!!"
        tmplList = AdminConfig.listTemplates('DataSource', tmplName)
        for tmplId in tmplList.split(lineSep):
            curName = AdminConfig.showAttribute(tmplId, 'name')
            if(curName == tmplName):
                break
        dsId = AdminConfig.createUsingTemplate('DataSource', provId, attrs, tmplId)
        print "INFO: createDataSource: Created datasource " + dsName        
    else:
        curJNDI = AdminConfig.showAttribute(dsId, 'jndiName')
        if(curJNDI != dsJNDI):
            AdminConfig.modify(dsId, [['jndiName', dsJNDI]])
            print "INFO: createDataSource: Modified JNDI name for datasource " + dsName + " from " + curJNDI + " to " + dsJNDI
        curAuthAlias = AdminConfig.showAttribute(dsId, 'authDataAlias')
        if(curAuthAlias != dsCompAlias):
            AdminConfig.modify(dsId, [['authDataAlias', dsCompAlias]])
            print "INFO: createDataSource: Modified auth alias for datasource " + dsName + " from " + curAuthAlias + " to " + dsCompAlias
        curStmtCache = AdminConfig.showAttribute(dsId, 'statementCacheSize')
        if(curStmtCache != dsStmtCache):
            AdminConfig.modify(dsId, [['statementCacheSize', dsStmtCache]])
            print "INFO: createDataSource: Modified db statement cache size for datasource " + dsName + " from " + curStmtCache + " to " + dsStmtCache
        connPoolId = AdminConfig.showAttribute(dsId, 'connectionPool')
        curTestConn = AdminConfig.showAttribute(connPoolId, 'testConnection')
        if(curTestConn != testConn):
            AdminConfig.modify(connPoolId, [['testConnection', testConn]])
            print "INFO: createDataSource: Modified db connection test for datasource " + dsName + " from " + curTestConn + " to " + testConn

    #print "DEBUG: END: createDataSource"
    return dsId

def modifyDSProperty(dsId, propName, propValue):
    #print "DEBUG: START: modifyDSProperty"
    psId = AdminConfig.showAttribute(dsId, 'propertySet')
    if(psId == ""):
        print "Exception: modifyDSProperty: Resource ID passed is bad"
        raise Exception, "Script raised exception, you are doing something wrong!!!"
    props = AdminConfig.showAttribute(psId, 'resourceProperties')
    # Call the function in common.py
    modifyProperty(dsId, props, propName, propValue)
    #print "DEBUG: END: modifyDSProperty"
    return