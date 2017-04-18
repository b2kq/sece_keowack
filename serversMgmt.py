def stopSingleServer(nodeName, jvmName):
   try:
      if (jvmIsRunning(nodeName, jvmName)):
         try:
            AdminControl.stopServer(jvmName, nodeName)
            #AdminControl.invoke(jvmMBean, 'stop')
            print "\r\nINFO: %s on %s stop in progress..." % (jvmName,nodeName)
         except:
            print "EXCEPTION: Unable to stop JVM, issuing terminate."
            print "Check the server log files for failure information and status."
            AdminControl.stopServer(jvmName, nodeName, 'terminate')
            status = _UNKNOWN_
            return status
         else:
            timeout = 600 # wait 10 minutes for graceful stop
            sleepCounter = 0
            #jvmMBean = getJVMMBean (nodeName, jvmName)
            #jvmMBean = AdminControl.completeObjectName('WebSphere:type=Server,node=' + nodeName + ',process=' + jvmName + ',*')
            jvmMBean = AdminControl.queryNames('type=Server,node=' + nodeName + ',name=' + jvmName + ',*')
            while(jvmMBean != ""):
               if(sleepCounter < timeout):
                  time.sleep(10)
                  sleepCounter = sleepCounter + 10
                  print "Waiting "+ str(sleepCounter) + " seconds."
                  #jvmMBean = AdminControl.completeObjectName('WebSphere:type=Server,node=' + nodeName + ',process=' + jvmName + ',*')
                  jvmMBean = AdminControl.queryNames('type=Server,node=' + nodeName + ',name=' + jvmName + ',*')
               else:
                  print "WARNING: Unable to stop JVM within " +str(timeout)+ " seconds, issuing terminate."
                  print "Check the server log files for failure information and status."
                  AdminControl.stopServer(jvmName, nodeName, 'terminate')
                  status = _UNKNOWN_
                  return status
         print "INFO: Successfully stopped %s" % (jvmName)
         status = _SUCCESS_
      else:
         print "WARNING: Server %s is not running." % (jvmName)
         status = _ALREADYSTOPPED_
      #endIf
      return status
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      return status
   #endTry
#endDef

def stopCluster(clusterName):
   try:
      clusterMgr   = AdminControl.completeObjectName('cell=' + cellName + ',type=ClusterMgr,*')
      AdminControl.invoke(clusterMgr, 'retrieveClusters')
      clusterMBean = AdminControl.completeObjectName('WebSphere:type=Cluster,name=%s,*' % (clusterName))
      clusterState = AdminControl.getAttribute(clusterMBean, 'state')

      # Do nothing, the cluster is already stopped
      if (clusterState == "websphere.cluster.stopped"):
         print "\r\nINFO: All JVMs in cluster %s are already stopped." % (clusterName)
         status = _ALREADYSTOPPED_
         print "Status: %s\r\n" % (status)
      # Stop the individual running JVMs
      elif (clusterState == "websphere.cluster.running" or clusterState == "websphere.cluster.partial.start" or clusterState == "websphere.cluster.partial.stop"):
         print "\r\nINFO: Stopping cluster %s in progress..." % (clusterName)
         clusterID    = AdminConfig.getid("/ServerCluster:%s/" % (clusterName))
         clusterMembers = AdminConfig.list('ClusterMember', clusterID)
         for member in clusterMembers.split(lineSep):
            serverName  = AdminConfig.showAttribute(member, 'memberName')
            nodeName    = AdminConfig.showAttribute(member, 'nodeName')
            serverMBean = AdminControl.completeObjectName('type=Server,name=%s,*' % (serverName))
            if (serverMBean != '' and AdminControl.invoke(serverMBean,'getState')=="STARTED"):
               status = stopSingleServer(nodeName, serverName)
               print "Status: %s\r\n" % (status)
            else:
               print "INFO: " +serverName+ " already stopped."
               status = _ALREADYSTOPPED_
               print "Status: %s\r\n" % (status)
            #endIf
         #endFor
      else:
         print "EXCEPTION: Unknown cluster status, unable to complete stop cluster request."
         status = _FAILURE_
         print "Status: %s\r\n" % (status)
      #endIf
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      print "Status: %s\r\n" % (status)
   #endTry
   return status
#endDef

def stopServersInNode(nodeName):
   try:
      servers = AdminConfig.getid("/Node:"+nodeName+"/Server:/")
      if (len(servers) == 0):
         print "EXCEPTION: No servers exist in node %s" % (nodeName)
         status = _FAILURE_
         print "Status: %s\r\n" % (status)
      else:
         runningServers = AdminControl.queryNames("type=Server,node="+nodeName+",processType=ManagedProcess,*")
         if (len(runningServers) == 0):
            print "WARNING: There are no running servers in node %s" % (nodeName)
            status = _FAILURE_
            print "Status: %s\r\n" % (status)
         else:
            runningServers = convertToList(runningServers)
            for aServer in runningServers:
               if (len(aServer) > 0):
                  serverName = AdminControl.getAttribute(aServer, "name")
                  status = stopSingleServer(nodeName, serverName)
                  print "Status: %s\r\n" % (status)
               #endIf
            #endFor
         #endIf
      #endIf
      #return status
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      #return status
      print "Status: %s\r\n" % (status)
   #endTry
