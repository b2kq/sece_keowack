@echo off

IF "%4"=="" GOTO ERRMSG

set WSADMIN=/IBM/WebSphere70/AppServer64/bin/wsadmin.bat

%WSADMIN% -p /promotion/properties/%1/wsadmin.properties^
          -f /promotion/jython/jvmTask.py^
          %2 %3 %4

:ERRMSG
echo.
echo    Usage:  jvmTask.bat ^<environment^> ^<jvmName^> ^<nodeName^> ^<task^>
echo.
echo    environment is one of the following:
echo       DEVWas DEV1Was INTWas SYSTESTWas UATWAS PRODWas
echo    jvmName is the JVM name, we have many, e.g.:
echo       RPW6FrontEnd_1_1  RPW6WebSvc_2_1 XAG_3_1
echo    nodeName would be specific to the defined nodes, e.g.:
echo       was30PROD64V70 kahobtwas35PROD32
echo    task woudl be one of the following:
echo       STOP START STATUS JAVACORE HEAPDUMP RESTART
echo.
echo    JAVACORE produces the thread dump, plain text file.
echo    HEAPDUMP produces portable heap dump, need heap analyzer tool.
echo    Location of the files default to was profile directory, e.g.
echo       ^\^\kahobtwas71^\j$^\UAT32^\javacore.^<date^>.^<time^>.^<pid^>.^<uniqueID^>.txt
echo       ^\^\kahobtwas71^\j$^\UAT32^\heapdump.^<date^>.^<time^>.^<pid^>.^<uniqueID^>.phd
echo    Note:  neither JAVACORE nor HEAPDUMP stops the JVM, it only pauses.
echo.
echo.   Also, if you want to HEAPDUMP/JAVACORE all JVMs in a cluster, use jython.bat
echo.
echo.   Usage:  jython.bat ^<environment^> ^<clusterName^> ^<task^>
echo.
@echo on