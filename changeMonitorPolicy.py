JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/validateNode.py")
execfile(JYTHON_HOME+"/validateServer.py")
execfile(JYTHON_HOME+"/saveOperations.py")
#execfile(JYTHON_HOME+"/saveTask.py")

def changeMonitorSettings(nodeName,serverName,restart,svrState,disableStart):
   try:
      jvmObjId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + serverName)
      if(len(jvmObjId) == 0):
         print "Exception: unable to get server information."
         #raise Exception, "Script raised exception, exiting with errors!"
         return _FAILURE_
      #endIf

      #objName = AdminConfig.getObjectName(jvmObjId)
      #monitor = AdminConfig.list('MonitoringPolicy', jvmObjId)
      #currentAutoRestart  = AdminConfig.showAttribute(monitor, 'autoRestart')
      #currentRestartState = AdminConfig.showAttribute(monitor, 'nodeRestartState')
      #print ""
      #print "INFO: Current Monitoring Policy Settings " + serverName + " on " + nodeName
      #print "      Node autorestart: " + currentAutoRestart
      #print "      Node restart state: " + currentRestartState
      #AdminConfig.modify(monitor, [['autoRestart', restart]])
      #AdminConfig.modify(monitor, [['nodeRestartState', svrState]])
      #state = AdminConfig.showAttribute(monitor, 'nodeRestartState')
      #currentAutoRestart  = AdminConfig.showAttribute(monitor, 'autoRestart')
      #currentRestartState = AdminConfig.showAttribute(monitor, 'nodeRestartState')
      #print ""
      #print "INFO: New Monitoring Policy Settings " + serverName + " on " + nodeName
      #print "      Node autorestart: " + currentAutoRestart
      #print "      Node restart state: " + currentRestartState

      jvmParm = "DONTSTART"
      newjvmParm = ""
      jvmId = AdminConfig.list('JavaVirtualMachine',jvmObjId)
      ojvmParm = AdminConfig.showAttribute(jvmId, 'genericJvmArguments')
      print ""
      print "INFO: Current genericJvmArguments " + serverName + " on " + nodeName
      print ojvmParm

      if (disableStart == "TRUE"):
         #if (jvmParm in ojvmParm): this does not work!
         if(ojvmParm.find(jvmParm) > 0):
            print "Exception: ", jvmParm, "is already in the generic JVM arguments."
            return _ALREADYSTARTED_
         else:
            newjvmParm = jvmParm + " " + ojvmParm
         #endIf
      else:
         newjvmParm = ojvmParm.replace(jvmParm, '')
         newjvmParm = newjvmParm.lstrip()
      #endIf

      print ""
      print "INFO: New genericJvmArguments " + serverName + " on " + nodeName
      print newjvmParm
      print ""
      AdminConfig.modify(jvmId, [['genericJvmArguments', newjvmParm]])

      if(SAVE == 1):
         saveSync("sync")
      else:
         print ""
         print "Changes will NOT be saved!"
      #endIf

      return _SUCCESS_

   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      return _FAILURE_
   #endTry
#endDef

#Main
try:
   status = _UNKNOWN_
   if(len(sys.argv) > 0):
      envName        = sys.argv[0]
      nodeName       = sys.argv[1]
      serverName     = sys.argv[2]
      restart        = sys.argv[3]
      option         = sys.argv[4]
      disableStart   = sys.argv[5].upper()
      validStates    = ["RUNNING", "STOPPED", "PREVIOUS"]
      print nodeName, serverName, restart, option, disableStart

      if(len(sys.argv) == 7):
         if(sys.argv[6].upper() == "SAVE"):
            SAVE = 1
         elif(sys.argv[6].upper() == "NOSAVE"):
            SAVE = 0
      elif(len(sys.argv) == 6):
         print "Defaulting to NOSAVE"
         print ""
      #endIf

      if ((eval(option)> 2) | (eval(option)< 0)) :
         print "Exception: Invalid monitoring state, only 0-RUNNING, 1-STOPPED, or 3-PREVIOUS allowed."
         status = _FAILURE_
         raise Exception, "Invalid Request"
      else:
         svrState = validStates[eval(option)]
         #print svrState
         if (validateNode(nodeName)==_SUCCESS_):
            if (validateServer(nodeName,serverName)==_SUCCESS_):
               status = changeMonitorSettings(nodeName,serverName,restart,svrState,disableStart)
            #endIf
         #endIf
      #endIf

   else:
      print "Exception: Missing/invalid input parameters."
      status = _FAILURE_
      #raise Exception, "Script raised exception, you are doing something wrong!!!"
   #endIf
   print "Status: ", status
except:
    print "Exception: Missing/invalid input parameters."
    status = _FAILURE_
    print "Status: ", status
#endTry
#endMain