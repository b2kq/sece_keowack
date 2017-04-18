def wilyIsInstalled(nodeName, jvmName):
   try:
      wjvmParm = "-javaagent:wily/Agent.jar"
      serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName,jvmName))
      jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
      ojvmParm = AdminConfig.showAttribute(jvmId, 'genericJvmArguments')

      if(len(ojvmParm)> 0):
         if(ojvmParm.find(wjvmParm) != -1): return _TRUE_
      return _FALSE_

   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      return _FALSE_
   #endTry
#endDef

def whichVersion(nodeName, jvmName):
   try:
      wily91 = "-Dcom.wily.introscope.agentProfile=wily/core/config/IntroscopeAgent.profile"
      wily81 = "-Dcom.wily.introscope.agentProfile=wily/IntroscopeAgent.profile"
      wilyonWAS6 = "AutoProbeConnector.jar"
      serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName,jvmName))
      jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
      ojvmParm = AdminConfig.showAttribute(jvmId, 'genericJvmArguments')

      if(len(ojvmParm)> 0):
         if(ojvmParm.find(wily91) != -1):
            return 9
         elif(ojvmParm.find(wily81) != -1):
            if(ojvmParm.find(wilyonWAS6) != -1):
               return 6
            else
               return 8
         else
            return 0
      else
         return 0
      #endIf

   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      return 0
   #endTry
#endDef

def addWily9(nodeName, jvmName):
   try:
      #Define the custom service for Wily Introscope
      CSdisplayName = ['displayName', 'Introscope Custom Service']
      CSclassname = ['classname', 'com.wily.introscope.api.websphere.IntroscopeCustomService']
      CSclasspath = ['classpath', 'wily/common/WebAppSupport.jar']
      CSdescription = ['description', 'Wily Introscope']
      CSenable = ['enable', 'true']
      CSprerequisiteServices = ['prerequisiteServices', '']
      CSproperties = ['properties', '']
      CSattributes =  [CSdisplayName, CSclassname, CSclasspath, CSdescription, CSenable, CSprerequisiteServices, CSproperties]

      #Define the Generic JVM arguments for Wily Introscope
      wjvmParm91 = "-javaagent:wily/Agent.jar -Dcom.wily.introscope.agentProfile=wily/core/config/IntroscopeAgent.profile -Dcom.wily.introscope.agent.agentName=${WAS_SERVER_NAME} -Xverify:none"
      wjvmParm81 = "-javaagent:wily/Agent.jar -Dcom.wily.introscope.agentProfile=wily/IntroscopeAgent.profile"
      wjvmParm61 = "-Xbootclasspath/p:wily/connectors/AutoProbeConnector.jar;wily/Agent.jar -Dcom.wily.introscope.agentProfile=wily/IntroscopeAgent.profile"
      njvmParm = ""
      modifyGenericParms = 0

      #Get the current Generic JVM arguments
      serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName,jvmName))
      jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
      ojvmParm = AdminConfig.showAttribute(jvmId, 'genericJvmArguments')
      if(ojvmParm == None): ojvmParm = ""

      #Determine if we are upgrading from Wily 8 to 9 or adding Wily 9 from scratch
      if (wilyIsInstalled(nodeName, jvmName)):
         wilyVersion = whichVersion(nodeName, jvmName)
         if(wilyVersion == 9):
            print "INFO: Generic JVM arguments already configured for W91; no changes made"
         else
            if(wilyVersion == 8):
               print "INFO: Generic JVM arguments configured for W81; will upgrade to W91"
               njvmParm = ojvmParm.replace(wjvmParm81, wjvmParm91, 1)
               modifyGenericParms = 1
            elif(wilyVersion == 6):
               print "INFO: adding W91 to WASv6 JVM"
               njvmParm = ojvmParm.replace(wjvmParm61, wjvmParm91, 1)
               modifyGenericParms = 1
            #endIf
         #endIf
      else
         print "INFO: adding W91 instrumentation"
         if(len(ojvmParm)> 0):
            njvmParm = ojvmParm + " " + wjvmParm91
         else
            njvmParm = wjvmParm91
         #endIf
         modifyGenericParms = 1
      #endIf

      if(modifyGenericParms == 1):
         AdminConfig.modify(jvmId, [['genericJvmArguments', njvmParm]])
         print "INFO: Modified Generic JVM arguments from: %s to %s" % (ojvmParm,njvmParm)

      #Does the custom service exist?
      cServices = AdminConfig.list('CustomService', serverId)
      foundWilyCService = 0
      for cService in cServices.split(lineSep):
         if(cService != ""):
            oServiceName = AdminConfig.showAttribute(cService, 'displayName')
            if(oServiceName == CSdisplayName[1]):
               print "INFO: already configured for custom service %s" % (oServiceName)
               foundWilyCService = 1
               break
            #endIf
         #endIf
      #endFor

      #Add the custom service
      if(foundWilyCService == 0):
         nService = AdminConfig.create('CustomService', serverId, CSattributes)
         print "INFO: added custom service: " + CSdisplayName[1]
      #endIf
      status = _SUCCESS_
      return status

   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      return status
   #endTry
#endDef