import zipfile
import shutil
import subprocess
from subprocess import Popen, PIPE, STDOUT

import time
try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    from lib.dypermin.common.label import label
    from lib.dypermin.common.messages import error
    from lib.dypermin.common.messages import yellow_log, blue_log
    from lib.dypermin.common.messages import success
    from lib.dypermin.common.information import DYPERMIN_ROOT
    from lib.dypermin.core.sdk_analyzer import extractor
    from lib.dypermin.common.colors import *

except:
    print ("Error While Loading Dypermin's Modules")

def apk_build(code):
    app_source_root = DYPERMIN_ROOT + "/" + "data" + "/" "PermissionScnanner"
    app_source_file = DYPERMIN_ROOT + "/" + "data" \
                      + "/" "PermissionScnanner" + "/" + "app" + "/" + "src" + "/" + "main" + "/" + "java" + "/" + "ssl" \
                      + "/" + "ds" + "/" + "unipi" + "/" + "gr" + "/" + "permissionscnanner" + "/" + "MainActivity.java"
    app_source_zip = DYPERMIN_ROOT + "/" + "data" + "/" "PermissionScnanner.zip"
    if os.path.exists(DYPERMIN_ROOT + "/" + "data" + "/" + "PermissionScnanner"):
        shutil.rmtree(DYPERMIN_ROOT + "/" + "data" + "/" + "PermissionScnanner")

    zip_ref = zipfile.ZipFile(app_source_zip, 'r')
    zip_ref.extractall(DYPERMIN_ROOT + "/" + "data")
    open(app_source_file, 'w').close()
    file = open(app_source_file, 'w')
    file.write(code)
    file.close()
    chmod = subprocess.Popen(['chmod', '+x', app_source_root + "/" + "gradlew"], stdout=PIPE, stderr=STDOUT)
    stdout, nothing = chmod.communicate()
    os.chdir(app_source_root)
    clean = subprocess.Popen(['./gradlew', 'clean'], stdout=PIPE, stderr=STDOUT)
    stdout, nothing = clean.communicate()
    apk_root = ""
    if "BUILD SUCCESSFUL" in stdout:
        build = subprocess.Popen(['./gradlew', 'assembleDebug'], stdout=PIPE, stderr=STDOUT)
        stdout, nothing = build.communicate()
        if "BUILD SUCCESSFUL" in stdout:
            apk_root = DYPERMIN_ROOT + "/" + "data" \
                       + "/" "PermissionScnanner" + "/" + "app" + "/" + "build" + "/" + "outputs" + "/" + "apk" + "/" + "app-debug.apk"
        else:
            error("[-] Build Error")
            #error(stdout)
            #blue_log(code)
    else:
        error("[-] Clean Error")
        error( stdout)

    os.chdir(DYPERMIN_ROOT)
    return apk_root


def apk_install(method_name, method_args,  apk_root):
    logs =[]
    clear_logcat = Popen(['adb', 'logcat', "-c"], stdout=PIPE, stderr=STDOUT)
    stdout, nothing = clear_logcat.communicate()
    logcat = Popen(['timeout', "5", "adb" , 'logcat'], stdout=PIPE, stderr=STDOUT)  # something long running
    #logcat = Popen(['adb', 'logcat'], stdout=PIPE, stderr=STDOUT, shell = False)  # something long running
    adb_install_app = Popen(['adb', 'install', apk_root], stdout=PIPE, stderr=STDOUT)
    stdout, nothing = adb_install_app.communicate()
    adb_start_main = subprocess.Popen(['adb', 'shell',
                                       'am start -n "ssl.ds.unipi.gr.permissionscnanner/ssl.ds.unipi.gr.permissionscnanner.MainActivity" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER'],
                                      stdout=PIPE, stderr=STDOUT)
    stdout, nothing = adb_start_main.communicate()
    timeout = time.time() + 2
    while True:
        line = logcat.stdout.readline()
        logs.append(line)
        if "Permission-Extracted" in line or 'No Error' in line or 'Exception' in line:
            if method_name + "(" + ",".join(method_args) +')' in line:
                break
        if time.time() > timeout:

            break
    logcat.terminate()
    uninstall = subprocess.Popen(['adb', 'shell', 'pm uninstall -k ssl.ds.unipi.gr.permissionscnanner'], stdout=PIPE,
                                 stderr=STDOUT)
    stdout, nothing = uninstall.communicate()
    return logs

def apk_uninstall():
    uninstall = subprocess.Popen(['adb', 'shell', 'pm uninstall -k ssl.ds.unipi.gr.permissionscnanner'], stdout=PIPE,
                                 stderr=STDOUT)
    stdout, nothing = uninstall.communicate()
    if os.path.exists(DYPERMIN_ROOT + "/" + "data" + "/" + "PermissionScnanner"):
        shutil.rmtree(DYPERMIN_ROOT + "/" + "data" + "/" + "PermissionScnanner")






