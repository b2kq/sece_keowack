#  To use:   functions called by mainV2.py
#  State:	work in progress, major revision first version
#  Purpose:  replacing application.py, attempt not to change prior functions
#	There is probably an existing working configuration, but may not be
#	A new build or deploy is being sumitted, this configuration is the target
#	Only the differences will be applied, we are trying to minimize work the 
#	deployment manager needs to do.
#  Assumptions:
#	x)  all dependancies already defined

codeVersion = '1.99'
printInfoLine('applicationV2.py ' + codeVersion)
#  Programming notes:
#	x)  continueing debug functions from mainV2.py
#	x)  omega is sumbited XML
#	x)  alpha is configuration as queried from existing configuration
#	x)  delta changes to make beta into alpha

###def appendToClusterList(clusterList, appendString):
###	#print "DEBUG: START: appendToClusterList"
###
###	found = 0
###	for listItem in clusterList:
###		if(listItem == appendString):
###			found = 1
###	if(found == 0):
###		clusterList.append(appendString)
###
###	#print "DEBUG: END: appendToClusterList"
###	return clusterList

def appInstall(wasElements):
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	processStage.append('Function appInstall( wasElements )')
	printDebugLine('start')
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	#	Assumptions for our (Unitrin) environemnt:
	#		1)  Always clustered environment, no stand alones
	#		2)  Netegrity Identity Manager has a fixed configuration.
	
###	#print "DEBUG: START: appInstall"
###
###	CLUSTERED = "TRUE"
###	clusterList = []
###
###	# Lookup server name, cluster name
###	appSvrNode = rootElement.getElementsByTagName("ApplicationServer").item(0)
###	if(appSvrNode != None):
###		serverName = getTagValue(appSvrNode, 'ServerName')
###		clusterName = getTagValue(appSvrNode, 'ClusterName')
###
###		# Check if both ServerName and ClusterName tags are present
###		if(((serverName == "") & (clusterName == "")) | ((serverName != "") & (clusterName != ""))):
###			print "ERROR: configJVM: Specify either a <ServerName> or a <ClusterName>"
###			raise Exception, "Script raised exception, you are doing something wrong!!!"
###
###		# Set the appropriate scope
###		if(DMGR == "TRUE"):
###			if(serverName == ""):
###				CLUSTERED = "TRUE"
###				scopeS = clusterName
###				scopeN = None
###			else:
###				CLUSTERED = "FALSE"
###		else:
###			CLUSTERED = "FALSE"
###
	# CLUSTERED set in function managerCheck in mainV2
	#earName = appName + '.ear'
	#earFile = '/promotion/staging/' + environment + '/' + earName
