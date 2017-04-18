JYTHON_HOME = "/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/globalconstants.py")

def listClusters(envName):
	try:
		f = open("J:/temp/"+envName+"_Clusters.txt","w")
		clusters = (AdminConfig.list('ServerCluster')).split('\r\n')
		#f.write('%s^%s^%s^%s' % ('Env', 'HostName', 'Node Name', 'Cluster Name') + CRLF)
		for cluster in clusters:
			#cName = cluster[0:cluster.find("(")]
			cName = AdminConfig.showAttribute(cluster, 'name')
			#f.write('%s^%s^%s^%s' % (envName,clusterHostName, cName) + CRLF)
			f.write('%s' % (cName) + CRLF)			
		f.close()
	except:
		typ, val, tb = sys.exc_info()
		if(typ==SystemExit):  raise SystemExit,`val`
		print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
		return -1

# Main
try:
    if(len(sys.argv) == 1):
        envName = sys.argv[0]
        print "INFO: Getting info for all clusters in " + envName
        print ""
        listClusters(envName)
    else:
        print "Exception: main: Missing/Bad input parameters"
        raise Exception, "Script raised exception"
    #endif
except:
    print "Exception: Invalid Request"