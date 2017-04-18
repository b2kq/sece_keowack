# This is a stand-alone script
# Depends on global.py, jvm.py, saveOperations.py

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/jvm.py")
execfile(JYTHON_HOME+"/saveOperations.py")

def addToAll():
    hamList = AdminConfig.list("HAManagerService")
    for ham in hamList.split(lineSep):
        temp = ham.split("/")[5]
        jvmName = temp.split("|")[0]
        nodeName = ham.split("/")[3]
        print jvmName + " " + nodeName
        setGenericJVMArgs(jvmName, nodeName, "-Xshareclasses:none")
    return

def removeFromAll():
    hamList = AdminConfig.list("HAManagerService")
    for ham in hamList.split(lineSep):
        temp = ham.split("/")[5]
        jvmName = temp.split("|")[0]
        nodeName = ham.split("/")[3]
        print jvmName + " " + nodeName
        serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
        jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
        ojvmParm = AdminConfig.showAttribute(jvmId, 'genericJvmArguments')
        if((ojvmParm != "") & (ojvmParm.find("-Xshareclasses:none") >= 0)):
            njvmParm = ojvmParm.replace("-Xshareclasses:none", "")
            AdminConfig.modify(jvmId, [['genericJvmArguments', njvmParm]])
            print njvmParm
    return

removeFromAll()
#saveSync("sync")