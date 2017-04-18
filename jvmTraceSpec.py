# This is a stand-alone script
# Depends on global.py, saveOperations.py

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/saveOperations.py")

def jvmTraceLevel(jvmName, nodeName, startupTraceSpec):
    #The changes below were made by Nik to modify the script to change the runtime 
    #and not the configuration trace settings
    #jvmId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + jvmName + '/')
    #if(jvmId == ""):
    #    print "ERROR: jvmTraceLevel: Bad server name passed: " + jvmName
    #    raise Exception, "Script raised exception, you are doing something wrong!!!"
    #tc = AdminConfig.list('TraceService', jvmId)
    #AdminConfig.modify(tc, [['startupTraceSpecification', startupTraceSpec]])
    #print AdminControl.queryMBeans('type=TraceService,process=AgencyContact_1_1,*')
    inptstrg = 'type=TraceService,process=' + jvmName + ',*'
    print inptstrg
    objNameString = AdminControl.completeObjectName(inptstrg) 
    AdminControl.setAttribute(objNameString,'traceSpecification', startupTraceSpec)
  
    #End of Nik's changes
    print "INFO: jvmTraceLevel: Changed trace level to " + startupTraceSpec + " for " + jvmName + ", " + nodeName
    return

def CLUSTER(clusterName, startupTraceSpec):
    clusId = AdminConfig.getid('/ServerCluster:' + clusterName + '/')
    if(clusId == ""):
        print "Exception: CLUSTER: Bad clusterName passed"
        return
    clusterMembers = AdminConfig.list('ClusterMember', clusId)
    for member in clusterMembers.split(lineSep):
        jvmName = AdminConfig.showAttribute(member, 'memberName')
        nodeName = AdminConfig.showAttribute(member, 'nodeName')
        jvmTraceLevel(jvmName, nodeName, startupTraceSpec)
    return

def ALL(startupTraceSpec):
    hamList = AdminConfig.list("HAManagerService")
    for ham in hamList.split(lineSep):
        temp = ham.split("/")[5]
        jvmName = temp.split("|")[0]
        nodeName = ham.split("/")[3]
        if((jvmName == "dmgr") | (jvmName == "nodeagent")):
            print "INFO: ALL: Skipping " + jvmName + " " + nodeName
        else:
            jvmTraceLevel(jvmName, nodeName, startupTraceSpec)
    return

def main():
    if(sys.argv[0].upper() == "ALL"):
        ALL(sys.argv[1])
    elif(sys.argv[0].upper() == "CLUSTER"):
        CLUSTER(sys.argv[1], sys.argv[2])
    elif(sys.argv[0].upper() == "JVM"):
        jvmTraceLevel(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Exception: main: Bad argument, specify one of ALL/CLUSTER/JVM"

    lastArg = len(sys.argv) - 1
    #Some More Nik Changes for the Runtime Settings. I commented out the Save and Sync calls because they are not required
    #if(sys.argv[lastArg].upper() == "SAVE"):
    #    saveSync("sync")
    #End of Nik changes
main()