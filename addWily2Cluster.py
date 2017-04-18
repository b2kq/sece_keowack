JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/convertToList.py")
execfile(JYTHON_HOME+"/validateCluster.py")
execfile(JYTHON_HOME+"/wilyAdd.py")
execfile(JYTHON_HOME+"/saveOperations.py")

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
      wily9 = "-Dcom.wily.introscope.agentProfile=wily/core/config/IntroscopeAgent.profile"
      wily8 = "-Dcom.wily.introscope.agentProfile=wily/IntroscopeAgent.profile"
      wilyonWAS6 = "AutoProbeConnector.jar"

      if(len(ojvmParm)> 0):
         if(ojvmParm.find(wily9) != -1):
            return 9
         elif(ojvmParm.find(wily8) != -1):
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

def addWily9toCluster(clusterName):
   try:
      clusterID = AdminConfig.getid("/ServerCluster:%s/" % (clusterName))
      clusterMembers = AdminConfig.list('ClusterMember', clusterID)
      for member in clusterMembers.split(lineSep):
         jvmName  = AdminConfig.showAttribute(member, 'memberName')
         nodeName = AdminConfig.showAttribute(member, 'nodeName')
         status = addWily9(nodeName, jvmName)
      #endFor
      if(SAVE == 1):
         saveSync("sync")
      else:
         print "\n\nChanges will NOT be saved!"
      #endIf
      return status
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      return status
   #endTry
#endDef

#Main
try:
   status = _UNKNOWN_
   if(len(sys.argv) > 1):
      env           = sys.argv[0]
      clusterName   = sys.argv[1]

      if(len(sys.argv) > 2):
         if(sys.argv[2].upper() == "SAVE"):
            SAVE = 1
         elif(sys.argv[2].upper() == "NOSAVE"):
            SAVE = 0
      elif(len(sys.argv) == 2):
         SAVE = 0
         print "Defaulting to NOSAVE"
      #endIf

      if (validateCluster(clusterName)==_SUCCESS_):
         status = addWily9toCluster(clusterName)
      #endIf

   else:
      print "EXCEPTION: Missing/invalid input parameters."
      status = _FAILURE_
   #endIf
   print "Status: %s\n" % (status)

except:
   typ, val, tb = sys.exc_info()
   if(typ==SystemExit):  raise SystemExit,`val`
   print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
   status = _FAILURE_
   print "Status: %s\r\n" % (status)
#endTry
#endMain