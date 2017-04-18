# This is a stand-alone script
# Depends on global.py and jvmOperations.py

JYTHON_HOME = "J:/promotion/jython"
execfile(JYTHON_HOME+"/global.py")
execfile(JYTHON_HOME+"/jvmOperations.py")

JVMOp(sys.argv[0], sys.argv[1], sys.argv[2])	