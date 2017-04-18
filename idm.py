def createJ2CCF(ra, name, JNDIname, descr, Comp_Alias):
    #print "DEBUG: START: createJ2CCF"

    name_attr = ["name", name]
    jndi_attr = ["jndiName", JNDIname]
    desc_attr = ["description", descr]
    authdata_attr = ["authDataAlias", Comp_Alias]
    j2ccfAttrs = [name_attr, jndi_attr, desc_attr, authdata_attr]

    j2ccfList = AdminConfig.list('J2CConnectionFactory', ra)
    for j2ccf in j2ccfList.split(lineSep):
        if(AdminConfig.showAttribute(j2ccf, 'name') == name):
            print "INFO: createJ2CCF: J2CCF " + name + " already exists, continuing..."
            return j2ccf

    cf = AdminConfig.create("J2CConnectionFactory", ra, j2ccfAttrs)
    print "INFO: createJ2CCF: Created J2CCF " + name

    #print "DEBUG: END: createJ2CCF"
    return cf

def copyProps(pfrom, to):
    #print "DEBUG: START: copyProps"

    pfrom = pfrom.split('[')
    pfrom = pfrom[1]
    pfrom = pfrom.split(']')
    pfrom = pfrom[0]
    pfrom = pfrom.split(' ')
    for pcount in range(len(pfrom)):
        property = pfrom[pcount]
        if((property == "") | (property == " ")):
            continue
        pName = AdminConfig.showAttribute(property, "name" )
        pValue = AdminConfig.showAttribute(property, "value" )
        pType = AdminConfig.showAttribute(property, "type" )
        print "imsInstall:   Copying property with name:("+pName+") and value:("+pValue+") of type ("+pType+")"
        newpName = ["name", pName]
        newpValue = ["value", pValue]
        newpType = ["type", pType]
        newpAttrs = [newpName, newpValue, newpType]
        AdminConfig.create("J2EEResourceProperty", to, newpAttrs)
        print "INFO: copyProps: Copied property " + pName

    #print "DEBUG: END: copyProps"
    return

def createJAASAuthData(rar_prop, name, desc):
    #print "DEBUG: START: createJAASAuthData"

    rar_prop = rar_prop.split('[')
    rar_prop = rar_prop[1]
    rar_prop = rar_prop.split(']')
    rar_prop = rar_prop[0]
    rar_prop = rar_prop.split(' ')
    for pcount in range(len(rar_prop)):
        property = rar_prop[pcount]
        if((property == "") | (property == " ")):
            continue
        pName = AdminConfig.showAttribute(property, "name" )
        pValue = AdminConfig.showAttribute(property, "value" )
        pType = AdminConfig.showAttribute(property, "type" )
        if(cmp(pName, "UserName") == 0):
            print "imsInstall:   Found property with name:("+pName+") Setting username on alias"
            sm_username = pValue
        if((cmp(pName, "AdminSecret") == 0) | (cmp(pName, "Password") == 0)):
            print "imsInstall:   Found property with name:("+pName+") Setting Password on alias"
            sm_password = pValue
    createJ2CAlias(name, sm_username, sm_password, desc)

    #print "DEBUG: END: createJAASAuthData"
    return

