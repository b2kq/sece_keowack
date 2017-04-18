JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/validateNode.py")
execfile(JYTHON_HOME+"/validateServer.py")

def getJVMMBean (nodeName, jvmName):
    iter = [1,2,3,4]
    for x in iter:
        jvmMBean = AdminControl.completeObjectName('WebSphere:type=Server,node=' + nodeName + ',process=' + jvmName + ',*')
        if((jvmMBean == "") & (x == 2)):
            print "WARNING: Could not get JVM MBean"
            return
        if(jvmMBean != ""):
            break
        sleep(60)
    return jvmMBean

def getServerPID(nodeName, jvmName):
   try:
      serverMBean = AdminControl.queryNames("node="+nodeName+",process="+jvmName+",type=Server,*")
      if (len(serverMBean) == 0):
         print "\r\nINFO: server %s is not running" % (jvmName)
      else:
         result = AdminControl.getAttribute(serverMBean, "pid")
         return result
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
   #endTry
#endDef

# Main
try:
   status = _UNKNOWN_
   if(len(sys.argv) == 3):
      envName    = sys.argv[0]
      nodeName   = sys.argv[1]
      jvmName    = sys.argv[2]
      myPID      = 0
      if (validateNode(nodeName)==_SUCCESS_):
         if (validateServer(nodeName,jvmName)==_SUCCESS_):
            myPID = getServerPID(nodeName, jvmName)
            print "\r\nINFO: PID for %s is %s" % (jvmName,myPID)
            status = _SUCCESS_
         #endIf
      #endIf
   else:
      print "EXCEPTION: Invalid Request, bad or missing input parameter(s)."
      status = _FAILURE_
      #raise Exception, "Invalid Request."
   #endIf
   #print "Status: ", status
except:
   print "EXCEPTION: The server cannot be located or is not running"
   status = _FAILURE_
   print "Status: ", status
#endTry
#endMain