###	# Get the EAR file's full path, name, etc.
###	earInfoNode = rootElement.getElementsByTagName("ear-info").item(0)
###	if(earInfoNode != None):
###		appName = getTagValue(earInfoNode, "app-name")
###		earName = getTagValue(earInfoNode, "ear-name")
###		earLoc = getTagValue(earInfoNode, "ear-location")
###		#earFile = earLoc + "/" + earName
###		earFile = "/promotion/staging/" + sys.argv[0] + "/" + earName
###		postDeployTask = getTagValue(earInfoNode, "PostDeployTask")
###		if(postDeployTask == ""):
###			postDeployTask = "RIPPLE"
###	else:
###		print "ERROR: appInstall: Cound not find ear-info node, quitting..."
###		raise Exception, "Script raised exception, you are doing something wrong!!!"
###
###	# Throw an exception if mod-info tags do not exist
###	modInfoNode = rootElement.getElementsByTagName("mod-info").item(0)
###	if(earInfoNode == None):
###		print "ERROR: appInstall: Cound not find mod-info node, quitting..."
###		raise Exception, "Script raised exception, you are doing something wrong!!!"
###
###	# Get the list of installed apps
###	appList = AdminApp.list()
###
###	# Find if the app already exists or not
###	found = 0
###	for app in appList.split(lineSep):
###		if(app == appName):
###			found = 1
###			break
###
###	# Install/update
###	if(found == 0):
	appName = rootElement.getElementsByTagName("ear-info").item(0)
	if (rootElement.getElementsByTagName("ear-info").item(0) != None):
		appName = getTagValue(earInfoNode, "app-name")
		if appName in AdminApp.list().splitlines():
			printInfoLine(' '.join('updating', appName, 'with', earFile))
			AdminApp.update( appName, 'app', '[-operation update -contents ' + earFile + ']' )
		else:
			options = [ '-appname', appName ]
			if appName == "Netegrity IdentityMinder":
				#options = ['-deployejb', '-preCompileJSPs', '-usedefaultbindings']
				# supOptions combines multiple lists into a list as required by IDM
				subOptions = []
				subOptions.append(["identityminder_ejb.jar","SubscriberMessageEJB","identityminder_ejb.jar,META-INF/ejb-jar.xml","","ACT","com.netegrity.ims.msg.queue",""]) 
				subOptions.append(["identityminder_ejb.jar","ServerCommandsEJB","identityminder_ejb.jar,META-INF/ejb-jar.xml","","ServerCommand","com/netegrity/idm/ServerCommandTopic",""]) 
				subOptions.append(["WorkPoint Server","ServerAutomatedActivityMDBean","wpServer.jar,META-INF/ejb-jar.xml","","jms/wpServAutoActActSpec","queue/wpServAutoActQueue",""]) 
				subOptions.append(["WorkPoint Server","UtilityMDBean","wpServer.jar,META-INF/ejb-jar.xml","","jms/wpUtilActSpec","queue/wpUtilQueue",""]) 
				options = ['-usedefaultbindings']
				options.append('-BindJndiForEJBMessageBinding')
				options.append(subOptions)
			else:
				subOptions = '['
				subOptions += ' -nopreCompileJSPs'
				subOptions += ' -distributeApp'
				subOptions += ' -nouseMetaDataFromBinary'
				subOptions += ' -nodeployejb'
				subOptions += ' -createMBeansForResources'
				subOptions += ' -reloadEnabled -reloadInterval 0'
				subOptions += ' -nodeployws'
				subOptions += ' -validateinstall warn'
				subOptions += ' -noprocessEmbeddedConfig'
				subOptions += ' -filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755'
				subOptions += ' -buildVersion Unknown'
				subOptions += ' -noallowDispatchRemoteInclude'
				subOptions += ' -noallowServiceRemoteInclude'
				subOptions += ' -asyncRequestDispatchType DISABLED'
				subOptions += ' -nouseAutoLink'
				subOptions += ' ]'
			printInfoLine( 'installing ' + appName + ' with ' + earFile )
			AdminApp.install( earFile, options )

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
			clusterNameList = ejbModules.item(i).getElementsByTagName("ClusterName")
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
		modOptionList = ["-MapModulesToServers", modOptions]
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
			clusterNameList = rarModules.item(i).getElementsByTagName("ClusterName")
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
	for i in range(webModules.getLength()):
		appModules = ""
		webFileName = getTagValue(webModules.item(i), "war-file-name")
		webDispName = getTagValue(webModules.item(i), "display-name")
		if(STANDALONE == "TRUE"):
			appModules = "+WebSphere:cell=" + cellName + ",node=" + MGRNODENAME + ",server=server1"
		else:
			clusterNameList = webModules.item(i).getElementsByTagName("cluster-name")
			clusterNameList = webModules.item(i).getElementsByTagName("ClusterName")
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

	# the following will always NameError with env, even if it is defined there will never be a match
###	if(re.search(env.upper(), "DEVWas/DEV1Was/SYSTESTWas/INTWas/UATWas") != None):
###		AdminApp.edit(appName, "-reloadEnabled true -reloadInterval 0")
###		print "INFO: appInstall: Disabled file update scanning for " + appName
###
	# TODO: special processing for IdentityMinder ...
	#   scopeS is the cluster name ... but we now have multiple cluster names do we loop?
	#   actually was_im only appears to use appName, everything else not referenced ... need to check with Nik and Dev 
	if appName == 'Netegrity IdentityMinder':
		was_im( None, appName, None, None, None )
###	if(appName == "Netegrity IdentityMinder"):
###		was_im(found, appName, earFile, scopeS, scopeN)
###
###	print "INFO: appInstall: Finished with application deploy for " + appName
###
###	if(SAVE == 1):
###		if(postDeployTask == "None"):
###			print "INFO: appInstall: Running postDeployTask saveSync"
###			saveSync("sync")
###		else:
###			print "INFO: appInstall: Running postDeployTasks saveSync and " + postDeployTask
###			saveSync("sync")
###			time.sleep(30)
###			for cName in clusterList:
###				clusterOp(cName, postDeployTask)
###
###	#print "DEBUG: END: appInstall"
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	if debug: sys.stdout.write( '  DEBUG: End stage ' + processStage.pop() + '.\n' )
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	return