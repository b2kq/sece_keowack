#! /usr/bin/python

__author__="USGEXG"
__date__ ="$Dec 14, 2010 2:18:18 PM$"

# Function actional() takes 3 parameters: addActional - TRUE/FALSE, clusterName - a WebSphere cluster name or "ALL", interceptorPath - path to uplink file
def actional(addActional, clusterName, interceptorPath):
    #print "DEBUG: START: Actional:"
    print "Entering the Actional Configuration Process...\n"

    clusterList = AdminConfig.list('ServerCluster')
    for clusterId in clusterList.split("\r\n"):

        #Initialize Variables - these cannot be global to the loop because they need to be reset for every JVM
        simpleClassPath = "J:/Actional/ActionalAgent/interceptors/ws/actional-http-interceptor.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-jdbc-interceptor.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-jms-interceptor.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-log4j-interceptor.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-sdk.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-servlet-interceptor.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-spring-ws-interceptor.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-ws-ejb-interceptor.jar;J:/Actional/ActionalAgent/interceptors/ws/actional-ws-soap-interceptor.jar;"
        bootClassPath = "J:/Actional/ActionalAgent/interceptors/ws/actional-ws-ejb-interceptor-boot.jar"
        genJVMArgs = "-javaagent:J:/Actional/ActionalAgent/interceptors/ws/actional-plugmaker.jar -Dorg.omg.PortableInterceptor.ORBInitializerClass.com.actional.lg.interceptor.websphere.v60.ORBInitializer -Dcom.actional.aops=com/actional/lg/interceptor/sdk/helpers/InterHelpJaxJIT.aop,com/actional/lg/interceptor/websphere/websphere.aop,com/actional/lg/interceptor/websphere/ibmorb.aop,com/actional/lg/interceptor/websphere/ejb-audit.aop,com/actional/lg/interceptor/jdbc/jdbc.aop,com/actional/lg/interceptor/jms/jms.aop,com/actional/lg/interceptor/axis/Axis-jit.aop,com/actional/lg/interceptor/log4j/log4j.aop,com/actional/lg/interceptor/j2ee/j2ee.aop,com/actional/lg/interceptor/http/client/jakarta2.aop -Dcom.actional.lg.interceptor.jms.queueGroupings=MessageBroker::$ISYS.USERS.Temporary*=,MgmtBroker1::SonicMQ.mf.JNDICLIENT*= -Dcom.actional.lg.interceptor.config=" + interceptorPath

        curClusterName = AdminConfig.showAttribute(clusterId, 'name')
        if((clusterName.upper() == "ALL") | (clusterName == curClusterName)):
            members = AdminConfig.showAttribute(clusterId, 'members')
            memberList = members[1:len(members)-1].split(" ")
            for member in memberList:
                jvmName = AdminConfig.showAttribute(member, 'memberName')
                nodeName = AdminConfig.showAttribute(member, 'nodeName')
                nodeVersion = AdminTask.getNodeBaseProductVersion('[-nodeName ' + nodeName + ']')
                nodeShortVersion = int(nodeVersion[0]+nodeVersion[2])

                #Complete classPath definition which is dependent on WAS version
                if(nodeShortVersion == 70):
                    classPath = simpleClassPath + "J:/IBM/WebSphere70/AppServer64/lib/j2ee.jar"
                elif((nodeShortVersion == 61) & (nodeName.find("64") >= 0)):
                    #For WAS 6.1 64-bit, this clause of the classpath needs to be removed - subject to change in the future
                    simpleClassPath = simpleClassPath.replace("J:/Actional/ActionalAgent/interceptors/ws/actional-log4j-interceptor.jar;", "")
                    classPath = simpleClassPath + "J:/IBM/WebSphere61/AppServer64/lib/j2ee.jar"
                elif((nodeShortVersion == 61) & (nodeName.find("32") >= 0)):
                    classPath = simpleClassPath + "J:/IBM/WebSphere61/AppServer32/lib/j2ee.jar"
                else:
                    print "Exception: Actional provided for WAS version 6.1 and 7.0 only."
                    raise Exception, "Script raised exception - Improper WAS version."

                #Define variables for JVM parameters
                serverId = AdminConfig.getid('/Node:' + nodeName + '/Server:' + jvmName + '/')
                jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
                origClassPath = AdminConfig.showAttribute(jvmId, 'classpath')
                origBootClassPath = AdminConfig.showAttribute(jvmId, 'bootClasspath')
                origJVMArgs = AdminConfig.showAttribute(jvmId, 'genericJvmArguments')

                #Initialize variables
                if(origClassPath == '[]'):
                    origClassPath = ""
                if(origBootClassPath == '[]'):
                    origBootClassPath = ""
                if(origJVMArgs == None):
                    origJVMArgs = ""

                modifyClassPath = 0
                modifyBootClassPath = 0
                modifyGenJVMArgs = 0