def was_im(found, appName, earFile, scopeS, scopeN):
    #print "DEBUG: START: was_im"

    gmFlag = "false"
    print "INFO: was_im: Defaulting gmFlag to false"

    deploy = AdminConfig.getid("/Deployment:" + appName + "/")
    deployedObject = AdminConfig.showAttribute(deploy, "deployedObject")
    modules = AdminConfig.showAttribute(deployedObject, "modules")
    modules = modules.split('[')
    modules = modules[1]
    modules = modules.split(']')
    modules = modules[0]
    modules = modules.split(' ')

    #Get the gmFlag
    for mc in range(len(modules)):
        module = modules[mc]
        if((module == "") | (module == " ")):
            continue
        moduleUri = AdminConfig.showAttribute(module, "uri")
        if(re.search(moduleUri, "workflow.rar") != None):
            ra = AdminConfig.showAttribute(module, "resourceAdapter")
            wf_props = AdminConfig.showAttribute(ra, "propertySet")
            wf_prop = AdminConfig.showAttribute(wf_props, "resourceProperties")
            wf_prop = wf_prop.split('[')
            wf_prop = wf_prop[1]
            wf_prop = wf_prop.split(']')
            wf_prop = wf_prop[0]
            wf_prop = wf_prop.split('"')
            for propCount in range(len(wf_prop)):
                    prop = wf_prop[propCount]
                    if((prop == "") | (prop == " ")):
                        continue
                    curPropName = AdminConfig.showAttribute(prop, 'name')
                    curPropValue = AdminConfig.showAttribute(prop, 'value')
                    if(curPropName == "RunGeneralMonitor"):
                        gmFlag = curPropValue.lower()
                        print "INFO: was_im: gmFlag value changed to: " + gmFlag

    for mc in range(len(modules)):
        module = modules[mc]
        if((module == "") | (module == " ")):
            continue
        moduleUri = AdminConfig.showAttribute(module, "uri")
        print "INFO: was_im: Working on module: " + moduleUri
        if(re.search(moduleUri, "policyserver.rar") != None):
            ra = AdminConfig.showAttribute(module, "resourceAdapter")
            rar_props = AdminConfig.showAttribute(ra, "propertySet")
            rar_prop = AdminConfig.showAttribute(rar_props, "resourceProperties")
            COMP_ALIAS_SM = "SmAdmin"
            createJAASAuthData(rar_prop, COMP_ALIAS_SM, "SiteMinder Credentials")
            if(appName == "IdentityMinder"):
                cf = createJ2CCF(ra, "PolicyServerConnection", "nete/rar/PolicyServerConnection", "Resource adapter for connections to SiteMinder", COMP_ALIAS_SM)
            else:
                cf = createJ2CCF(ra, "PolicyServerConnection", "iam/im/rar/nete/rar/PolicyServerConnection", "Resource adapter for connections to SiteMinder", COMP_ALIAS_SM)
            newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
            copyProps(rar_prop, newProps)
            print "INFO: was_im: Fixed module policyserver.rar"
        if(re.search(moduleUri, "workflow.rar") != None):
            ra = AdminConfig.showAttribute(module, "resourceAdapter")
            wf_props = AdminConfig.showAttribute(ra, "propertySet")
            wf_prop = AdminConfig.showAttribute(wf_props, "resourceProperties")
            COMP_ALIAS_WF = "WorkflowAdmin"
            createJAASAuthData(wf_prop, COMP_ALIAS_WF, "Workflow Credentials")
            cf = createJ2CCF(ra, "Workflow", "Workflow", "Resource adapter for Workflow", COMP_ALIAS_WF)
            newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
            copyProps(wf_prop, newProps)
            print "INFO: was_im: Fixed module workflow.rar"
        if(re.search(moduleUri, "inbound.rar") != None):
            ra = AdminConfig.showAttribute(module, "resourceAdapter")
            idm_props = AdminConfig.showAttribute(ra, "propertySet")
            idm_prop = AdminConfig.showAttribute(idm_props, "resourceProperties")
            cf = createJ2CCF(ra, "IdentityMinderConnection", "IdentityMinder", "Resource adapter for IdentityMinder sessions", "")
            newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
            copyProps(idm_prop, newProps)
            print "INFO: was_im: Fixed module inbound.rar"
        if(re.search(moduleUri, "eprovision.rar") != None):
            ra = AdminConfig.showAttribute(module, "resourceAdapter")
            eprov_props = AdminConfig.showAttribute(ra, "propertySet")
            eprov_prop = AdminConfig.showAttribute(eprov_props, "resourceProperties")
            cf = createJ2CCF(ra, "eProvisionServer", "nete/eis/eProvisionServer", "Resource adapter for connections to the eProvision Server", "")
            newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
            copyProps(eprov_prop, newProps)
            print "INFO: was_im: Fixed module eprovision.rar"
        if(re.search(moduleUri, "wpServer.jar") != None):
            AdminConfig.modify(module, [["startingWeight", 500]])
            print "INFO: was_im: Fixed weight 500 for module wpServer.jar"
            if(gmFlag == "false"):
                targetMapping = AdminConfig.list("DeploymentTargetMapping", module)
                AdminConfig.modify(targetMapping, [["enable", "false"]])
                print "INFO: was_im: Disabled wpServer.jar, since RunGeneralMonitor is set to false"
        if(re.search(moduleUri, "user_console.war") != None):
            AdminConfig.modify(module, [["startingWeight", 4000]])
            print "INFO: was_im: Fixed weight 4000 for module user_console.war"
        if(re.search(moduleUri, "taskpersistence_ejb.jar") != None):
            AdminConfig.modify(module, [["startingWeight", 3500]])
            print "INFO: was_im: Fixed weight 3500 for module taskpersistence_ejb.jar"

    print "INFO: was_im: Finished with application deploy for " + appName

    if(SAVE == 1):
        saveSync("sync")

    #print "DEBUG: END: was_im"
    return