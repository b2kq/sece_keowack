#  To use:  wsadmin>execfile('/MainV2.py')
#  State:   work in progress, major revision
#  Purpose:  Given application name, create properties file for 
#			application installation in current environment, 
#			that is the environment this script is running in.  
#  Assumptions:
#	x)  assumes jython home is at /promotion/jython 
#		and all dependencies are rooted there
#	x)  Application name is case sensitive.
#	x)  EAR file name is the application name plus '.ear' suffix

#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
import sys
processStage = ['Preamble']
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
codeVersion = '2.00'
#  Programming notes:
#	x)  house of cards, to debug the old code is changed, after debug, 
#		the old code is changed again
#	x)  function managerCheck is used only once

if  ''.join(['print', ' "DEBUG:', ' START', ' "']) == '#print "DEBUG: START "':
	# supports backward compatibility with verbose.bat
	debug = 1
	#  Debug, set variable debug to 1 (true) to display debug information.
	#  Can be done both interactively and programmatically.
try:
	if  sys.argv:
		if sys.argv[-1].upper() == 'DEBUG': DEBUG = (sys.argv.pop().upper() == 'DEBUG')
	DEBUG = DEBUG
	if DEBUG: 
		debug=DEBUG 
	debug=debug
except: debug=0 

#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
# Formats messages for readability.  Any program that maintains a stacked array
# called processStage, can use these routines to organize output in a consistent
# manner.  Especially useful when using printDebugLine to identify called and/or
# looping processes.  
# messages with indention similar to how python/jython manages layers.
# printDebugLine("start") prints new stage starting, 
#   assumes processStage.append( "new stage comment" ) executed prior to call 
# printDebugLine("end") print stage ended, pops the stage name from processStage
# printDebugLine(string) if debug is true, print sting to standard out
# printInfoLine(string) prints comment with indention and tag to standard out
# printWarningLine(string) prints comment with indention and tag to standard out
# printErrorLine(string) prints comment with indention and tag to standard error
# printSevereLine(string)  prints comment with indention and tag to standard error
# printToDoLine(string) prints comment with indention and tag to standard error
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
try:
	processStage = processStage
except:
	processStage = ['Default Initialization']
if not isinstance(processStage, type([])):
	sys.stderr.write(' WARNING: processStage not a list of strings, printTagLine will not work.\n')
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
def printTagLine(toStdErr, tagIndent, tagString, comment):
	outputLine = ''.join([tagString,'  ' * tagIndent,comment,'\n'])
	if  toStdErr:
		sys.stderr.write(outputLine)
	else:
		sys.stdout.write(outputLine)
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
def printDebugLine(comment):
	if comment == 'end' : endedStage = processStage.pop()
	if debug:
		debugIndent = len(processStage)
		if comment == 'end':
			printTagLine(0, debugIndent,	 '  Debug: ', ' '.join(['> End stage>',endedStage]))
		elif comment == 'start':
			printTagLine(0, debugIndent - 1, '  Debug: ', ' '.join(['Begin stage>',processStage[-1]]))
		elif comment != '':
			printTagLine(0, debugIndent,	 '  Debug: ', comment)
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
def printInfoLine(comment):
	printTagLine(0, len( processStage ), '   Info: ', comment)
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
def printWarningLine(comment):
	printTagLine(0, len(processStage), 'Warning: ', comment)
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
def printErrorLine(comment):
	printTagLine(1, len(processStage), '  ERROR: ', comment)
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
def printSevereLine(comment):
	printTagLine(1, len(processStage), ' SEVERE: ', comment)
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
def printToDoLine(comment):
	printTagLine(1, len(processStage), '  To do: ', comment)
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

if debug: sys.stdout.write('\n=== === === === ===\n  DEBUG: debug==true detected.  Expect verbose output.\n')
printDebugLine('start')
printDebugLine(codeVersion.join(['MainV2.py ','.']))

JYTHON_HOME = "J:/promotion/jython"
printDebugLine(' '.join(['JYTHON_HOME =',JYTHON_HOME]))

printInfoLine(codeVersion.join(['Version ',' of MainV2.']))
printDebugLine('Version 2 added functionality for generating property sheets.')
printDebugLine('Version 2 added functionality inline and programmatic debugging.')

