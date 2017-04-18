# This is a stand-alone script
# Depends on global.py, actional.py and saveOperations.py

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/actional.py")
execfile(JYTHON_HOME+"/saveOperations.py")

actional(sys.argv[0], sys.argv[1], sys.argv[2])
if(len(sys.argv) == 4):
    if(sys.argv[3].upper() == "SAVE"):
        saveSync("sync")