@echo off

IF "%3"=="" GOTO ERRMSG

set WSADMIN=/IBM/WebSphere70/AppServer64/bin/wsadmin.bat

rem Nik changed the statement below to add %1 to the argument string.
%WSADMIN% -p /promotion/properties/%1/wsadmin.properties^
          -f /promotion/jython/main.py^
          %1 /promotion/properties/%1/%2 %3 %4

:ERRMSG
    echo "Usage: jython.bat <DEVwnd80/INTwnd90/PRODwnd40> <XmlPropertySheet.xml> <build/deploy/both> [SAVE/NOSAVE]"

@echo on