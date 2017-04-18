#This function 'waits' up to 20 minutes (40 minutes for ClaimCenter)and determines if app is ready to be started
def isAppReady(appName):
    #print "DEBUG: START: isAppReady"

    #Initialize return variable
    appIsReady = ""

    #Initialize timeout variable (in seconds) - ClaimCenter requires special handling
    if(appName == "ClaimCenter"):
        to = 2400
    else:
        to = 1200

    #Record current time (in seconds)
    currTime = time.time()

    #Empty loop to delay while the application is not ready to be started
    print "INFO: isAppReady: Waiting for the application to be ready to be started..."
    while(AdminApp.isAppReady(appName).upper() == "FALSE"):
        #5-second delay
        time.sleep(5)

        #Set a 20 (or 40) minute timeout for the loop
        if(time.time() - currTime >= to):
            break
        continue

    #Once out of the loop, check if app is ready
    if(AdminApp.isAppReady(appName).upper() == "TRUE"):
        appIsReady = "TRUE"
    else:
        appIsReady = "FALSE"

    #print "DEBUG: END: isAppReady"
    return appIsReady

def appendToClusterList(clusterList, appendString):
    #print "DEBUG: START: appendToClusterList"

    found = 0
    for listItem in clusterList:
        if(listItem == appendString):
            found = 1
    if(found == 0):
        clusterList.append(appendString)

    #print "DEBUG: END: appendToClusterList"
    return clusterList

