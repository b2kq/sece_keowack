# This is a stand-alone script
# Depends on global.py, saveOperations.py

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/saveOperations.py")

def changeModClassLoaderPolicy(appName, modFileName, classLdrMode):
    #print "DEBUG: START: changeModClassLoaderPolicy"

    # Find if the app already exists or not
    found = 0
    appList = AdminApp.list()
    for app in appList.split(lineSep):
        if(app == appName):
            found = 1
            break
    if(found == 0):
        print "ERROR: changeModClassLoaderPolicy: Application " + appName + " not found, verify your app is installed"
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    if((classLdrMode.upper() == "PARENT_FIRST") or (classLdrMode.upper() == "PARENT_LAST")):
        deployment = AdminConfig.getid('/Deployment:' + appName + '/')
        depObject = AdminConfig.showAttribute(deployment, 'deployedObject')
        modules = AdminConfig.showAttribute(depObject, 'modules')
        modules = modules[1:len(modules)-1].split(" ")
        for module in modules:
            modURI = AdminConfig.showAttribute(module, 'uri')
            if(modURI == modFileName):
                curClassLdrMode = AdminConfig.showAttribute(module, 'classloaderMode')
                if(curClassLdrMode != classLdrMode):
                    AdminConfig.modify(module, [['classloaderMode', classLdrMode.upper()]])
                    print "INFO: changeModClassLoaderPolicy: Changed module " + modFileName + " class loader mode from " + curClassLdrMode + " to " + classLdrMode.upper()

    #print "DEBUG: END: changeModClassLoaderPolicy"
    return

changeModClassLoaderPolicy(sys.argv[0], sys.argv[1], sys.argv[2])
saveSync("fullresync")