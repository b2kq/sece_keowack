JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/convertToList.py")

def wilyIsInstalled(ojvmParm):
   try:
      wjvmParm = "wily/Agent.jar"
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

def whichVersion(ojvmParm):
   try:
      wily91 = "-Dcom.wily.introscope.agentProfile=wily/core/config/IntroscopeAgent.profile"
      wily81 = "-Dcom.wily.introscope.agentProfile=wily/IntroscopeAgent.profile"
      wilyonWAS6 = "AutoProbeConnector.jar"

      if(len(ojvmParm)> 0):
         if(ojvmParm.find(wily91) != -1):
            return 9
         elif(ojvmParm.find(wily81) != -1):
            if(ojvmParm.find(wilyonWAS6) != -1):
               return 6
            else:
               return 8
         else:
            return 0
      else:
         return 0
      #endIf
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      return 0
   #endTry
#endDef

def listJVMArgs(envName):
   try:
      wjvmParm91 = "-javaagent:wily/Agent.jar -Dcom.wily.introscope.agentProfile=wily/core/config/IntroscopeAgent.profile -Dcom.wily.introscope.agent.agentName=${WAS_SERVER_NAME} -Xverify:none"
      wjvmParm81 = "-javaagent:wily/Agent.jar -Dcom.wily.introscope.agentProfile=wily/IntroscopeAgent.profile"
      wjvmParm61 = "-Xbootclasspath/p:wily/connectors/AutoProbeConnector.jar;wily/Agent.jar -Dcom.wily.introscope.agentProfile=wily/IntroscopeAgent.profile"
   
      f = open("J:/temp/"+envName+"_JVMs.txt","w")
      nodes = (AdminConfig.list('Node')).split(lineSep)
      #f.write('%s;%s;%s;%s;%s;%s' % ('Env', 'HostName', 'Node Name', 'Server Type', 'Server Name', 'genericJvmArguments') + "\n")
      for node in nodes:
         nodeName = node[0:node.find("(")]
         nodeId = AdminConfig.getid("/Node:" + nodeName)
         nodeHostName = AdminConfig.showAttribute(nodeId, 'hostName')
         servers = AdminConfig.getid("/Node:"+nodeName+"/Server:/")
         if (len(servers) == 0):
            print "EXCEPTION: No servers exist in node %s" % (node)
         else:
            servers = convertToList(servers)
            for aServer in servers:
               if (len(aServer) > 0):
                  sType = AdminConfig.showAttribute(aServer,"serverType")
                  if sType == 'APPLICATION_SERVER':
                     jvmId = AdminConfig.list('JavaVirtualMachine', aServer)
                     #serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName,jvmName))
                     serverName = AdminConfig.showAttribute(aServer, "name")
                     ojvmParm = AdminConfig.showAttribute(jvmId, 'genericJvmArguments')
                     wVersion = ""
                     njvmParm = ""
                     if (wilyIsInstalled(ojvmParm)):
                        wilyVersion = whichVersion(ojvmParm)
                        f.write('%s^%s^%s^%s^%s^%s' % (envName,nodeHostName,nodeName,serverName,wilyVersion,ojvmParm) + "\n")
                     #endIf
                     #f.write('%s;%s;%s;%s;%s;%s' % (nodeHostName,nodeName,serverName,wVersion,ojvmParm,njvmParm) + "\n")
                  #endIf
               #endIf
            #endFor
         #endIf
      #endFor
      f.close()
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      return -1
   #endTry
#endDef

# Main
try:
    if(len(sys.argv) == 1):
        envName = sys.argv[0]
        print "INFO: Getting genericJvmArguments for all servers in %s\r\n" % (envName)
        listJVMArgs(envName)
    else:
        print "Exception: main: Missing/Bad input parameters"
        raise Exception, "Script raised exception"
    #endif
except:
    print "Exception: Invalid Request"