try:
    from lib.dypermin.common.label import label
    from lib.dypermin.common.messages import error, success, yellow_log, blue_log
    from lib.dypermin.common.information import DYPERMIN_ROOT

except:
    print ("Error While Loading Dypermin's Modules")
import datetime
import time
import os
#write_permission(package_name, class_name, " ".join( mf),  method_type ,method_type ,"(" + ",".join(method_args) + ")" ,  m[0])
#def write_permission(package, _class, access_modifiers,  method_type ,method_name, args, permission):
def write_permission(entry, folder):


    directory = DYPERMIN_ROOT + "/" + "data" + "/" + folder
    if not os.path.exists(directory):
        os.makedirs(directory)
    f = open(directory + "/" + "PERMISSION.CSV", 'a+')
    f.write(entry + "\n")
    #f.write(package + " "  _class, "Type": method_type, "Access_Modifiers": access_modifiers,"Method": method_name , "Arguments":args , "Permission": permission} )  # python will convert \n to os.linesep
    f.close()