#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
printDebugLine('end')
processStage.append('Global settings')
printDebugLine('start')
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
global AdminApp, AdminTask, AdminConfig, AdminControl
global DMGR, STANDALONE, MGRNODENAME, SAVE

import sys
import traceback
import time
import re
import org.apache.xerces.parsers.DOMParser as xerces
import org.xml.sax

#TODO line.separator obsolete?
#lineSep = java.lang.System.getProperty('line.separator')

#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
printDebugLine('end')
processStage.append('Local function definitions(s)')
printDebugLine('start')
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

printDebugLine('defining usageException()')
class usageException:
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return `self.value`

printDebugLine('defining usage()')
def usage():
		sys.stderr.write( '\n  Usage: wsadmin.bat -p wsadmin.properties -f MainV2.py <ENV> <appName.xml> <task> {SAVE}\n\n' )
		sys.stderr.write( '		 wsadmin.bat is WAS admin command line interface for environment, \n' ) 
		sys.stderr.write( '			as of this writting, found at\n')
		sys.stderr.write( '			\\\\usgobtdeploy40\\J$\\IBM\\WebSphere70\\AppServer64\\bin.\n\n' )
		sys.stderr.write( '		 -p wsadmin.properties is specific properties for the environment,\n' )
		sys.stderr.write( '			eg J:\promotion\properties\DEV3Was\wsadmin.properties\n\n' )
		sys.stderr.write( '		 -f MainV2.py is this script,\n' )
		sys.stderr.write( '			eg J:\promotion\jython\MainV2.py\n\n' )
		sys.stderr.write( '		 <ENV> is required keyword, identifies the environment, \n' )
		sys.stderr.write( '			eg DEVwas, DEV1was, SysTestwas, UATwas, or Prodwas.\n\n' )
		sys.stderr.write( '		 <appName.xml> is required case sensitive application\'s properties\n' )
		sys.stderr.write( '			XML file name, eg RPW_App.xml\n\n' )
		sys.stderr.write( '		 <task> is required keyword, specifies one of following actions: \n' )
		sys.stderr.write( '			BUILD the application server(s) but do not deploy the application.\n' )
		sys.stderr.write( '			DEPLOY the application to the environment.\n' )
		sys.stderr.write( '			BOTH means BUILD and DEPLOY.\n' )
		#sys.stderr.write( '			START the application.\n' )
		#sys.stderr.write( '			STOP the application .\n' )
		#sys.stderr.write( '			JAVACORE issues a core dump request to all application\'s servers will be dumped.\n' )
		#sys.stderr.write( '			HEAPDUMP issues a heap dump request to all the application\'s servers.\n' )
		#sys.stderr.write( '			STOPIMMEDIATE kills the application\'s servers.\n' )
		#sys.stderr.write( '			RIPPLE issues a ripple (re)start request of all application servers.\n' )
		#sys.stderr.write( '			STATUS request of all application\'s servers.\n' )
		sys.stderr.write( '		 \n' )
		sys.stderr.write( '		 {SAVE|NOSAVE} optional parameter specifies that saves configuration,\n' ) 
		sys.stderr.write( '			 not saving is the default.\n\n' )
		#sys.stderr.write( '		 {DEBUG} optional turns on debug messages.\n\n' )
		return

printDebugLine('defining managerCheck()')
def managerCheck():
	DMGR		= "TRUE"
	STANDALONE  = "FALSE"
	CLUSTERED   = "TRUE"
	MGRNODENAME = AdminControl.getNode()
	cellName	= AdminControl.getCell()
	cellId	  = AdminConfig.getid(''.join(['/Cell:', cellName, '/']))
	processType = AdminControl.getAttribute(
					AdminControl.completeObjectName(
					  ''.join(['type=Server,node=',MGRNODENAME,',cell=',cellName,',*'])),
					'processType')
	
	if  processType == "DeploymentManager":
		printInfoLine(' '.join(['managerCheck: Connected to a deployment manager',MGRNODENAME]))
	elif processType == 'ManagedProcess' or processType == 'NodeAgent':
		printDebugLine(''.join(['Connected to ',processType,': ',MGRNODENAME]))
		printSeverLine('This deployment needs to be to a deployment manager or unmanaged process.')
		raise Exception, "Script raised exception, not able to continue."
	elif processType == 'UnManagedProcess':
		printInfoLine(''.join(['managerCheck: Connected to an UnManagedProcess:',MGRNODENAME]))
		DMGR = "FALSE"
		STANDALONE = "TRUE"
	
	return

