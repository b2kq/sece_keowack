#  Special routine to configure specific (WAS 6.1) applications ORB_LISTENER_PORT to assigned numbers
#  Limited use.  
#  Application names are hard coded.  
#  Port numbers are seeded between 0 and 32.
#  SysTest will get ports 9933 - 9965
#  Int will get ports 9966 to 9998
#  All other envinronments will use ports 9900 - 9932
#  Port 9999 is allocated but not assigned

orbListenerPort = { 
    'AgencyContact'             :  0, 
    'AgentAlerts'               :  1, 
    'AgentDocuments'            :  2, 
    'AgentInside'               :  3, 
    'AgentInsideDoc'            :  4, 
    'AgntPlcySrvcs'             :  5, 
    'AMIInqSvcs'                :  6,
    'ClaimCenter'               :  7, 
    'ClaimInquiry'              :  8, 
    'ClaimsService'             :  9, 
    'ContactCenter'             : 10, 
    'ContentMgmt'               : 11, 
    'CoverageConfirmation'      : 12, 
    'CoverageConfirmationPERS'  : 13, 
    'CQService'                 : 14, 
    'CustomerManager'           : 15, 
    'CustomerWeb'               : 16, 
    'CustomerWebService'        : 17, 
    'DMVCC'                     : 18, 
    'DocumentWebServices'       : 19, 
    'EventJournal'              : 20,
    'FormsLibrary'              : 21, 
    'HostOnDemand'              : 22,
    'IdentityManager'           : 23, 
    'IDMPublic'                 : 24, 
    'IDMSecure'                 : 25, 
    'KemperBillingSystem'       : 26, 
    'PaymentService'            : 27, 
    'ProducerService'           : 28,
    'RPW6FrontEnd'              : 29, 
    'RPW6WebSvc'                : 30, 
    'XAG'                       : 31,
    'Available'                 : 32 
    }

cellName = AdminControl.getCell()

for applicationName in orbListenerPort.keys():
    for entry in AdminConfig.list( 'ServerEntry', applicationName + '_*' ).split():
        serverName = AdminConfig.showAttribute( entry, 'serverName' )
        for special in AdminConfig.showAttribute( entry, 'specialEndpoints' )[ 1 : -1 ].split():
            if AdminConfig.showAttribute( special, 'endPointName' ) == 'ORB_LISTENER_ADDRESS':
                port = orbListenerPort[ applicationName ]
                if    cellName == 'KAHINT' :
                    port = port + 9966
                elif  cellName == 'KAHSYSTEST' : 
                    port = port + 9933
                else: 
                    port = port + 9900
                try:
                    AdminConfig.modify( AdminConfig.showAttribute( special, 'endPoint' ), [[ 'port', str( port ) ]] )
                except:
                    sys.stderr.write( 'ERROR:  ' + serverName +', AdminConfig.modify( ' + AdminConfig.showAttribute( special, 'endPoint' ) + ", [[ 'port', str( " + str( port ) + ' ) ]] )\n' )
                    continue
                sys.stdout.write( ' INFO:  ' + serverName + ' ORB listener port set to ' + str( port ) + '\n' )
                # end ORB_LISTENER_ADDRESS changes
            # end special end point loop
        # end server entry loop
    # end application loop

sys.stdout.write( ' INFO: End of job.  Changes are staged, a save (AdminConfig.save()) is required to commit the changes.\n' )
