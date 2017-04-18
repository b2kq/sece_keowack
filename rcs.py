import re

lineSep = '\r\n'
appName = 'RPW_App'


#
#  To use:  wsadmin>execfile('/rcs.py')
#

print '<EnterpriseApplication>' + lineSep

print '\t<EMail>'
print '\t\t<To><\To>'
print '\t</EMail>' + lineSep

print '\t<ear-info>'
print '\t\t<ear-name>' + appName + '.ear</ear-name>'
print '\t\t<app-name>' + appName + '</app-name>'
print '\t</ear-info>' + lineSep

print '\t<mod-info>'
print

try:
    for moduleRaw in AdminApp.listModules( appName, '-server' ).split( lineSep ):
        isEJB =  ( re.search( r'\+META-INF/ejb-jar\.xml', moduleRaw ) != None )
        isWAR =  ( re.search( r'\+WEB-INF/web\.xml', moduleRaw ) != None )
        fileName = re.search( r'(?<=#)\w+\.[jw]ar', moduleRaw ).group(0)
        display  = re.sub(    '_', ' ', re.search( '\w+', fileName ).group(0) )
        display  = re.search( '\w+', fileName ).group(0)
        clusters = re.findall( r'(?<=cluster=)\w+', moduleRaw )
        #print 'DEBUG:  app module = ' + moduleRaw
        print '\t\t<module>'
     
        if isEJB:
            print '\t\t\t<ejb>'
            print '\t\t\t\t<ejb-file-name>' + fileName + '</ejb-file-name>'
     
        if isWAR:
            print '\t\t\t<web>'
            print '\t\t\t\t<war-file-name>' + fileName + '</war-file-name>'
        
        print '\t\t\t\t<display-name>' + display + '</display-name>'
    
        if isWAR:
            print '\t\t\t\t<virtual-host>default_host</virtual-host>'
    
        for cluster in clusters:
            print '\t\t\t\t<cluster-name>' + cluster + '</cluster-name>'
    
        if isWAR:
            print '\t\t\t</web>'
     
        if isEJB:
            print '\t\t\t</ejb>'
     
        print '\t\t</module>' + lineSep
except:
    print "Warning:  Unspecified error listing modules for application " + appName + "."

print '\t<Security>'
print '\t\t<J2CAuthData>'
print '\t\t\t<J2C>'
#for x in AdminConfig.list('JAASAuthData').split(lineSep):
#    print AdminConfig.showAttribute(x, 'alias')
print '\t\t\t<\J2C>'
print '\t\t<\J2CAuthData>'
print '\t<\Security>' + lineSep

print '\t</mod-info>' + lineSep

print '</EnterpriseApplication>'