printDebugLine('defining parseDOM()')
def parseDOM(thisNode):
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	# Recursive function parses a xerces DOM document into a:
	#	list of dictionaries of parent (there can be only one for thisNode) ...
	#		who have lists of one or more dictionaries of children ...
	#			there are lists of more childrent and/or lists one or more dictionaries of keys ...
	#				which/who have a list of values that are strings
	# [{parent:[{child}:[{key:[value, value, ...], key:[], ...}, {}, ...], child:...,  ...]}]
	#
	# Usage:  can do an entire document, but for large documents, it is probably easier
	#	more efficient to 'slice' up major branches, e.g.:
	#		import org.apache.xerces.parsers.DOMParser as xerces
	#		xmlParser = xerces()
	#		xmlParser.parse(xmlFile)
	#		majorElement = xmlParser.document.getElementsByTagName('majorTag').item(0)
	#		parseDOM(majorElement) 
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	if thisNode == None: return None
	try:
		parentName = thisNode.parentNode.nodeName
	except:
		printSevereLine(''.join(['parseDOM issue with ', str(thisNode)]))
		return None
	thisName = thisNode.nodeName
	### starting with blank list, thisNode, its (only one) parent, probably an element, may have children
	nodeList = []
	if  thisNode.hasChildNodes():
		### node has children so we walk down the tree ...
		if  thisNode.length == 1:
			### end of the line, there can only be a string value, and never empty
			value = thisNode.item(0).nodeValue
			### TODO uncomment following debug print
			#if debug: sys.stdout.write( '  DEBUG: parseDOM() parsed ' + parentName + '/' + thisName + ': ' + value + '.\n' )
			nodeList.append({thisName:[value]})
		else:
			### more than single string, probably more children ...
			for index in range(thisNode.length):
				### each item could be 1:element, 2:attribute, 3:text, or 8:comment.  9:document would only apply to top node 
				item = thisNode.item(index)
				if  item.nodeType == 1:
					### item is an element so we recurse 
					childNode = parseDOM(item)
					### childNode is a list of dictionaries, but thisNode is the only parent of the child
					### that is, thisNode.nodeName = thisName = childNode[0].keys()[0]
					### every child is a dictionary of element lists and/or a dictionary member that has a list of strings
					for child in childNode[0].keys():
						### for every child there are one or more keys, some keys could be the same, when so, all their values must be listed
						if  len( childNode[0][child] ) < 1 : 
							### child of length 0 is means no value, going to try to put empty string, using key of item.nodeName
							childNode[0][child] = [{item.nodeName:['']}]
							#continue
						for key in childNode[0][child][0].keys():
							value = childNode[0][child][0][key][0]
							if  nodeList == []:  nodeList = [{child:[{}]}]
							if  nodeList[0][child][0].has_key(key):
								### commented out as it adds significant output 
								#if  debug: sys.stdout.write( '  DEBUG: parseDOM() duplicate key found, appending value ...\n' )
								nodeList[0][child][0][key].append(value)
							else:
								nodeList[0][child][0][key] = [value]
							### commentd out as it adds tons of output
							#if  debug: sys.stdout.write( '  DEBUG: parseDOM() parent/child/key/value/ = ' + parentName + '/' + child + '/' + key + '/' + str( value ) + '/\n' )
	return [{parentName:nodeList}]
printDebugLine('end')

