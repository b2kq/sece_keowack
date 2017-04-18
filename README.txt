WARNING
  0. The scripts exit out on first failure without saving anything, this is an intended feature.
  1. The scripts are not destructive, and try to get a best effort.
  2. You need to understand the XML flow, especially when using BUILD/BOTH options.
  3. Be very careful with the scope because, as long as the scope you provide exists, even wrong, the resource will be built/modified.
  4. To test BUILD/BOTH/DEPLOY options, invoke with a "nosave".  This will make the scripts run their course, 
     but not save anything and quit.
     Ex: wsadmin -lang jython -f main.py J:\promotion\properties\abcdApp.xml build nosave

For DEBUGGING, or VERBOSE mode, do the following.  This will invoke a print statement at the begin and end of every function.
Ofcourse, if a function returns a value due to some condition in the middle, without reaching the end, you will not see 
the DEBUG: END: statement.
  0. Make sure that none of the files under J:/promotion/jython/*.py are open, if open close them.
  1. Open a command window.
  2. "cd J:\promotion\jython"
  3. "verbose.bat on" to turn on debugging.
  4. "verbose.bat off" to turn off debugging.
Also, the DEBUG/VERBOSE mode will not enable debugging of the function getTagValue() in xml.py.
Enabling DEBUG of that function will clutter the output with a lot of START/END statements, due to the number of times it is invoked.

J2C Resource Adapters (CICS, IMS, Sonic, ...)
  1. Copy the rar files to every node (and set the proper path in the xml sheet before attempting to build them.
  2. Some rar's like Sonic might require copying of some extra libraries into lib/ext and restarting the nodeagent processes,
     before you can attempt to install the rar.

LIMITATIONS
These limitations have been identified based on the KAH application needs only.
  1. The SIB build/create functions only create resources.  They do not check for existing and modify.
     So you will see failures when you run SIB stuff a 2nd time or more.
  2. There is no delete feature.  If you want to delete something, do it manually via the admin console.

PMI.py
  1. The PMI tasks are stand-alone and not integrated into the XML property sheets (this is intentional).
  2. Basic PMI is by default enabled on all JVMs, WAS 6.0 upwards; this script does the same task.
  3. They are provided so you have a quick way to trun it on/off when needed in a JVM, cluster, or all clusters in the cell.

HAMGR.py
  1. The hamgr script is stand-alone, although the XML supports hamgr thru jvm.py
  2. hamgr scripts are provided so you have a quick way to turn it on/off when needed.

CHANGEMONITOR.py
  1. The changemonitor script is stand-alone, although the XML supports changemonitoring thru jvm.py
  2. It provides a quick way to change JVM monitoring settings.

JVMTASK.py
  1. jvmTask.py is stand-alone, although the XML supports it thur jvm.py
  2. It can be used to perform tasks on individual JVMs like start, stop, heapdump, javacore, etc.

ClassPaths must use the backslash \ and not the forward slash /.