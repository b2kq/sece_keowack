JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/xml.py")
execfile(JYTHON_HOME+"/convertToList.py")
execfile(JYTHON_HOME+"/jvmOperations.py")
execfile(JYTHON_HOME+"/saveOperations.py")

def managerCheck():
   #print "DEBUG: START: managerCheck"
   global DMGR, STANDALONE, MGRNODENAME
   MGRNODENAME = AdminControl.getNode()
   command = "AdminControl.completeObjectName('type=Server,node=" + MGRNODENAME + ",cell=" + cellName + ",*')"
   serverList = eval(command)
   server = serverList.split(lineSep)[0]
   processType = AdminControl.getAttribute(server, 'processType')
   if(processType == "DeploymentManager"):
      print "INFO: managerCheck: Connected to a Deployment Manager"
      DMGR = "TRUE"
      STANDALONE = "FALSE"
   elif(processType == "ManagedProcess" or processType == "NodeAgent"):
      print "INFO: managerCheck: Connected to a NodeAgent"
      print "Exception: managerCheck: This script was not run by connecting to dmgr process"
      raise Exception, "Script raised exception, you are doing something wrong!!!"
   elif(processType == "UnManagedProcess"):
      print "INFO: managerCheck: Connected to an UnManaged Process"
      DMGR = "FALSE"
      STANDALONE = "TRUE"
   #print "DEBUG: END: managerCheck"
   return

def isAppReady(appName):
   #print "DEBUG: START: isAppReady"

   #Initialize return variable
   appIsReady = ""
   #Initialize timeout variable (in seconds)
   to = 2400
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

