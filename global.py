global AdminApp
global AdminTask
global AdminConfig
global AdminControl

import sys
import time
import org.w3c.dom as dom
import org.apache.xerces as xerces
import org.python.modules.re as re
import java

cellName = AdminControl.getCell()
cellId   = AdminConfig.getid('/Cell:' + cellName + '/')
lineSep  = java.lang.System.getProperty('line.separator')

global DMGR, STANDALONE, MGRNODENAME, SAVE