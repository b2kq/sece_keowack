lineSep  = java.lang.System.getProperty('line.separator')
provList = AdminConfig.list('JDBCProvider')
for provId in provList.split(lineSep):
    if((provId != "") & (provId.find("SQL") > -1)):
        cpath = AdminConfig.showAttribute(provId, 'classpath')
        #if((cpath != "${MICROSOFT_JDBC_DRIVER_PATH}/sqljdbc.jar") & (cpath != "${MICROSOFT_JDBC_DRIVER_PATH}/sqljdbc4.jar") & (cpath != "${WAS_LIBS_DIR}/sqlserver.jar;${WAS_LIBS_DIR}/base.jar;${WAS_LIBS_DIR}/util.jar;${WAS_LIBS_DIR}/spy.jar")):
        print provId
        print cpath