def appInstall(rootElement):
    #print "DEBUG: START: appInstall"

    # This array is used to hold multiple cluster names for an app if present
    # It will be used to issue ripple/restart after the deploy
    clusterList = []

    # This var will be used to figure out whether the deploy type is ear/war
    appType = ""

    # Get the EAR file's full path, name, etc.
    earInfoNode = rootElement.getElementsByTagName("ear-info").item(0)
    if(earInfoNode != None):
        appType = "ear"
        appName = getTagValue(earInfoNode, "app-name")
        earName = getTagValue(earInfoNode, "ear-name")
        #earLoc = getTagValue(earInfoNode, "ear-location")
        #earFile = earLoc + "/" + earName
        earFile = "/promotion/staging/" + sys.argv[0] + "/" + earName
        postDeployTask = getTagValue(earInfoNode, "PostDeployTask")
        if(postDeployTask == ""):
            postDeployTask = "RIPPLE"
    else:
        # Get war module info if available
        webInfoNode = rootElement.getElementsByTagName("web").item(0)
        if webInfoNode == None: 
            webInfoNode = rootElement.getElementsByTagName("war").item(0)
        if(webInfoNode != None):
            appType = "war"
            appName = getTagValue(webInfoNode, "display-name")
            warName = getTagValue(webInfoNode, "war-file-name")
            warFile = "/promotion/expand/" + sys.argv[0] + "/" + appName + "/" + warName
            #warFile = "/promotion/staging/" + sys.argv[0] + "/" + warName
            ctxRoot = getTagValue(webInfoNode, "ContextRoot")
            postDeployTask = getTagValue(webInfoNode, "PostDeployTask")
            if(postDeployTask == ""):
                postDeployTask = "RIPPLE"    
            
    # Check if app type is portlet
    #artifactTypeNode = rootElement.getElementsByTagName("ArtifactType").item(0)
    #if(artifactTypeNode != None):
    artifactType = getTagValue(rootElement, "ArtifactType")
    if(artifactType.upper() == "PORTLET"):
        appType = "portlet"
        postDeployTask = "fullresync"

    # Throw an exception if mod-info tags do not exist
    modInfoNode = rootElement.getElementsByTagName("mod-info").item(0)
    if(modInfoNode == None):
        print "Exception: appInstall: Cound not find mod-info node, quitting..."
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    # Find if the app already exists or not
    found = 0
    appList = AdminApp.list()
    for app in appList.split(lineSep):
        if(app == appName):
            found = 1
            break

    # Install/update
    if(appType == "ear"):
        if(found):
            print "INFO: appInstall: " + appName + " already exists, updating"
            uOpts = ['-MapWebModToVH', [['.*', '.*', 'default_host']]]
            uOpts += ['-operation update -contents', earFile]
            AdminApp.update(appName, 'app', uOpts)
        else:
            iOpts = ['-appname', appName]
            if(appName == "Netegrity IdentityMinder"):
                iOpts = ['-usedefaultbindings']
                iOpts += ["-BindJndiForEJBMessageBinding", [["identityminder_ejb.jar", "SubscriberMessageEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "ACT", "com.netegrity.ims.msg.queue", ""], ["identityminder_ejb.jar", "ServerCommandsEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "ServerCommand", "com/netegrity/idm/ServerCommandTopic", ""], ["WorkPoint Server", "ServerAutomatedActivityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "jms/wpServAutoActActSpec", "queue/wpServAutoActQueue", ""], ["WorkPoint Server", "UtilityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "jms/wpUtilActSpec", "queue/wpUtilQueue", ""]]]
            if(appName == "IdentityMinder"):
                iOpts = ['-usedefaultbindings']
                iOpts += ["-BindJndiForEJBMessageBinding", [["identityminder_ejb.jar", "SubscriberMessageEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "ACT", "com.netegrity.ims.msg.queue", ""], ["identityminder_ejb.jar", "ServerCommandsEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "ServerCommand", "topic/ServerCommandTopic", ""], ["identityminder_ejb.jar", "RuntimeStatusDetailEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "jms/RuntimeStatusDetailQueue", "queue/RuntimeStatusDetailQueue", ""], ["WorkPoint Server", "ServerAutomatedActivityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "jms/wpServAutoActActSpec", "queue/wpServAutoActQueue", ""], ["WorkPoint Server", "UtilityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "jms/wpUtilActSpec", "queue/wpUtilQueue", ""], ["WorkPoint Server", "EventMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "jms/wpEventActSpec", "queue/wpEventQueue", ""]]]
            if(appName == "iam_im"):
                iOpts = ['-usedefaultbindings']
                iOpts += ["-BindJndiForEJBMessageBinding", [["identityminder_ejb.jar", "SubscriberMessageEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "iam/im/ACT", "iam/im/jms/queue/com.netegrity.ims.msg.queue", ""], ["identityminder_ejb.jar", "ServerCommandsEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "iam/im/ServerCommand", "iam/im/jms/topic/topic/ServerCommandTopic", ""], ["identityminder_ejb.jar", "RuntimeStatusDetailEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/RuntimeStatusDetailQueue", "iam/im/jms/queue/queue/wpServAutoActQueue", ""], ["WorkPoint Server", "ServerAutomatedActivityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/wpServAutoActActSpec", "iam/im/jms/queue/queue/wpServAutoActQueue", ""], ["WorkPoint Server", "UtilityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/wpUtilActSpec", "iam/im/jms/queue/queue/wpUtilQueue", ""], ["WorkPoint Server", "EventMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/wpEventActSpec", "iam/im/jms/queue/queue/wpEventQueue", ""]]]
            iOpts += ['-MapWebModToVH', [['.*', '.*', 'default_host']]]
           
            print "INFO: appInstall: Deploying " + appName
            print iOpts
            AdminApp.install(earFile, iOpts)
        #Etien's changes -- fetching and setting Security Role-to-Group Mapping pairs
        #for CommFW security (ExceedJ CommFW requires this)
        secRolToGrpMaps = earInfoNode.getElementsByTagName("SecurityRoleToGroupMapping")
        for e in range(secRolToGrpMaps.getLength()):
            role = getTagValue(secRolToGrpMaps.item(e), "Role")
            mappedGroup = getTagValue(secRolToGrpMaps.item(e), "MappedGroup")
            print "INFO: appInstall: Setting security role-to-group mapping for " + role + " to " + mappedGroup
            AdminApp.edit(appName, '[ -MapRolesToUsers [[ ' + role + ' AppDeploymentOption.No AppDeploymentOption.No "" ' + mappedGroup + ' AppDeploymentOption.No "" group:FederatedRealm/' + mappedGroup + ' ]]]' )
        #End Etien's changes
    elif(appType == "war"):
        if(found):
            uOpts =  ['-operation', 'update']
            uOpts += ['-contents', warFile]
            uOpts += ['-contextroot', ctxRoot]
            print "INFO: war: " + appName + " already exists, updating..."
            AdminApp.update(appName, 'app', uOpts)
        else:
            iOpts =  ['-nopreCompileJSPs', '-nouseMetaDataFromBinary', '-nodeployejb']
            iOpts += ['-appname', appName]
            iOpts += ['-contextroot', ctxRoot]
            print "INFO: war: Deploying " + appName
            AdminApp.install(warFile, iOpts)
    elif(appType == "portlet"):
        print "INFO: appInstall: No update/deploy task for Portlet type"
    else:
        print "Exception: appInstall: App type must be ear/war/portlet, quitting..."
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    # Lookup server name, cluster name for an ear file in the ApplicationServer node
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
                scopeS = clusterName
                scopeN = None

    # Fix the EJB module mappings
    ejbModules = modInfoNode.getElementsByTagName("ejb")
    for i in range(ejbModules.getLength()):
        appModules = ""
        ejbFileName = getTagValue(ejbModules.item(i), "ejb-file-name")
        ejbDispName = getTagValue(ejbModules.item(i), "display-name")
        if(STANDALONE == "TRUE"):
            appModules = "+WebSphere:cell=" + cellName + ",node=" + MGRNODENAME + ",server=server1"
        else:
            clusterNameList = ejbModules.item(i).getElementsByTagName("cluster-name")
            if(clusterNameList.getLength() != 0):
                for j in range(clusterNameList.getLength()):
                    clusterName = clusterNameList.item(j).firstChild.nodeValue.strip()
                    appModules = appModules + "+WebSphere:cell=" + cellName + ",cluster=" + clusterName
                    clusterList = appendToClusterList(clusterList, clusterName)
            else:
                appModules = "+WebSphere:cell=" + cellName + ",cluster=" + scopeS
                clusterList = appendToClusterList(clusterList, scopeS)
        moduleURI = ejbFileName + ",META-INF/ejb-jar.xml"
        appModules = appModules[1:len(appModules)]
        modOptions = [[ejbDispName, moduleURI, appModules]]
        modOptionList = [ "-MapModulesToServers", modOptions]
        AdminApp.edit(appName, modOptionList)
        print "INFO: appInstall: Mapped module " + ejbFileName + " to " + appModules

    # Fix RAR module mappings
    rarModules = modInfoNode.getElementsByTagName("rar")
    for i in range(rarModules.getLength()):
        appModules = ""
        rarFileName = getTagValue(rarModules.item(i), "rar-file-name")
        rarDispName = getTagValue(rarModules.item(i), "display-name")
        if(STANDALONE == "TRUE"):
            appModules = "+WebSphere:cell=" + cellName + ",node=" + MGRNODENAME + ",server=server1"
        else:
            clusterNameList = rarModules.item(i).getElementsByTagName("cluster-name")
            if(clusterNameList.getLength() != 0):
                for j in range(clusterNameList.getLength()):
                    clusterName = clusterNameList.item(j).firstChild.nodeValue.strip()
                    appModules = appModules + "+WebSphere:cell=" + cellName + ",cluster=" + clusterName
                    clusterList = appendToClusterList(clusterList, clusterName)
            else:
                appModules = "+WebSphere:cell=" + cellName + ",cluster=" + scopeS
                clusterList = appendToClusterList(clusterList, scopeS)
        moduleURI = rarFileName + ",META-INF/ra.xml"
        appModules = appModules[1:len(appModules)]
        modOptions = [[rarDispName, moduleURI, appModules]]
        modOptionList = [ "-MapModulesToServers", modOptions]
        AdminApp.edit(appName, modOptionList)
        print "INFO: appInstall: Mapped module " + rarFileName + " to " + appModules

    # Fix the WEB module and virtual hosts mappings, and CLASSLOADER MODE if necessary
    webModules = modInfoNode.getElementsByTagName("web")
    if webModules.item(0) == None: 
		webModules = modInfoNode.getElementsByTagName("war")
		scopeS = getTagValue(rootElement.getElementsByTagName("Cluster").item(0),'ClusterName')
		print "INFO: cluster " + scopeS
    for i in range(webModules.getLength()):
        appModules = ""
        webFileName = getTagValue(webModules.item(i), "war-file-name")
        webDispName = getTagValue(webModules.item(i), "display-name")

        #Etien's changes -- fetching environment entry name/value pairs 
        #to allow for Web Module environment entry specification (ExceedJ CommFW requires this)
        envEntries = webModules.item(i).getElementsByTagName("EnvironmentEntry")
        for e in range(envEntries.getLength()):  
            envEntryName = getTagValue(envEntries.item(e), "Name")
            envEntryValue = getTagValue(envEntries.item(e), "Value")
            print "INFO: appInstall: Setting web module environment entry value for " + envEntryName + " to " + envEntryValue
            AdminApp.edit(appName, '[ -MapEnvEntryForWebMod [[' + webDispName + " " + webFileName + ',WEB-INF/web.xml ' + envEntryName + ' String "" ' + envEntryValue + ']]]')            
        #End Etien's changes

        if(STANDALONE == "TRUE"):
            appModules = "+WebSphere:cell=" + cellName + ",node=" + MGRNODENAME + ",server=server1"
        else:
            clusterNameList = webModules.item(i).getElementsByTagName("cluster-name")
            if(clusterNameList.getLength() != 0):
                for j in range(clusterNameList.getLength()):
                    clusterName = clusterNameList.item(j).firstChild.nodeValue.strip()
                    appModules = appModules + "+WebSphere:cell=" + cellName + ",cluster=" + clusterName
                    clusterList = appendToClusterList(clusterList, clusterName)
            else:
                appModules = "+WebSphere:cell=" + cellName + ",cluster=" + scopeS
                clusterList = appendToClusterList(clusterList, scopeS)
        webSrvNameList = webModules.item(i).getElementsByTagName("server-name")
        for j in range(webSrvNameList.getLength()):
            webServName = webSrvNameList.item(j).firstChild.nodeValue.strip()
            serverList = AdminTask.listServers('[-serverType WEB_SERVER]')
            webServerNodeList = [None]
            for webItem in serverList.split(lineSep):
                webItemName = AdminConfig.showAttribute(webItem, "name")
                if(webItemName == webServName):
                    nodeName = webItem.split("/")[3]
                    webServerNodeList.append(nodeName)
            webServerNodeList.remove(None)
            for nodeName in webServerNodeList:
                appModules = appModules + "+WebSphere:cell=" + cellName + ",node=" + nodeName + ",server=" + webServName
        moduleURI = webFileName + ",WEB-INF/web.xml"
        appModules = appModules[1:len(appModules)]
        modOptions = [[webDispName, moduleURI, appModules]]
        modOptionList = ["-MapModulesToServers", modOptions]
        AdminApp.edit(appName, modOptionList)
        print "INFO: appInstall: Mapped module " + webFileName + " to " + appModules
        vHostName = getTagValue(webModules.item(i), "virtual-host")
        vHostOptions = [[webDispName, moduleURI, vHostName]]
        vHostOptionsList = ["-MapWebModToVH", vHostOptions]
        AdminApp.edit(appName, vHostOptionsList)
        print "INFO: appInstall: Mapped module " + webFileName + " to " + vHostName
        classLdrMode = getTagValue(webModules.item(i), "ClassLoaderMode")
        if((classLdrMode.upper() == "PARENT_FIRST") or (classLdrMode.upper() == "PARENT_LAST")):
            deployment = AdminConfig.getid('/Deployment:' + appName + '/')
            depObject = AdminConfig.showAttribute(deployment, 'deployedObject')
            modules = AdminConfig.showAttribute(depObject, 'modules')
            modules = modules[1:len(modules)-1].split(" ")
            for module in modules:
                modURI = AdminConfig.showAttribute(module, 'uri')
                if(modURI == webFileName):
                    AdminConfig.modify(module, [['classloaderMode', classLdrMode.upper()]])
                    print "INFO: appInstall: Changed module " + webFileName + " class loader mode to " + classLdrMode.upper()

    # Disable class reload scanning
    AdminApp.edit(appName, "-reloadEnabled true -reloadInterval 0")
    print "INFO: appInstall: Disabled file update scanning for " + appName

    print "INFO: appInstall: Finished with application deploy for " + appName

    if(SAVE == 1):
        # Stop cluster if app is IDM
        if((appName == "IdentityMinder") | (appName == "iam_im") | (appName == "Netegrity IdentityMinder")):
            print "INFO: was_im: Stopping the IDM cluster"
            clusterOp(clusterName, "STOP")

        if(postDeployTask == "None"):
            print "INFO: appInstall: Running postDeployTask saveSync"
            saveSync("sync")
        elif(postDeployTask == "fullresync"):
            print "INFO: appInstall: Running postDeployTask saveFullSync"
            saveSync("fullresync")
        else:
            print "INFO: appInstall: Running postDeployTasks saveSync and " + postDeployTask
            saveSync("sync")

            if((appName == "IdentityMinder") | (appName == "iam_im") | (appName == "Netegrity IdentityMinder")):
                was_im(found, appName, earFile, scopeS, scopeN)

            #Wait for app to be ready to be started
            appIsReady = isAppReady(appName)
            if(appIsReady == "TRUE"):
                print "INFO: appInstall: Application is ready to be started."
            else:
                #Determine timeout value for error message below
                if(appName == "ClaimCenter"):
                    toVal = "40"
                else:
                    toVal = "20"

                #Simply display warning until fully tested, then use the commented-out lines below.
                #print "WARNING: appInstall: A 5-minute timeout has taken place and the application is still not " \
                #      "ready to be started.  A manual restart of the JVM may be necessary at a later time."
                print "ERROR: appInstall: A " + toVal + "-minute timeout has taken place and the application is still not " \
                      "ready to be started.  A manual restart of the JVM may be necessary at a later time."
                raise Exception, "Script raised error - app not ready to be started."

            for cName in clusterList:
                clusterOp(cName, postDeployTask)

    #print "DEBUG: END: appInstall"
    return