#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
processStage.append('Main')
printDebugLine('start')
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
try:
	global SAVE
	SAVE = 0
	argLength = len(sys.argv)

	if debug: 
		sys.stdout.write('  Debug: ')
		if argLength == 0: sys.stdout.write('  No parameters passed.\n')
		else:
			sys.stdout.write('  Parameters passed: ')
			for parameter in sys.argv:
				sys.stdout.write(parameter + ' ')
			sys.stdout.write('\n')

	if   argLength < 2:
		 raise usageException, "  Not enough parameters."
	elif argLength > 4:
		 raise usageException, "  Too many parameters."
	elif argLength == 4:
		 if   sys.argv[3].upper() == 'SAVE':  SAVE = 1
		 elif sys.argv[3].upper() != 'NOSAVE': raise usageException, "4th parameter must be either SAVE or NOSAVE"
	environment = sys.argv[0]
	xmlFile = sys.argv[1]
	task = sys.argv[2].upper()
	if debug: sys.stdout.write('  Debug:   environment = ' + environment + ', xmlFile = ' + xmlFile + ', task = ' + task + ', SAVE = ' + str(SAVE) + '\n')

	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	processStage.append('Inclusions')
	printDebugLine('start')
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	#for inclusion in [ 'global', 'jvm', 'security', 'transport', 'datasource', 'idm', 'application', 'buildEnv', 
	#	'scope', 'ra', 'xml', 'common', 'resource', 'sib', 'webserver', 'saveOperations', 'jms', 'wily', 'jvmOperations' ]:
	#for inclusion in ['security', 'resource', 'scope', 'applicationV2', 'buildEnvV2', 'ra', 'transport', 'jvm',
	for inclusion in ['security', 'resource', 'scope', 'application', 'buildEnvV2', 'ra', 'transport', 'jvm',
		  'datasource', 'common', 'resource', 'jms', 'saveOperations']:
		inclusion = ''.join([JYTHON_HOME, '/', inclusion, '.py'])
		printDebugLine('Executing ' + inclusion)
		try:
			execfile(inclusion)
		except:
			printWarningLine(' '.join([inclusion, 'failed (may not be found), continuing...']))
	printDebugLine('end')
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

	printDebugLine('managerCheck(), verifying connection ...')
	managerCheck()

	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	processStage.append('Read properties XML')
	printDebugLine('start')
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	xmlParser = xerces()
	xmlParser.parse('J:/promotion/properties/' + environment + '/' + xmlFile)
	# commented out following in support original WebServer build function
	#rootElement = xmlParser.document.getElementsByTagName( 'WAS' ).item(0)
	#parsedDOM = parseDOM( rootElement )
	rootElement = xmlParser.document
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
	printDebugLine('end')
	#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#

	# Invoke the required task, BUILD before DEPLOY
	if task == "BUILD"  or task == "BOTH" :  buildTask(None, rootElement)
	#if task.upper() == "DEPLOY" or task.upper() == "BOTH" :  appInstall(environment, xmlFile[0:sys.argv[1].index('.')], rootElement.getElementsByTagName("mod-info").item(0))
	if task == "DEPLOY" or task == "BOTH" :  appInstall(rootElement.getElementsByTagName('WAS').item(0))
#	
#	if(re.search(task, "START/STOP/JAVACORE/HEAPDUMP/STOPIMMEDIATE/RIPPLE/STATUS/RESTART") != None):
#		appSvrNode = rootElement.getElementsByTagName("ApplicationServer").item(0)
#		if(appSvrNode != None):
#			clusterName = getTagValue(appSvrNode, 'ClusterName')
#			clusterOp(clusterName, task)
#		else:
#			print "ERROR: main: ClusterName node not found in XML property sheet"
#			raise Exception, "Script raised exception, you are doing something wrong!!!"   
#	else:
#		print "ERROR: main: Bad input parameters"
#		raise Exception, "Script raised exception, you are doing something wrong!!!"
#
except usageException, e:
	usage()
	printSevereLine('Can not continue.  Parameters not recognized.')
except java.io.FileNotFoundException, e:
	traceback.print_exc()
	printSevereLine('File not found exception, can not continue.')
except org.xml.sax.SAXParseException, e:
	traceback.print_exc()
	printSevereLine('SAX parse exception, can not continue.')
except:
	traceback.print_exc()
	printSevereLine('Unknown error, can not continue.')

#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
printDebugLine('end')
if debug: sys.stdout.write('  Debug: End of script.\n')
if debug: sys.stdout.write('=== === === === ===\n\n')
#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#===+===#
