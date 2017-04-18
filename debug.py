    ### 
    #  debug.py
    #  version 1.0
    #  sets global boolean variable DEBUG, change and save
    #  subsequent routines that support DEBUG should 
    #  print relative debugging information to sys.stderr.    
    #  Author:  RShen
    ###
    
global DEBUG
DEBUG = ( 'true' == 'false' )
DEBUG = not DEBUG     # Comment out this line to set debug to true