#endDef

def startSingleServer(nodeName, jvmName):
   try:
      #Don't bother to start if the JVM is disabled
      if (jvmIsDisabled(nodeName, jvmName)):
         print "\r\nINFO: JVM has been disabled, will not attempt to start %s on %s" % (jvmName,nodeName)
         status = _SUCCESS_
         return status
      #endIf

      if (jvmIsRunning(nodeName, jvmName)):
         print "WARNING: Server %s is already running." % (jvmName)
         status = _ALREADYSTARTED_
      else:
         try:
            AdminControl.startServer(jvmName, nodeName, 1)
            print "\r\nINFO: %s on %s start in progress..." % (jvmName,nodeName)
         except:
            print "EXCEPTION: Unable to start JVM."
            print "Check the server log files for failure information and status."
            status = _UNKNOWN_
            return status
         else:
            timeout = 1200 # wait the default 20 minutes
            sleepCounter = 0
            #jvmMBean = AdminControl.completeObjectName('WebSphere:type=Server,node=' + nodeName + ',process=' + jvmName + ',*')
            jvmMBean = AdminControl.queryNames('type=Server,node=' + nodeName + ',name=' + jvmName + ',*')
            #if (len(jvmMBean) > 0 and AdminControl.getAttribute(jvmMBean, "state") == "STARTED"):
            while(jvmMBean == ""):
               if(sleepCounter < timeout):
                  time.sleep(10)
                  sleepCounter = sleepCounter + 10
                  print "Waiting "+ str(sleepCounter) + " seconds."
                  jvmMBean = AdminControl.queryNames('type=Server,node=' + nodeName + ',name=' + jvmName + ',*')
               else:
                  print "WARNING: Unable to start JVM within " +str(timeout)+ " seconds; check SystemOut.log for status."
                  status = _UNKNOWN_
                  return status
               #endIf
            #endWhile
         print "INFO: Successfully started %s" % (jvmName)
         status = _SUCCESS_
      #endIf
      return status
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      return status
   #endTry
#endDef

def rippleStartCluster(clusterName):
   try:
      clusterMgr     = AdminControl.completeObjectName('cell=' + cellName + ',type=ClusterMgr,*')
      AdminControl.invoke(clusterMgr, 'retrieveClusters')
      clusterMBean   = AdminControl.completeObjectName('WebSphere:type=Cluster,name=%s,*' % (clusterName))
      clusterState   = AdminControl.getAttribute(clusterMBean, 'state')
      clusterID      = AdminConfig.getid("/ServerCluster:%s/" % (clusterName))
      clusterMembers = AdminConfig.list('ClusterMember', clusterID)

      print "\r\nINFO: cluster current state - %s" % (clusterState)
      print "INFO: Ripple start cluster %s in progress..." % (clusterName)
      for member in clusterMembers.split(lineSep):
         serverName  = AdminConfig.showAttribute(member, 'memberName')
         nodeName    = AdminConfig.showAttribute(member, 'nodeName')
         serverMBean = AdminControl.completeObjectName('type=Server,name='+serverName+',*')
         if (serverMBean != '' and AdminControl.invoke(serverMBean,'getState')=="STARTED"):
            print "\r\nINFO: Restarting " +serverName+ " in progress..."
            #AdminControl.invoke(serverMBean,'restart')
            status = stopSingleServer(nodeName, serverName)
            status = startSingleServer(nodeName, serverName)
            print "Status: %s\r\n" % (status)
         else:
            print "\r\nINFO: Starting " +serverName+ " in progress..."
            #AdminControl.startServer(serverName, nodeName)
            status = startSingleServer(nodeName, serverName)
            print "Status: %s\r\n" % (status)
         #endIf
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      print "Status: %s\r\n" % (status)
   #endTry
   return status
#endDef

def startServersInNode(nodeName):
   try:
      servers = AdminConfig.getid("/Node:"+nodeName+"/Server:/")
      if (len(servers) == 0):
         print "EXCEPTION: No servers exist in node %s" % (nodeName)
         status = _FAILURE_
         print "Status: %s\r\n" % (status)
      else:
         servers = convertToList(servers)
         for aServer in servers:
            serverName = AdminConfig.showAttribute(aServer,"name")
            if (serverName != "nodeagent"):
               startSingleServer(nodeName, serverName)
               #AdminControl.startServer(serverName, nodeName)
            #endIf
            print ""
         #endFor
      #endIf
      #return status
   except:
      typ, val, tb = sys.exc_info()
      if(typ==SystemExit):  raise SystemExit,`val`
      print "EXCEPTION: %s %s " % (sys.exc_type, sys.exc_value)
      status = _FAILURE_
      #return status
      print "Status: %s\r\n" % (status)
   #endTry
#endDef