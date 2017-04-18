###
#  Name: deploy.py
#  Description: used to deploy application to the USG managed infrastructure
#  Version: 0.01
#  Usage:  deploy <applicationName> {noSave|save} 
#  Notes:  to debug edit debug.py to 'turn on' the global debug flag
#  Author:  RShen 
###

### The Initialization

# Jython/Python built in and standard modules
import sys
import time
import java
import org.python.modules.re  as re

# Additional 3rd party modules
import org.w3c.dom            as dom
import org.apache.xerces      as xerces

# IBM specific modules
global AdminApp
global AdminTask
global AmdinConfig
global AdminControl

# Unitrin Services Group written modules
lineSep  = java.lang.System.getProperty( 'line.separator' )
returnCode = 0
try:
    import debug
except:
    sys.stderr.write( 'Warning:  not able to read debug flag from debug.py, setting it to false.' + lineSep )
    global DEBUG
    DEBUG = ( 'true' != 'true' )

global DMGR, STANDALONE, MGRNODENAME, SAVE
nodeName = AdminControl.getNode()
cellName = AdminControl.getCell()
processType = AdminControl.getAttribute( AdminControl.completeObjectName( 'type=Server,node=' + nodeName  + ',cell=' + cellName + ',*' ), 'processType' )

if DEBUG == 1 : 
    sys.stderr.write( 'DEBUG:  node name is ' + nodeName + lineSep )
    sys.stderr.write( 'DEBUG:  cell name is ' + cellName + lineSep )
    sys.stderr.write( 'DEBUG:  type name is ' + processType + lineSep )

### The Start

if DEBUG :
    sys.stderr.write( 'DEBUG:  debug flag detected as true, this should print to stderr.' + lineSep )
else:
    sys.stdout.write( 'End of line.' + lineSep )
    
### The End