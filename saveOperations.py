def saveSync(syncType):
    #print "DEBUG: START: saveSync"

    if((syncType != "sync") & (syncType != "fullresync")):
        print "Exception: saveSync: Bad sync parameter: " + syncType
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    if(AdminConfig.hasChanges() == 0):
        print "INFO: saveSync: No changes made to configuration, nothing to save"
    else:
        print "INFO: saveSync: Saving changes..."
        AdminConfig.save()
        #time.sleep(60)

    print "INFO: saveSync: Starting sync"
    mNodeList = AdminTask.listManagedNodes()
    if(mNodeList == ""):
        print "INFO: saveSync: No managed nodes to sync"
        return

    for nodeName in mNodeList.split(lineSep):
        iter = [1,2,3,4]
        for x in iter:
            # Get the node sync MBean object
            nodeSyncObj = AdminControl.queryNames('type=NodeSync,node=' + nodeName + ',*')
            # If it's not empty, run thru the sync steps
            if(nodeSyncObj != ""):
                # If sync and node is already synchronized, continue with next node
                if(syncType == "sync"):
                    if(AdminControl.invoke(nodeSyncObj, 'isNodeSynchronized')):
                        print "INFO: saveSync: Node " + nodeName + " is already synchronized"
                        break
                # If fullresync, refresh the repository epoch for the node
                if(syncType == "fullresync"):
                    nodeRepositoryObj = AdminControl.completeObjectName('type=ConfigRepository,node=' + nodeName + ',process=nodeagent,*')
                    AdminControl.invoke(nodeRepositoryObj, 'refreshRepositoryEpoch')
                    print "INFO: saveSync: The repository epoch is refreshed for node " + nodeName
                # Issue a sync, and check if it succeeded
                if(AdminControl.invoke(nodeSyncObj, 'sync')):
                    if(AdminControl.invoke(nodeSyncObj, 'isNodeSynchronized')):
                        print "INFO: saveSync: Synced node " + nodeName
                    else:
                        print "Exception: saveSync: Unable to obtain sync status for node " + nodeName
                        raise Exception, "Script raised exception, you are doing something wrong!!!"
                else:
                    print "Exception: saveSync: Synchronization of node " + nodeName + " failed, or did not respond in a timely fashion"
                    raise Exception, "Script raised exception, you are doing something wrong!!!"
                break
            # If it's empty and this is the 4th iteration, throw an error message, and continue with next node
            if((nodeSyncObj == "") & (x == 4)):
                print "Exception: saveSync: mbean is not running for node " + nodeName + " , continuing with next node"
                break
            print "INFO: saveSync: Waiting 60 sec for node sync MBean object"
            sleep(60)

    #print "DEBUG: END: saveSync"
    return

def toogleAutoSync(flag):
    #print "DEBUG: START: toogleAutoSync"

    if((flag.upper() == "TRUE") | (flag.upper() == "FALSE")):
        mNodeList = AdminTask.listManagedNodes().split(lineSep)
        for nodeName in mNodeList:
            nodeObj = AdminControl.completeObjectName('type=NodeSync,node=' + nodeName + ',*')
            AdminControl.setAttribute(nodeObj, 'autoSyncEnabled', flag)
            print "INFO: toogleAutoSync: Auto sync for " + nodeName + " changed to " + flag
    else:
        print "Exception: toogleAutoSync: Bad toogle paramer passed; accepts only true/false"
        raise Exception, "Script raised exception, you are doing something wrong!!!"

    #print "DEBUG: START: toogleAutoSync"
    return