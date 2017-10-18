
try:
    from lib.dypermin.common.label import label
    from lib.dypermin.common.messages import error
    from lib.dypermin.common.messages import yellow_log, blue_log
    from lib.dypermin.common.messages import success
    from lib.dypermin.common.information import DYPERMIN_ROOT
    from lib.dypermin.core.sdk_analyzer import extractor
    from lib.dypermin.common.colors import *

except:
    print ("Error While Loading Dypermin's Modules")

import subprocess
import shlex
import time

#OK
def executeAsyncCommand(commandAndArgs):
    return subprocess.Popen(commandAndArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#OK
def executeCommand(commandAndArgs):
    if isinstance(commandAndArgs, str):
        commandAndArgs = shlex.split(commandAndArgs)
    try:
        return subprocess.check_output(commandAndArgs, stderr=subprocess.STDOUT)
    except Exception, e:
        error("Error occured while executing command : {0}".format(e))
        return None

def start_emulator(emulator_path, port, name ,adb_path):
    emulator_port = str(port)
    #virtual machine name
    cmd = [
        emulator_path,
        "-no-snapshot-save",
        "-netspeed",
        "full",
        "-netdelay",
        "none",
        "-port",
        emulator_port,
        "-avd",
        name,
        #"-no-window",
        #"-gpu off"
    ]

    proc = executeAsyncCommand(cmd)
    time.sleep(10)
    wait_for_device_ready(port, adb_path)
    return proc

def stop_emulator(port, adb_path ,proc):
    emulator_port = str(port)
    cmd = [adb_path, "-s", "emulator-" + emulator_port, "emu", "kill"]
    executeCommand(cmd)
    time.sleep(1)
    #proc.kill()

def wait_for_device_ready(port, adb_path):

    emulator_port = str(port)
    adb = adb_path
    cmd = [adb, "-s", "emulator-" + emulator_port, "wait-for-device"]
    executeCommand(cmd)
    #print cmd

    ready = False
    while not ready:
        cmd = [adb, "-s", "emulator-" + emulator_port, "shell", "getprop", "dev.bootcomplete"]
        result = executeCommand(cmd)
        if result is not None and result.strip() == "1":
            ready = True
        else:
            time.sleep(1)
    ready = False
    while not ready:
        cmd = [adb, "-s", "emulator-" + emulator_port, "shell", "getprop", "sys.boot_completed"]
        result = executeCommand(cmd)
        if result is not None and result.strip() == "1":
            ready = True
        else:
            time.sleep(1)
    ready = False
    while not ready:
        cmd = [adb, "-s", "emulator-" + emulator_port, "shell", "getprop", "init.svc.bootanim"]
        result = executeCommand(cmd)
        if result is not None and result.strip() == "stopped":
            ready = True
        else:
            time.sleep(1)
    time.sleep(5)

