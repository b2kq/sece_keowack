def convertToList(inlist):
   outlist = []
   if (len(inlist) > 0):
      if (inlist[0] == '[' and inlist[len(inlist) - 1] == ']'):
         # Special checking when the config name contain space
         if (inlist[1] == "\"" and inlist[len(inlist)-2] == "\""):
            clist = inlist[1:len(inlist) -1].split(")\" ")
         else:
            clist = inlist[1:len(inlist) - 1].split(" ")
         #endIf
      else:
         clist = inlist.split(java.lang.System.getProperty("line.separator"))
      #endIf

      for elem in clist:
          elem = elem.rstrip();
          if (len(elem) > 0):
             if (elem[0] == "\"" and elem[len(elem) -1] != "\""):
                elem = elem+")\""
             #endIf
             outlist.append(elem)
          #endIf
       #endFor
   #endIf
   return outlist
#endDef