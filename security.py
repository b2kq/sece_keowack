def createJ2CAlias(alias, uid, pwd, desc):
    #print "DEBUG: START: createJ2CAlias"
    found = 0
    aliasProp = ['alias', alias]
    uidProp = ['userId', uid]
    pwdProp = ['password', pwd]
    desc = desc + " "
    descProp = ['description', desc]
    attrs = [aliasProp, uidProp, pwdProp, descProp]
    jaasAuthList = AdminConfig.list('JAASAuthData')
    for jaasAuth in jaasAuthList.split(lineSep):
        if(jaasAuth == ""):
            break
        authAlias = AdminConfig.showAttribute(jaasAuth, 'alias')
        manager = AdminControl.getNode()
        if((authAlias == alias) or (authAlias == (manager + '/' + alias))):
            found = 1
            curUID = AdminConfig.showAttribute(jaasAuth, 'userId')
            curPWD = AdminConfig.showAttribute(jaasAuth, 'password')
            #AdminConfig.modify(jaasAuth, [uidProp])
            #if((pwd != "") | (pwd != None)):
            #    AdminConfig.modify(jaasAuth, [pwdProp])
            #AdminConfig.modify(jaasAuth, [descProp])
            #print "INFO: createJ2CAlias: J2C auth alias " + alias + " exists, modified"
    if(found == 0):
        security = AdminConfig.getid('/Cell:' + cellName + '/Security:/')
        AdminConfig.create('JAASAuthData', security, attrs)
        print "INFO: createJ2CAlias: J2C auth alias " + alias + " created"
    #print "DEBUG: END: createJ2CAlias"
    return