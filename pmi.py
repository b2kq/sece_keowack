# This is an stand-alone script
# Depends on saveOperations.py

# LIMITATIONS: The "all" option will fail if there are any WebSphere 5 JVMs in the cell

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/saveOperations.py")

# Function pmi() takes 2 parameters: enable - TRUE/FALSE, clusterName - a WebSphere cluster name or "all"
def pmi(enable, clusterName):
    clusterList = AdminConfig.list('ServerCluster')
    for clusterId in clusterList.split("\r\n"):
        curClusterName = AdminConfig.showAttribute(clusterId, 'name')
        if((clusterName.upper() == "ALL") | (clusterName == curClusterName)):
            members = AdminConfig.showAttribute(clusterId, 'members')
            memberList = members[1:len(members)-1].split(" ")
            for member in memberList:
                jvmName = AdminConfig.showAttribute(member, 'memberName')
                nodeName = AdminConfig.showAttribute(member, 'nodeName')
                serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
                pmi = AdminConfig.list('PMIService', serverId)
                if(enable.upper() == "TRUE"):
                    AdminConfig.modify(pmi, [['enable', 'true']])
                    AdminConfig.modify(pmi, [['statisticSet', 'basic']])
                    print "INFO: pmi: Enabled BASIC PMI for " + jvmName + ", " + nodeName
                else:
                    AdminConfig.modify(pmi, [['enable', 'false']])
                    AdminConfig.modify(pmi, [['statisticSet', 'none']])
                    print "INFO: pmi: Disabled PMI for " + jvmName + ", " + nodeName

pmi(sys.argv[0], sys.argv[1])
if(len(sys.argv) == 3):
    if(sys.argv[2].upper() == "SAVE"):
        saveSync("sync")