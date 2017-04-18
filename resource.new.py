def setupNameSpaceString(scopeS, scopeN, ident, nameNS, string):
    #print "DEBUG: START: setupNameSpaceString"
    found = 0
    scopeId = getScopeID(scopeS, scopeN)
    name = ['name', ident]
    nsname = ['nameInNameSpace', nameNS]
    nsstring = ['stringToBind', string]
    attrs = [name, nsname, nsstring]
    strNameList = AdminConfig.list('StringNameSpaceBinding', scopeId)
    for strName in strNameList.split(lineSep):
        if(strName == ""):
            break
        curIdent = AdminConfig.showAttribute(strName, 'name')
        curNSName = AdminConfig.showAttribute(strName, 'nameInNameSpace')
        curNSString = AdminConfig.showAttribute(strName, 'stringToBind')
        if(curIdent == ident):
            found = 1
            if(curNSName != nameNS):
                #AdminConfig.modify(strName, attrs)
                AdminConfig.modify(strName, [['nameInNameSpace', nameNS]])
                print "INFO: setupNameSpaceString: Namespace name for " + ident + " modified from " + curNSName + " to " + nameNS
            if(curNSString != string):
                AdminConfig.modify(strName, [['stringToBind', string]])
                print "INFO: setupNameSpaceString: Namespace string for " + ident + " modified from " + curNSString + " to " + string
    if(found == 0):
        AdminConfig.create('StringNameSpaceBinding', scopeId, attrs)
        print "INFO: setupNameSpaceString: Name space string " + ident + " created"
    #print "DEBUG: END: setupNameSpaceString"
    return

def setupVariable(scopeS, scopeN, varName, varValue):
    #print "DEBUG: START: setupVariable"
    scope = getScopeString(scopeS, scopeN)
    scopeId = getScopeID(scopeS, scopeN)
    name = ['symbolicName', varName]
    value = ['value', varValue]
    attrs = [name, value]
    varMap = AdminConfig.getid(scope + 'VariableMap:/')
    entries = AdminConfig.list('VariableSubstitutionEntry', varMap)
    for entry in entries.split(lineSep):
        if(entry == ""):
            break
        symName = AdminConfig.showAttribute(entry, 'symbolicName')
        if(symName == varName):
            curVal = AdminConfig.showAttribute(entry, 'value')
            if(curVal != varValue):
                AdminConfig.modify(entry, [['value', varValue]])
                print "INFO: setupVariable: Variable " + varName + " exists, modified from " + curVal + " to " + varValue
            return
    AdminConfig.create('VariableSubstitutionEntry', varMap, attrs)
    print "INFO: setupVariable: Variable " + varName + " created, set to " + varValue
    #print "DEBUG: END: setupVariable"
    return

def mailSetup(scopeS, scopeN, mName, mJNDI, mHost, mUID, mPWD, mFROM):
    #print "DEBUG: START: mailSetup"
    scopeId = getScopeID(scopeS, scopeN)
    mailProv = AdminConfig.list('MailProvider', scopeId)
    protocols = AdminConfig.showAttribute(mailProv, 'protocolProviders')
    protocolList = protocols[1:len(protocols)-1].split(" ")
    for protocol in protocolList:
        if(AdminConfig.showAttribute(protocol, 'protocol') == "smtp"):
            transportProto = ['mailTransportProtocol', protocol]
        if(AdminConfig.showAttribute(protocol, 'protocol') == "pop3"):
            storeProto = ['mailStoreProtocol', protocol]
    name = ['name', mName]
    jndi = ['jndiName', mJNDI]
    host = ['mailTransportHost', mHost]
    uid = ['mailTransportUser', mUID]
    pwd = ['mailTransportPassword', mPWD]
    sender = ['mailFrom', mFROM]
    strict = ['strict', 'false']
    debug = ['debug', 'false']
    attrs = [name, jndi, host, uid, pwd, sender, strict, debug, transportProto, storeProto]

    sessList = AdminConfig.list('MailSession', mailProv)
    if(sessList != ""):
        for sess in sessList.split(lineSep):
            curName = AdminConfig.showAttribute(sess, 'name')
            if(curName == mName):
                curJNDI = AdminConfig.showAttribute(sess, 'jndiName')
                if(curJNDI != mJNDI):
                    AdminConfig.modify(sess, [['jndiName', mJNDI]])
                    print "INFO: mailSetup: Modified jndiName for " + mName + " from " + curJNDI + " to " + mJNDI
                curTHost = AdminConfig.showAttribute(sess, 'mailTransportHost')
                if(curTHost != mHost):
                    AdminConfig.modify(sess, [['mailTransportHost', mHost]])
                    print "INFO: mailSetup: Modified mailTransportHost for " + mName + " from " + curTHost + " to " + mHost
                curFrom = AdminConfig.showAttribute(sess, 'mailFrom')
                if(curFrom != mFROM):
                    AdminConfig.modify(sess, [['mailFrom', mFROM]])
                    print "INFO: mailSetup: Modified mailFrom for " + mName + " from " + curFrom + " to " + mFROM
                return

    AdminConfig.create('MailSession', mailProv, attrs)
    print "INFO: mailSetup: Mail session " + mJNDI + " created"
    #print "DEBUG: END: mailSetup"
    return