def createJ2CCF(ra, name, JNDIname, descr):
   #print "DEBUG: START: createJ2CCF"

   name_attr = ["name", name]
   jndi_attr = ["jndiName", JNDIname]
   desc_attr = ["description", descr]
   j2ccfAttrs = [name_attr, jndi_attr, desc_attr]

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
   pfrom = convertToList(pfrom)

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
         ctxRoot = getTagValue(webInfoNode, "ContextRoot")
         postDeployTask = getTagValue(webInfoNode, "PostDeployTask")
         if(postDeployTask == ""):
            postDeployTask = "RIPPLE"

   # Throw an exception if mod-info tags do not exist
   modInfoNode = rootElement.getElementsByTagName("mod-info").item(0)
   if(modInfoNode == None):
      print "Exception: appInstall: Cound not find mod-info node, quitting..."
      raise Exception, "Script raised exception, you are doing something wrong!!!"

   # Find if the app already exists
   found = 0
   appList = AdminApp.list()
   for app in appList.split(lineSep):
      if(app == appName):
         found = 1
         break

   # Install/Update
   if(appType == "ear"):
      if(found):
         print "INFO: appInstall: " + appName + " already exists, updating"
         uOpts = ['-MapWebModToVH', [['.*', '.*', 'default_host']]]
         uOpts += ['-operation update -contents', earFile]
         AdminApp.update(appName, 'app', uOpts)
      else:
         iOpts = ['-appname', appName]
         iOpts += ['-usedefaultbindings']
         iOpts += ["-BindJndiForEJBMessageBinding", [["identityminder_ejb.jar", "SubscriberMessageEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "iam/im/ACT", "iam/im/jms/queue/com.netegrity.ims.msg.queue", ""], ["identityminder_ejb.jar", "ServerCommandsEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "iam/im/ServerCommand", "iam/im/jms/topic/topic/ServerCommandTopic", ""], ["identityminder_ejb.jar", "RuntimeStatusDetailEJB", "identityminder_ejb.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/RuntimeStatusDetailQueue", "iam/im/jms/queue/queue/RuntimeStatusDetailQueue", ""], ["wpServer.jar", "ServerAutomatedActivityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/wpServAutoActActSpec", "queue/wpServAutoActQueue", ""], ["wpServer.jar", "UtilityMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/wpUtilActSpec", "queue/wpUtilQueue", ""], ["wpServer.jar", "EventMDBean", "wpServer.jar,META-INF/ejb-jar.xml", "", "iam/im/jms/wpEventActSpec", "queue/wpEventQueue", ""]]]
         iOpts += ['-MapWebModToVH', [['.*', '.*', 'default_host']]]
         iOpts += ['-deployejb']
         iOpts += ['-verbose']
         print "INFO: appInstall: Deploying " + appName
         print iOpts
         AdminApp.install(earFile, iOpts)
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
   else:
      print "Exception: appInstall: App type must be ear/war, quitting..."
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

      if(STANDALONE == "TRUE"):
         appModules = "+WebSphere:cell=" + cellName + ",node=" + MGRNODENAME + ",server=server1"
      else:
         clusterNameList = webModules.item(i).getElementsByTagName("cluster-name")
         if(clusterNameList.getLength() != 0):
            for j in range(clusterNameList.getLength()):
               clusterName = clusterNameList.item(j).firstChild.nodeValue.strip()
               ppModules = appModules + "+WebSphere:cell=" + cellName + ",cluster=" + clusterName
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

   print "INFO: appInstall: Finished with application deploy for " + appName

   if(SAVE == 1):
      print "INFO: appInstall: Stopping the IDM cluster..."
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

         AdminTask.modifyJSFImplementation(appName, '[-implName "SunRI1.2"]')
         print "INFO: appInstall: Setting JSF implementation to SunRI1.2"

         gmFlag = "false"
         deploy = AdminConfig.getid("/Deployment:" + appName + "/")
         deployedObject = AdminConfig.showAttribute(deploy, "deployedObject")
         modules = AdminConfig.showAttribute(deployedObject, "modules")
         modules = convertToList(modules)
         for module in modules:
            if (len(module) > 0):
               moduleUri = AdminConfig.showAttribute(module, "uri")

               if(re.search(moduleUri, "policyserver.rar") != None):
                  ra = AdminConfig.showAttribute(module, "resourceAdapter")
                  rar_props = AdminConfig.showAttribute(ra, "propertySet")
                  rar_prop = AdminConfig.showAttribute(rar_props, "resourceProperties")
                  cf = createJ2CCF(ra, "iam_im-PolicyServerConnection", "iam/im/rar/nete/rar/PolicyServerConnection", "iam_im Resource adapter for connections to SiteMinder")
                  newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
                  copyProps(rar_prop, newProps)
                  print "INFO: appInstall: Creating connection factories and properties for policyserver.rar"

               if(re.search(moduleUri, "workflow.rar") != None):
                  ra = AdminConfig.showAttribute(module, "resourceAdapter")
                  rar_props = AdminConfig.showAttribute(ra, "propertySet")
                  rar_prop = AdminConfig.showAttribute(rar_props, "resourceProperties")
                  cf = createJ2CCF(ra, "iam_im-Workflow", "iam/im/rar/Workflow", "iam_im Resource adapter for Workflow")
                  newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
                  copyProps(rar_prop, newProps)
                  print "INFO: appInstall: Creating connection factories and properties for workflow.rar"

               if(re.search(moduleUri, "inbound.rar") != None):
                  ra = AdminConfig.showAttribute(module, "resourceAdapter")
                  rar_props = AdminConfig.showAttribute(ra, "propertySet")
                  rar_prop = AdminConfig.showAttribute(rar_props, "resourceProperties")
                  cf = createJ2CCF(ra, "iam_im-IdentityMinderConnection", "iam/im/rar/IdentityMinder", "iam_im Resource adapter for IdentityMinder sessions")
                  newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
                  copyProps(rar_prop, newProps)
                  print "INFO: appInstall: Creating connection factories and properties for inbound.rar"

               if(re.search(moduleUri, "eprovision.rar") != None):
                  ra = AdminConfig.showAttribute(module, "resourceAdapter")
                  rar_props = AdminConfig.showAttribute(ra, "propertySet")
                  rar_prop = AdminConfig.showAttribute(rar_props, "resourceProperties")
                  cf = createJ2CCF(ra, "iam_im-eProvisionServer", "iam/im/rar/nete/eis/eProvisionServer", "iam_im Resource adapter for connections to the eProvision Server")
                  newProps = AdminConfig.create("J2EEResourcePropertySet", cf, [])
                  copyProps(rar_prop, newProps)
                  print "INFO: appInstall: Creating connection factories and properties for eprovision.rar"

               if(re.search(moduleUri, "ca-nim-sm.war") != None):
                  AdminConfig.modify(module, [["startingWeight", 400]])
                  print "INFO: appInstall: Changing ca-nim-sm.war starting weight to 400"

               if(re.search(moduleUri, "wpServer.jar") != None):
                  AdminConfig.modify(module, [["startingWeight", 500]])
                  print "INFO: appInstall: Changing wpServer.jar starting weight to 500"
                  ra = AdminConfig.showAttribute(module, "resourceAdapter")
                  wf_props = AdminConfig.showAttribute(ra, "propertySet")
                  wf_prop = AdminConfig.showAttribute(wf_props, "resourceProperties")
                  wf_prop = convertToList(wf_prop)
                  print "INFO: appInstall: Enable/Disable the wpServer.jar based on the RunGeneralMonitor flag in the ra.xml"
                  for prop in (wf_prop):
                      if (len(prop) > 0):
                          curPropName = AdminConfig.showAttribute(prop, 'name')
                          curPropValue = AdminConfig.showAttribute(prop, 'value')
                          if(curPropName == "RunGeneralMonitor"):
                              gmFlag = curPropValue.lower()
                              print "INFO: appInstall: gmFlag value changed to: " + gmFlag

               if(re.search(moduleUri, "user_console.war") != None):
                  AdminConfig.modify(module, [["startingWeight", 4000]])
                  print "INFO: appInstall: Changing user_console.war starting weight to 4000"

               if(re.search(moduleUri, "taskpersistence_ejb.jar") != None):
                  AdminConfig.modify(module, [["startingWeight", 3500]])
                  print "INFO: appInstall: Changing taskpersistence_ejb.jar starting weight to 3500"


         #Wait for app to be ready to be started
         appIsReady = isAppReady(appName)
         if(appIsReady == "TRUE"):
            print "INFO: appInstall: Application is ready to be started."
         else:
            #Determine timeout value for error message below
            toVal = "20"
            print "ERROR: appInstall: A " + toVal + "-minute timeout has taken place and the application is still not " \
               "ready to be started.  A manual restart of the JVM may be necessary at a later time."
            raise Exception, "Script raised error - app not ready to be started."

         for cName in clusterList:
            clusterOp(cName, postDeployTask)

   #print "DEBUG: END: appInstall"
   return

# Main
try:
   global SAVE
   SAVE = 0
   status = _UNKNOWN_
   if(len(sys.argv) > 1):
      env        = sys.argv[0].upper()
      propFile   = sys.argv[1]

      if(len(sys.argv) > 2):
         if(sys.argv[2].upper() == "SAVE"):
            SAVE = 1
         elif(sys.argv[2].upper() == "NOSAVE"):
            SAVE = 0
      elif(len(sys.argv) == 2):
         SAVE = 0
         print "Defaulting to NOSAVE" + CRLF

      managerCheck()
      domDoc = parseXML(propFile)
      rootElement = domDoc.getDocumentElement()
      appInstall(rootElement)
      status = _SUCCESS_
   else:
      print "EXCEPTION: Missing/invalid input parameters."
      status = _FAILURE_
   #endIf
   print "Status: %s\r\n" % (status)
except:
   typ, val, tb = sys.exc_info()
   if(typ==SystemExit):  raise SystemExit,`val`
   print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
   status = _FAILURE_
   print "Status: %s\r\n" % (status)
