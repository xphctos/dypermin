import argparse
import time
import sys
import json
import os
try:
    from lib.dypermin.common.label  import label
    from lib.dypermin.common.messages import error
    from lib.dypermin.common.messages import success
    from lib.dypermin.common.messages import yellow_log, blue_log
    from lib.dypermin.common.information import DYPERMIN_ROOT
    from lib.dypermin.core.sdk_analyzer import extractor
    from lib.dypermin.core.android_sdk_permissions import documentantion_permissions
    from lib.dypermin.core.test_controller import test_controller
    #from lib.dypermin.core.code_generator import constuctor



except:
    print ("Error While Loading Dypermin's Modules")


def main():
    try:
        label()
        if len(sys.argv) <= 1:
            parser.print_usage()
            sys.exit(1)
        else:
            results = parser.parse_args()
            android_source_folder = results.android_source_folder
            android_source_permissions = results.android_source_permissions
            android_source_documentation_permissions = results.android_source_documentation_permissions
            save_to_folder = results.save_to_folder
            input_api_dump = results.input_api_dump
            android_sdk_version = results.android_sdk_version
            if android_source_folder and android_sdk_version:
                if input_api_dump:
                    with open(input_api_dump) as data_file:
                        data = json.load(data_file)
                else:
                    data, api_level = extractor(android_source_folder)
                    if save_to_folder:
                        file = open(save_to_folder + "/" + "Android-API-" + str(api_level) +"-Dump.json", "w+")
                        file.write(json.dumps(data, indent=4, sort_keys=True))
                        file.close()
                    else:
                        if not os.path.exists(DYPERMIN_ROOT + "/" + "data"):
                            os.makedirs(DYPERMIN_ROOT + "/" + "data")
                        file = open(DYPERMIN_ROOT + "/" + "data" + "/" + "Android-API-" + str(api_level) + "-Dump.json", "w+")
                        file.write(json.dumps(data, indent=4, sort_keys=True))
                        file.close()
                if android_source_documentation_permissions:
                    if save_to_folder:
                        documentantion_permissions(data, save_to_folder, api_level)
                    else:
                        api_level = android_sdk_version
                        documentantion_permissions(data, DYPERMIN_ROOT + "/" + "data" + "/", api_level)
                elif android_source_permissions:
                    if not save_to_folder:
                        save_to_folder = DYPERMIN_ROOT
                    if input_api_dump:
                        with open(input_api_dump) as data_file:
                            data = json.load(data_file)
                        test_controller(android_source_folder, android_sdk_version, save_to_folder, data)
                    else:
                        error("You Must Define SDK Dump File.")
                        parser.print_usage()
                        sys.exit(1)
            elif not android_source_folder:
                error("You Must Define An Android SDK Folder.")
                parser.print_usage()
                sys.exit(1)
            elif not android_sdk_version:
                error("You Must Define The Android Version.")
                parser.print_usage()
                sys.exit(1)

    except KeyboardInterrupt:
        exit(1)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Android Framwork Permission Extractor.')
    parser.add_argument('-f', dest='android_source_folder', help='Define Android SDK Folder For Analysis', type=str)
    parser.add_argument('-d', dest='android_source_documentation_permissions', help='Extract Permissions From SDK Documentation.', action='store_true')
    parser.add_argument('-p', dest='android_source_permissions', help='Extract Permissions From SDK Method Invocation.', action='store_true')
    parser.add_argument('-s', dest='save_to_folder', help='Folder To Save Results.', type=str)
    parser.add_argument('-i', dest='input_api_dump', help='Folder To Save Results.', type=str)
    parser.add_argument('-v', dest='android_sdk_version', help='Android SDK Version.', type=int)

    start_time = time.time()
    main()