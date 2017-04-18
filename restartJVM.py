JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/validateNode.py")
execfile(JYTHON_HOME+"/validateServer.py")
execfile(JYTHON_HOME+"/serversMgmt.py")

# Main
try:
   status = _UNKNOWN_
   if(len(sys.argv) == 3):
      envName    = sys.argv[0]
      nodeName   = sys.argv[1]
      jvmName    = sys.argv[2]

      if (validateNode(nodeName)==_SUCCESS_):
         if (nodeagentIsRunning(nodeName)):
            if (validateServer(nodeName,jvmName)==_SUCCESS_):
               status = stopSingleServer(nodeName, jvmName)
               status = startSingleServer(nodeName, jvmName)
            #endIf
         else:
            print "EXCEPTION: the node agent is not started; unable to restart JVM!"
            status = _FAILURE_
         #endIf
      #endIf
   else:
      print "EXCEPTION: Main - Missing/bad input parameters."
      status = _FAILURE_
      raise Exception, "Invalid Request."
   #endIf
   print "Status: ", status
except:
   print "EXCEPTION: Invalid Request"
   status = _FAILURE_
   print "Status: ", status
#endTry
#endMain