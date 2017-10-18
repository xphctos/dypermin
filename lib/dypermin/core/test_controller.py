import json
import time
import ConfigParser
import re
import datetime
from lib.dypermin.common.result_controller import write_permission
from pathlib import Path

try:
    from lib.dypermin.common.label import label
    from lib.dypermin.common.messages import error
    from lib.dypermin.common.messages import yellow_log, blue_log, magenta_log
    from lib.dypermin.common.messages import success
    from lib.dypermin.common.information import DYPERMIN_ROOT
    from lib.dypermin.core.sdk_analyzer import extractor
    from lib.dypermin.common.colors import *
    from lib.dypermin.core.emulator_controller import stop_emulator, start_emulator
    from lib.dypermin.core.apk_controller import apk_install, apk_build, apk_uninstall
    from lib.dypermin.core.code_generator import code_generator
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

except:
    print ("Error While Loading Dypermin's Modules")

def test_controller(sdk_path, version, output_dir, data):
    folder = "PERMISSION_" + str(version) + "_DUMP"
    directory = output_dir + "/" + "data" + "/" + folder
    if not os.path.exists(directory):
        os.makedirs(directory)
    time_log = open(directory + "/" + "RUN_TIME.txt", 'a+')
    folder = "PERMISSION_" + str(version) + "_DUMP"
    total_checked_accept_last = total_checked = []
    conf = ConfigParser.ConfigParser()
    conf.read("conf" + "/" + "control.conf")
    emulator_port = conf.get("avd", "emulator_port")
    emulator_path = conf.get("avd", "emulator_path")
    name = conf.get("avd", "emulator_name")
    adb_path = conf.get("avd", "adb_path")
    success_tests =[]
    error_tests =[]
    proc = start_emulator(emulator_path, emulator_port, name, adb_path)
    for _package in data:
        package_name = _package["package"]
        for _class in _package["classes"]:
            if _class["type"] == "Class" and "abstract" not in _class["modifiers"]:
                class_name = _class["class"]
                gen = []
                for _method in _class["methods"]:
                    method_type = _method["type"]
                    method_api = _method["api"]
                    mf = _method["modifiers"]
                    method_args = _method["args"]
                    method_name = _method["method"]
                    CODE_GEN = time.time()
                    to_check = package_name + "." + class_name + " " + " ".join(
                        mf) + " " + method_type + " " + method_name + "(" + ",".join(method_args) + ")" + " "
                    directory = DYPERMIN_ROOT + "/" + "data" + "/" + folder
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    my_file = Path(directory + "/" + "CHECKED.CSV")
                    if my_file.is_file():
                        f = open(directory + "/" + "CHECKED.CSV", 'r+')
                        total_checked_accept_last = f.read().splitlines()[:-1]
                        f.close()
                        f = open(directory + "/" + "CHECKED.CSV", 'r+')
                        total_checked = f.read().splitlines()
                        f.close()
                    if class_name:
                        INIT_TIME = time.time()
                        ts = time.time()
                        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        blue_log("[+] " + str(st) + " " + str(time.time()) + " Testing: " + package_name + "." + class_name + " " + " ".join( mf) + " " + method_type + " " + method_name + "(" + ",".join(method_args) + ")")
                        if to_check not in total_checked_accept_last:
                            test = code_generator(data, package_name, class_name, method_name,method_type, mf, method_args, sdk_path)
                            logs = []
                            if to_check not in total_checked:
                                f = open(directory + "/" + "CHECKED.CSV", 'a+')
                                f.write(to_check + "\n")
                                f.close()
                            if test:
                                code =  test[0]
                                class_name = test[2]
                                mf = test[3]
                                method_type = test[4]
                                method_name = test[5]
                                method_args = test[6]
                                CODE_BUILD = time.time()
                                gen.append(str(CODE_BUILD - CODE_GEN))
                                GEN_TIME = str(CODE_BUILD - CODE_GEN)
                                print("GEN TIME: " + GEN_TIME)
                                apk_root = apk_build(code)
                                INSTALL_APK = time.time()
                                INSTALL_TIME = str(INSTALL_APK - CODE_BUILD)
                                print("INSTALL TIME: " + INSTALL_TIME)
                                logs = []
                                found = False
                                if apk_root:
                                    logs = apk_install(method_name, method_args  ,apk_root)
                                    for log in logs:
                                        if "Permission-Extracted:" in log and method_name + "(" + ", ".join(method_args) + ")" in log:
                                            found = True
                                            print "[Android-Logcat]", log
                                            m = re.findall("(?:.permission.)([A-Z_]+)", str(log))
                                            if m:
                                                ts = time.time()
                                                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                                success ("[+] " + str(st) + " " + package_name + "." + class_name + " " + " ".join( mf) + " " + method_type + " " + method_name + "(" + ",".join(method_args) + ")" + " Permission:" + m[0])
                                                entry = method_api + "-API " + package_name + "." + class_name + " " + " ".join( mf) + " " + method_type + " " + method_name + "(" + ",".join(method_args) + ")" + " " + m[0]
                                                write_permission(entry, folder)
                                                success_tests.append("[+] " + str(st) + " " + package_name + "." + class_name + " " + " ".join( mf) + " " + method_type + " " + method_name + "(" + ",".join(method_args) + ")" + " Permission:" + m[0])
                                                break
                                            m = re.findall("([cC]arrier [Pp]rivilege)", str(log))
                                            if m:

                                                ts = time.time()
                                                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                                success("[+] " + str(
                                                    st) + " " + package_name + "." + class_name + " " + " ".join(
                                                    mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                    method_args) + ")" + " Permission:" + m[0])
                                                entry =  method_api + "-API " + package_name + "." + class_name + "." + method_name + "(" + ", ".join(
                                                    method_args) + ")" + " : " + m[0]
                                                write_permission(entry, folder)
                                                success_tests.append("[+] " + str(
                                                    st) + " " + package_name + "." + class_name + " " + " ".join(
                                                    mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                    method_args) + ")" + " Permission:" + m[0])
                                                break

                                        elif "No Error" in log and method_name + "(" + ", ".join(method_args) + ")" in log:
                                            print "[Android-Logcat]", log
                                            found = True
                                            ts = time.time()
                                            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                            yellow_log("[-] " + str(st) + " " + package_name + "." + class_name + " " + " ".join(
                                                mf) + " " + method_type + " " + method_name + "(" + ",".join(
                                                method_args) + ")")
                                            success_tests.append("[-] " + str(st) + " " + package_name + "." + class_name + " " + " ".join(
                                                mf) + " " + method_type + " " + method_name + "(" + ",".join(
                                                method_args) + ")")
                                            break
                                    if not found:
                                        for log in logs:
                                            if "NoSuchMethodException" in log and method_name + "(" + ", ".join(
                                                        method_args) + ")" in log :
                                                magenta_log("[NoSuchMethodException] " + package_name + "." + class_name + " " + " ".join(
                                                    mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                    method_args) + ")")
                                                #for l in logs:
                                                #    if "System.err" in l:
                                                #        error(l)
                                                #yellow_log(code)
                                                error_tests.append("[NoSuchMethodException] " + package_name + "." + class_name + " " + " ".join(
                                                    mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                    method_args) + ")")
                                                break
                                            elif "NullPointerException" in log and method_name + "(" + ", ".join(
                                                        method_args) + ")" in log :
                                                error("[NullPointerException] " + package_name + "." + class_name + " " + " ".join(
                                                    mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                    method_args) + ")")
                                                #for l in logs:
                                                #    if "System.err" in l:
                                                #        error(l)
                                                #yellow_log(code)
                                                error_tests.append(
                                                    "[NullPointerException] " + package_name + "." + class_name + " " + " ".join(
                                                        mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                        method_args) + ")")
                                                break

                                            elif "IllegalAccessException" in log and method_name + "(" + ", ".join(
                                                        method_args) + ")" in log:
                                                error("[IllegalAccessException] " + package_name + "." + class_name + " " + " ".join(
                                                    mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                    method_args) + ")")
                                                #for l in logs:
                                                #    if "System.err" in l:
                                                #        error(l)
                                                #yellow_log(code)
                                                error_tests.append(
                                                    "[IllegalAccessException] " + package_name + "." + class_name + " " + " ".join(
                                                        mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                        method_args) + ")")
                                                break
                                            elif "InvocationTargetException" in log and method_name + "(" + ",".join(
                                                        method_args) + ")" in log:
                                                error("[InvocationTargetException] " + package_name + "." + class_name + " " + " ".join(
                                                    mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                    method_args) + ")")
                                                #for l in logs:
                                                #    if "System.err" in l:
                                                #        error(l)
                                                #yellow_log(code)
                                                error_tests.append(
                                                    "[InvocationTargetException] " + package_name + "." + class_name + " " + " ".join(
                                                        mf) + " " + method_type + " " + method_name + "(" + ", ".join(
                                                        method_args) + ")")
                                                break
                                    apk_uninstall()
                                    TEST_TIME = str(time.time() - INSTALL_APK)
                                    TOTAL_TIME = str(time.time() - INIT_TIME)
                                    print("TEST TIME: " + TEST_TIME)
                                    print ("TOTAL TIME: " + TOTAL_TIME)
                                    time_log.write(package_name + "." + class_name + "." + method_name + "(" + ",".join(method_args) + ")" + "| " + GEN_TIME + "| " + INSTALL_TIME + "| " + TEST_TIME + "| " + TOTAL_TIME + "\n")
                        else:
                            magenta_log("[%]" + to_check)
    time_log.close()
    stop_emulator(emulator_port, adb_path, proc)

