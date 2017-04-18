def disableAIO(jvmName, nodeName):
    #print "DEBUG: START: disableAIO"

    jvmId = AdminConfig.getid("/Node:" + nodeName + "/Server:" + jvmName)
    svc = AdminConfig.list('TransportChannelService', jvmId)
    print AdminConfig.showAttribute(svc, 'factories')
    fact = AdminConfig.create('TCPFactory', svc, [])
    AdminConfig.create('Property', fact, [['name', 'commClass'], ['value', 'com.ibm.ws.tcp.channel.impl.NioTCPChannel']])
    print AdminConfig.showAttribute(svc, 'factories')

    #print "DEBUG: END: disableAIO"
    return

#AdminConfig.save()