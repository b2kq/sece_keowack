# This is a stand-alone script
# Depends on global.py, saveOperations.py

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/saveOperations.py")

def JVM(jvmName, nodeName, task):
    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    if(jvmId == ""):
        print "Exception: JVM: Bad jvmName, or nodeName passed"
        return
    hamId = AdminConfig.list("HAManagerService", jvmId)
    if(task.upper() == "ENABLE"):
        AdminConfig.modify(hamId, [["enable", "true"]])
        print "INFO: JVM: HA MGR enabled on " + jvmName + " " + nodeName
    elif(task.upper() == "DISABLE"):
        AdminConfig.modify(hamId, [["enable", "false"]])
        print "INFO: JVM: HA MGR disabled on " + jvmName + " " + nodeName
    else:
        print "Exception: JVM: Bad HA-MGR task"
    return

def CLUSTER(clusterName, task):
    clusId = AdminConfig.getid('/ServerCluster:' + clusterName + '/')
    if(clusId == ""):
        print "Exception: CLUSTER: Bad clusterName passed"
        return
    clusterMembers = AdminConfig.list('ClusterMember', clusId)
    for member in clusterMembers.split(lineSep):
        jvmName = AdminConfig.showAttribute(member, 'memberName')
        nodeName = AdminConfig.showAttribute(member, 'nodeName')
        JVM(jvmName, nodeName, task)
    return

def ALL(task):
    hamList = AdminConfig.list("HAManagerService")
    for ham in hamList.split(lineSep):
        temp = ham.split("/")[5]
        jvmName = temp.split("|")[0]
        nodeName = ham.split("/")[3]
        if((jvmName == "dmgr") | (jvmName == "nodeagent")):
            print "INFO: ALL: Skipping " + jvmName + " " + nodeName
        else:
            JVM(jvmName, nodeName, task)
    return

def showAllActive():
    hamList = AdminConfig.list("HAManagerService")
    for ham in hamList.split(lineSep):
        temp = ham.split("/")[5]
        jvmName = temp.split("|")[0]
        nodeName = ham.split("/")[3]
        jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
        if(jvmId == ""):
            print "Exception: JVM: Bad jvmName, or nodeName passed"
            return
        hamId = AdminConfig.list("HAManagerService", jvmId)
        hamState = AdminConfig.showAttribute(hamId, 'enable')
        if(hamState == "true"):
            print "HA Manager enabled state for " + jvmName + ", "  + nodeName + " is " + hamState
        if(((jvmName == "dmgr") | (jvmName == "nodeagent")) & (hamState != "true")):
            print "HA Manager enabled state for " + jvmName + ", "  + nodeName + " is " + hamState
    return

def main():
    if(sys.argv[0].upper() == "ALL"):
        ALL(sys.argv[1])
    elif(sys.argv[0].upper() == "CLUSTER"):
        CLUSTER(sys.argv[1], sys.argv[2])
    elif(sys.argv[0].upper() == "JVM"):
        JVM(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Exception: main: Bad argument, specify one of ALL/CLUSTER/JVM"

    lastArg = len(sys.argv) - 1
    if(sys.argv[lastArg].upper() == "SAVE"):
        saveSync("sync")

#main()