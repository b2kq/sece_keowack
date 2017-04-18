JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/validateCluster.py")
execfile(JYTHON_HOME+"/validateServer.py")
execfile(JYTHON_HOME+"/serversMgmt.py")

# Main
try:
   status = _UNKNOWN_
   if(len(sys.argv) == 2):
      envName    	= sys.argv[0]
      clusterName	= sys.argv[1]
      if (validateCluster(clusterName)==_SUCCESS_):
         status = rippleStartCluster(clusterName)
      #endIf
   else:
      print "Exception: Invalid Request, bad or missing input parameter(s)."
      status = _FAILURE_
      #raise Exception, "Invalid Request."
   #endIf
   #print "Status: ", status
except:
   print "Exception: The cluster cannot be located or is not running"
   status = _FAILURE_
   print "Status: ", status
#endTry
#endMain