#==========================================================================================================================
#Addition Section
		if(addActional.upper() == "TRUE"):
                    #Generate Classpath
                    if(origClassPath != ""):
                        if(origClassPath.find(classPath) < 0):
                            classPath = origClassPath + " " + classPath
                            modifyClassPath = 1
                    else:
                        modifyClassPath = 1

                    #Generate Boot Classpath
                    if(origBootClassPath != ""):
                        if(origBootClassPath.find(bootClassPath) < 0):
                            bootClassPath = origBootClassPath + " " + bootClassPath
                            modifyBootClassPath = 1
                    else:
                        modifyBootClassPath = 1

                    #Generate the Generic JVM Arguments
                    if(origJVMArgs != ""):
                        if(origJVMArgs.find(genJVMArgs) < 0):
                            genJVMArgs = origJVMArgs + " " + genJVMArgs
                            modifyGenJVMArgs = 1
                    else:
                        modifyGenJVMArgs = 1

                    #Print JVM and which parameters will be modified
                    print "JVM: " + jvmName
                    print "Modify Classpath: " + modifyClassPath.toString()
                    print "Modify Boot Classpath: " + modifyBootClassPath.toString()
                    print "Modify Generic JVM arguments: " + modifyGenJVMArgs.toString() + "\n"

                    #Add to Classpath
                    if(modifyClassPath == 1):
                        AdminConfig.modify(jvmId, [['classpath', classPath]])
                        print "INFO: Actional: Modified Classpath from: " + origClassPath + " to " + classPath + "\n"
                    else:
                        print "Actional has already been added to Classpath." + "\n"
                    #Add to Boot Classpath
                    if(modifyBootClassPath == 1):
                        AdminConfig.modify(jvmId, [['bootClasspath', bootClassPath]])
                        print "INFO: Actional: Modified Boot Classpath from: " + origBootClassPath + " to " + bootClassPath + "\n"
                    else:
                        print "Actional has already been added to Boot Classpath." + "\n"
                    #Add to Generic JVM Args
                    if(modifyGenJVMArgs == 1):
                        AdminConfig.modify(jvmId, [['genericJvmArguments', genJVMArgs]])
                        print "INFO: Actional: Modified Generic JVM Arguments from: " + origJVMArgs + " to " + genJVMArgs + "\n"
                    else:
                        print "Actional has already been added to Generic JVM Arguments." + "\n"

#==========================================================================================================================
#Removal Section
                elif(addActional.upper() == "FALSE"):
                    print "JVM: " + jvmName + ":"
                    #Remove from Classpath
                    if(origClassPath.find(classPath) >= 0):
                        newClassPath = origClassPath.replace(classPath, '')
                        AdminConfig.modify(jvmId, [['classpath', newClassPath]])
                        print "INFO: Actional: Modified Classpath from: " + origClassPath + " to " + newClassPath + "\n"
                    else:
                        print "Actional has already been removed from Classpath." + "\n"

                    #Remove from Boot Classpath
                    if(origBootClassPath.find(bootClassPath) >= 0):
                        newBootClassPath = origBootClassPath.replace(bootClassPath, '')
                        AdminConfig.modify(jvmId, [['bootClasspath', newBootClassPath]])
                        print "INFO: Actional: Modified Boot Classpath from: " + origBootClassPath + " to " + newBootClassPath + "\n"
                    else:
                        print "Actional has already been removed from Boot Classpath." + "\n"

                    #Remove from Generic JVM Args
                    if(origJVMArgs.find(genJVMArgs) >= 0):
                        newGenJVMArgs = origJVMArgs.replace(genJVMArgs, '')
                        AdminConfig.modify(jvmId, [['genericJvmArguments', newGenJVMArgs]])
                        print "INFO: Actional: Modified Generic JVM Arguments from: " + origJVMArgs + " to " + newGenJVMArgs + "\n"
                    else:
                        print "Actional has already been removed from Generic JVM Arguments." + "\n"
                else:
                    print "Exception: Actional: Improper Actional add/remove param."
                    raise Exception, "Script raised exception - Improper Actional enable/disable param."

    print "Exiting the Actional Configuration Process..."
    return

###============DEBUG==============###
#actional("false", "MessageManager")
###===============================###