def setupURL(scopeS, scopeN, uName, uJNDI, uSpec, uDesc):
    #print "DEBUG: START: setupURL"
    scopeId = getScopeID(scopeS, scopeN)
    name = ['name', uName]
    jndi = ['jndiName', uJNDI]
    spec = ['spec', uSpec]
    desc = ['description', uDesc]
    attrs = [name, jndi, spec, desc]

    urlProvList = AdminConfig.list('URLProvider', scopeId)
    for urlProv in urlProvList.split(lineSep):
        if(AdminConfig.showAttribute(urlProv, 'name') == "Default URL Provider"):
            urlList = AdminConfig.list('URL', urlProv)
            if(urlList != ""):
                for url in urlList.split(lineSep):
                    #curname = AdminConfig.showAttribute(url, 'name')
                    curjndi = AdminConfig.showAttribute(url, 'jndiName')
                    curspec = AdminConfig.showAttribute(url, 'spec')
                    if(curjndi == uJNDI):
                        if(curspec != uSpec):
                            AdminConfig.modify(url, [['spec', uSpec]])
                            print "INFO: setupURL: URL " + uJNDI + " specfication modified from " + curspec + " to " + uSpec
                        return
            AdminConfig.create('URL', urlProv, attrs)
    print "INFO: setupURL: URL " + uJNDI + " created"
    #print "DEBUG: END: setupURL"
    return

def setupVHAlias(vhId, aliasName, aliasPort):
    #print "DEBUG: START: setupVHAlias"
    hostname = ['hostname', aliasName]
    port = ['port', aliasPort]
    attrs = [hostname, port]
    aliasList = AdminConfig.list('HostAlias', vhId)
    for alias in aliasList.split(lineSep):
        if(alias == ""):
            break
        host = AdminConfig.showAttribute(alias, 'hostname')
        port = AdminConfig.showAttribute(alias, 'port')
        if((host.upper() == aliasName.upper()) and (port == aliasPort)):
            #print "INFO: setupVHAlias: Virtual host alias " + aliasName + ", " + aliasPort + " exists"
            return
    AdminConfig.create('HostAlias', vhId, attrs)
    print "INFO: setupVHAlias: Virtual host alias " + aliasName + ", " + aliasPort + " created"
    #print "DEBUG: END: setupVHAlias"
    return

def setupVirtualHost(vhName):
    #print "DEBUG: START: setupVirtualHost"
    name = ['name', vhName]
    vhId = AdminConfig.getid('/VirtualHost:' + vhName)
    #if(vhId == ""):
    #    vhId = AdminConfig.create('VirtualHost', cellId, [name])
    #    print "INFO: setupVirtualHost: Virtual host " + vhName + " created"
    #else:
    #    print "INFO: setupVirtualHost: Virtual host " + vhName + " exists"
    #print "DEBUG: END: setupVirtualHost"
    return vhId