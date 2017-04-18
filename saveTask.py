# This is a stand-alone script
# Depends on global.py, and saveOperations.py

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/saveOperations.py")

saveSync("fullresync")