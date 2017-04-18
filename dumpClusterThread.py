JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")
execfile(JYTHON_HOME+"/validateCluster.py")

def dumpClusterThread(clusterName):
   try:
      clusterMBean = AdminControl.completeObjectName('WebSphere:type=Cluster,name=' + clusterName + ',*')
      clusterMgr   = AdminControl.completeObjectName('cell=' + cellName + ',type=ClusterMgr,*')
      clusterState = AdminControl.getAttribute(clusterMBean, 'state')
      clusterID    = AdminConfig.getid("/ServerCluster:" +clusterName+"/")
      AdminControl.invoke(clusterMgr, 'retrieveClusters')

      if (clusterState == "websphere.cluster.stopped"):
         print "Exception: All JVMs in cluster "  + clusterName + " are currently stopped, unable to generate thread dump!"
         status = _FAILURE_
         print "Status: ", status
      else:
         print ""
         print "INFO: Thead dump for " + clusterName + " in progress..."
         print ""
         clusterMembers = AdminConfig.list('ClusterMember', clusterID)
         for member in clusterMembers.split(lineSep):
            serverName  = AdminConfig.showAttribute(member, 'memberName')
            nodeName    = AdminConfig.showAttribute(member, 'nodeName')
            serverMBean  = AdminControl.completeObjectName('WebSphere:type=JVM,node=' + nodeName + ',process=' + serverName + ',*')
            if (serverMBean != ''):
               #AdminControl.invoke(serverMBean,'generateHeapDump')
               AdminControl.invoke(serverMBean,'dumpThreads')
               print "INFO: Generating thread dump for " +serverName
               status = _SUCCESS_
               print "Status: ", status
               print ""
            else:
               print "INFO: Server " +serverName+ " is currently stopped, unable to generate thread dump!"
               status = _ALREADYSTOPPED_
               print "Status: ", status
               print ""
            #endIf
         #endFor            
      #endIf
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      print "Status: ", status
   #endTry
#endDef

# Main
try:
   status = _UNKNOWN_
   if(len(sys.argv) == 2):
      envName    	= sys.argv[0]
      clusterName	= sys.argv[1]
      if (validateCluster(clusterName)==_SUCCESS_):
         dumpClusterThread(clusterName)
      #endIf
   else:
      print "Exception: Invalid Request, bad or missing input parameter(s)."
      status = _FAILURE_
      print "Status: ", status
      #raise Exception, "Invalid Request."
   #endIf
except:
   print "Exception: The cluster cannot be located or is not running"
   status = _FAILURE_
   print "Status: ", status
#endTry
#endMain