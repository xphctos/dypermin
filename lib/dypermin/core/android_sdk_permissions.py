import javalang
import os
import re
import json
import difflib
from lib.dypermin.common.information import DYPERMIN_ROOT
from lib.dypermin.common.messages import yellow_log, blue_log, magenta_log, error, success

from progressbar import ProgressBar, Percentage, Bar

def documentantion_permissions(data, path, api_level):
    documentation_permissions = []
    for _package in data:
        package_name = _package["package"]
        for _class in _package["classes"]:
            if _class["type"] == "Class":
                class_name = _class["class"]
                for _method in _class["methods"]:
                    if _method['permissions']:
                        entry = _method['api'] + "-API " + package_name + "." + class_name + "." + _method[
                            'method'] + "(" + ', '.join(_method['args']) + ")" + " : " + ', '.join(
                            _method['permissions'])
                        documentation_permissions.append(str(entry))
    if documentation_permissions:
        if not os.path.exists(path):
            os.makedirs(path)
        file = open(path + "SDK_" + str(api_level) + "_DOCUMENTATION_PERMISSION_DUMP.TXT", "w+")
        for element in documentation_permissions:
            file.write(element + "\n")
        file.close()
