
import javalang
import os
import re
import json
import difflib
from lib.dypermin.common.information import DYPERMIN_ROOT
#from lib.dypermin.common.messages import yellow_log, blue_log, magenta_log, error, success
from progressbar import ProgressBar, Percentage, Bar

java_lang_package_classes_interfaces = ['Appendable', 'AutoCloseable', 'CharSequence', 'Cloneable',
                                        'Comparable', 'Iterable', 'Readable', 'Runnable', 'Boolean',
                                        'Byte', 'Character', 'Class', 'ClassLoader', 'Compiler',
                                        'Double', 'Enum', 'Float', 'Integer', 'Long', 'Number',
                                        'Object', 'Package', 'Process', 'ProcessBuilder',
                                        'ProcessBuilder.Redirect', 'Runtime',
                                        'Short', 'StackTraceElement', 'StrictMath', 'String',
                                        'StringBuffer', 'StringBuilder', 'System', 'Thread', 'ThreadGroup',
                                        'ThreadLocal', 'Throwable', 'Void', 'Exception', 'Error']

basic_types = ['int', 'short', 'byte', 'long', 'double', 'char', 'float', 'boolean']

def argument_subtype(arg_sub_type, argument):
    argument = argument + "." + arg_sub_type.name
    if str(arg_sub_type.sub_type) != 'None':
        argument = argument_subtype(arg_sub_type.sub_type, argument)

    return argument

def has_inner_class_interface(part, class_api_category, imports, enums, package_name, _path ,outer_class, overall_inner_classes):

    class_list = []
    inner_classes_name = []
    for inner_part in part.body:


        if str(inner_part) == 'ClassDeclaration' or str(inner_part) == 'InterfaceDeclaration':
            inner_name = inner_part.name

            has_class_list, has_inner_classes_name = has_inner_class_interface(inner_part, class_api_category, imports, enums, package_name, _path, outer_class, overall_inner_classes)

            for element in has_inner_classes_name:
                if element not in inner_classes_name:
                    inner_classes_name.append(element)
            for element in has_class_list:
                if element not in class_list:
                    class_list.append(element)
    # TODO inner_class_enumerations
    inner_class_enumeration = []
    inner_class_modifiers = []
    # Todo Fix 30/09 Merikse fores lipei to innerclass
    inner_class_implements = []
    inner_class_annotations = []
    inner_class_api_category = ""
    inner_class_extends = []
    inner_class_name = ''
    inner_method_list = []
    inner_class_type = ""
    if str(part) is 'ClassDeclaration':

        inner_class_type = "Class"
        inner_class_name = part.name
        inner_class_api_category = "Private"
        if part.modifiers:
            for modifiers in part.modifiers:
                inner_class_modifiers.append(modifiers)
        if part.implements:
            for implement in part.implements:
                inner_class_implements.append(implement.name)
        if part.extends:
            inner_class_extends.append(part.extends.name)
        if part.documentation:
            if class_api_category:
                if "@hide" not in part.documentation:
                    inner_class_api_category = "Public"
        if part.annotations:
            for annotation in part.annotations:
                inner_class_annotations.append(annotation.name)

        #getVideoResolution
        # INNER METHOD
        if part.body:
            inner_class_method_name = ''
            inner_method_list = []
            for inner_method in part.body:
                inner_method_args = []
                inner_method_modifiers = []
                permissions = []
                if str(inner_method) == 'ConstructorDeclaration':
                    inner_class_method_name = inner_method.name
                    method_api_category = 'Private'
                    if class_api_category:
                        if inner_method.documentation:
                            if "@hide" not in inner_method.documentation:
                                method_api_category = "Public"
                        else:
                            method_api_category = 'Public'
                    inner_class_method_type = "constructor"
                    if inner_method.annotations:
                        for annotation in inner_method.annotations:
                            if annotation.name == "RequiresPermission":
                                try:

                                    permissions.append(annotation.element.member)
                                except:
                                    for anot in annotation.element:
                                        for k in anot.value.values:
                                            permissions.append(k.member)
                    if inner_method.parameters:
                        for parameter in inner_method.parameters:
                            arg_name = parameter.type.name
                            if str(parameter.type) != "BasicType":
                                if str(parameter.type.sub_type) != "None":
                                    arg_name = argument_subtype(parameter.type.sub_type, arg_name)
                            else:
                                arg_name = parameter.type.name

                            is_array = ""
                            if parameter.type.dimensions:
                                is_array = "[]" * len(parameter.type.dimensions)
                            type = get_package(_path, package_name, arg_name, imports,
                                               [], overall_inner_classes, outer_class)
                            if is_array:
                                type = type +  is_array
                            inner_method_args.append(type)

                    if inner_method.modifiers:
                        for modifiers in inner_method.modifiers:
                            inner_method_modifiers.append(modifiers)

                elif str(inner_method) == 'MethodDeclaration':
                    inner_class_method_name = inner_method.name
                    method_api_category = 'Private'
                    if class_api_category:
                        if inner_method.documentation:
                            if "@hide" not in inner_method.documentation:
                                method_api_category = "Public"
                        else:
                            method_api_category = 'Public'
                    # Inner Method Args
                    ###HOHOH
                    inner_method_args = []
                    permissions = []
                    if inner_method.annotations:
                        for annotation in inner_method.annotations:
                            if annotation.name == "RequiresPermission":
                                try:
                                    # print annotation.element.member
                                    permissions.append(annotation.element.member)
                                except:
                                    for anot in annotation.element:
                                        for k in anot.value.values:
                                            # print k.member
                                            permissions.append(k.member)
                    if inner_method.parameters:
                        for parameter in inner_method.parameters:
                            arg_name = parameter.type.name
                            if str(parameter.type) != "BasicType":

                                if str(parameter.type.sub_type) != "None":
                                    arg_name = argument_subtype(parameter.type.sub_type, arg_name)

                            else:
                                arg_name = parameter.type.name

                            is_array = ""
                            if parameter.type.dimensions:
                                is_array = "[]" * len(parameter.type.dimensions)
                            type = get_package(_path, package_name, arg_name, imports,
                                               [], overall_inner_classes, outer_class)
                            if is_array:
                                type = type + is_array
                            inner_method_args.append(type)
                    # Inner Method Ret-Type if
                    return_type = ''
                    if inner_method.return_type:
                        is_array = ""
                        if inner_method.return_type.dimensions:
                            is_array = "[]" * len(inner_method.return_type.dimensions)

                        for im in imports:
                            separator = im.rfind(".")

                            if str(inner_method.return_type.name) == im[separator + 1:]:
                                if is_array:
                                    return_type = im +  is_array
                                else:
                                    return_type = im
                                break
                            elif inner_method.return_type.name in java_lang_package_classes_interfaces:
                                if is_array:
                                    return_type = "java.lang." + inner_method.return_type.name +  is_array
                                else:
                                    return_type = "java.lang." + inner_method.return_type.name
                                break
                            elif str(inner_method.return_type.name) == inner_class_name:
                                if is_array:
                                    return_type = package_name + "." + inner_method.return_type.name +  is_array
                                else:
                                    return_type = package_name + "." + inner_method.return_type.name
                            else:
                                if is_array:
                                    return_type = inner_method.return_type.name +  is_array
                                else:
                                    return_type = inner_method.return_type.name

                        inner_class_method_type = return_type
                    # Inner MethodRet-Type else
                    else:
                        inner_class_method_type = "void"
                    # Inner Method Modifiers
                    if inner_method.modifiers:
                        for modifiers in inner_method.modifiers:
                            inner_method_modifiers.append(modifiers)
            if inner_class_method_name:
                entry = {

                    "method": inner_class_method_name,
                    "args": inner_method_args,
                    "modifiers": inner_method_modifiers,
                    "type": inner_class_method_type,
                    "api": method_api_category,
                    "permissions": permissions

                }

                inner_method_list.append(entry)

    elif str(part) is 'InterfaceDeclaration':
        inner_class_name = part.name
        inner_class_type = "Interface"
        inner_class_api_category = "Private"
        if part.modifiers:
            for modifiers in part.modifiers:
                inner_class_modifiers.append(modifiers)
        if part.extends:
            for extension in part.extends:
                inner_class_extends.append(extension.name)
        if part.documentation:
            if class_api_category:
                if "@hide" not in part.documentation:
                    inner_class_api_category = "Public"
        if part.annotations:
            permission = []
            for annotation in part.annotations:
                inner_class_annotations.append(annotation.name)

    # APPAND HERE CLASS
    if inner_class_name:

        entry = {"class": outer_class + "$" + inner_class_name,  # OK
                 "type": inner_class_type,  # OK
                 "anotations": inner_class_annotations,  # OK
                 "modifiers": inner_class_modifiers,  # OK
                 "implements": inner_class_implements,  # OK
                 "extends": inner_class_extends,  # OK
                 "methods": inner_method_list,  # OK
                 "imports": imports,  # OK
                 "enumeration": enums,  # ???
                 "api": inner_class_api_category,
                 "inner_classes": inner_classes_name}
        class_list.append(entry)

    #if inner_classes_name:
        #print "INNERS-N: ", inner_class_name, inner_classes_name
    inner_classes_name = []
    inner_classes_name.append(inner_class_name)

    return [class_list, inner_classes_name]

def get_package(_path, package, argument_name, import_list, enumerations, inner_classes , class_name):
    inner = ''
    if "." in argument_name:
        #is inner class
        if argument_name.count('.') == 1:
            separator = argument_name.rfind(".")
            inner = argument_name[separator + 1:]
            argument_name = argument_name[:separator]
        #is package
        elif argument_name.count('.') > 1:
            return argument_name
    #print inner_classes
    if import_list:
        for _import in import_list:
            separator = _import.rfind(".")
            # It was imported
            if str(argument_name) == _import[separator + 1:]:
                # success("[+Imported]" + _import)
                if inner:
                    #print "[+I]", _import + "$" + inner
                    return _import + "$" + inner
                else:
                    return _import
            # It is java.lang
            elif argument_name in java_lang_package_classes_interfaces:

                return "java.lang." + argument_name
            # IS BASIC
            elif argument_name in basic_types:
                # success("+[basic]" + class_name)
                return argument_name
        # In the same package
        for _import in import_list:
            if os.path.exists(_path + "/" + package.replace(".", "/") + "/" + argument_name + ".java"):
                return package + "." + argument_name
        # Wildcard Import
        for _import in import_list:
            if _import.endswith("*"):
                dir = _path + "/" + _import[:-1].replace(".", "/")
                for path, subdirs, files in os.walk(dir):
                    for name in files:
                        if os.path.join(path, name).endswith("/" + argument_name + ".java"):
                            return os.path.join(path, name).replace(_path + "/", "").replace("/", ".").replace(".java",'')

        # Enumeration
        for enum in enumerations:
            if argument_name == enum.split('.')[1]:
                #success(argument_name)
                return enum
        # Inner Class

        for inner_class in inner_classes:
            if argument_name == inner_class:
                #success(package + "." + class_name +"$" + argument_name)
                return package + "." + class_name +"$" + argument_name
    else:
        # IS JAVA.LANG
        if argument_name in java_lang_package_classes_interfaces:
            # success("[+java.lang2]" + "java.lang." + class_name)
            return "java.lang." + argument_name
        # IS BASIC
        elif argument_name in basic_types:
            # success("+[basic2]" + class_name)
            #print argument_name
            return argument_name

        else:
            if os.path.exists(_path + "/" + package.replace(".", "/") + "/" + argument_name + ".java"):
                # success("[+FileFoundInPackage2]" + package + "." + class_name)
                return package + "." + argument_name

        for enum in enumerations:
            if argument_name == enum.split('.')[1]:
                #error(argument_name)
                return enum
                # Inner Class

        for inner_class in inner_classes:

            if argument_name == inner_class:

                #success(package + "." + class_name +"$" + argument_name)
                return package + "." + class_name +"$" + argument_name

    #error("Non Found Package For: " + argument_name)
    return argument_name

def extractor(_path):
    api_level = 0
    total_files = 0
    permission_list = []
    with open('data/android-permissions.txt') as permissions:
        for permission in permissions:
            permission_list.append(permission.replace("\n", "").replace("android.permission.", ""))

    for api_folder in os.walk(_path).next()[1]:
        for path, subdirs, files in os.walk(_path):
            for filename in files:
                if ".java" in filename and filename not in "package-info.java":
                    total_files += 1
                if "source.properties" in filename:
                    property_file = open(path + "/" + filename, "r")
                    property_file_text = property_file.read()
                    property_file.close()
                    reg = "(?:AndroidVersion.ApiLevel=)([0-9]+)"
                    api_level_list = re.findall(reg, property_file_text)
                    api_level = api_level_list[0]
    widgets = ['Dumping: Android API ' + str(api_level) + " ", Percentage(), ' ', Bar(marker='#', left='[', right=']')]
    pbar = ProgressBar(widgets=widgets, maxval=total_files + 1)
    pbar.start()
    q = 0
    package_list = []
    for api_folder in os.walk(_path).next()[1]:
        is_java = False
        for path, subdirs, files in os.walk(_path + "/" + api_folder + "/"):
            class_list = []
            error_list = []
            for filename in files:
                if ".java" in filename and filename not in "package-info.java":
                    is_java = True
                    pbar.update(q)
                    q += 1
                    java_file = open(path + "/" + filename, "r")
                    java_code = java_file.read()
                    java_file.close()
                    try:
                        tree = javalang.parse.parse(java_code)
                    except:
                        error_list.append(java_file)
                        continue
                    imports = []
                    for i in tree.imports:
                        if i.wildcard:
                            imports.append(i.path + ".*")
                        else:
                            imports.append(i.path)
                    package_name = tree.package.name
                    for klass in tree.types:
                        enums = []
                        method_list = []
                        class_name = klass.name
                        class_api_category = "Public"
                        if klass.documentation:
                            if "@hide" in klass.documentation:
                                class_api_category = "Private"
                        outer_class = klass.name
                        inner_classes_name = []
                        overall_inner_classes =[]
                        #FIND ALL INNER INTERFACE/CLASSES
                        for part in klass.body:
                            if str(part) == 'ClassDeclaration' or str(part) == 'InterfaceDeclaration':
                                overall_inner_classes.append(part.name)
                                for inner_part in part.body:
                                    if str(inner_part) == 'ClassDeclaration' or str(inner_part) == 'InterfaceDeclaration':
                                        overall_inner_classes.append(inner_part.name)
                        for part in klass.body:
                            if str(part) is 'EnumDeclaration':
                                enums.append(class_name + "." + part.name)
                            if str(part) == 'ClassDeclaration' or str(part) == 'InterfaceDeclaration':

                                has_inner_class_list, has_inner_classes_name  = has_inner_class_interface(part, class_api_category, imports, enums, package_name, _path, outer_class, overall_inner_classes)
                                for element in has_inner_classes_name:
                                    if element not in inner_classes_name:
                                        inner_classes_name.append(element)
                                for element in has_inner_class_list:
                                    if element not in class_list:
                                        class_list.append(element)
                        # OLDER-CODE
                        modifier_list = []
                        for modifiers in klass.modifiers:
                            modifier_list.append(modifiers)
                        extends_list = []
                        anotation_list = []
                        implements_list = []
                        for anotation in klass.annotations:
                            anotation_list.append(anotation.name)
                        class_type = ""
                        if str(klass) == "ClassDeclaration":
                            class_type = "Class"
                            if klass.extends:
                                extends_list.append(klass.extends.name)
                            if klass.implements:
                                for implement in klass.implements:
                                    if implement.sub_type:
                                        if implement.sub_type.sub_type:
                                            implements_list.append(
                                                implement.name + "." + implement.sub_type.name + "." + implement.sub_type.sub_type.name)
                                        else:
                                            implements_list.append(implement.name + "." + implement.sub_type.name)
                                    else:
                                        implements_list.append(implement.name)
                        elif str(klass) == "InterfaceDeclaration":
                            class_type = "Interface"
                            if klass.extends:
                                for extension in klass.extends:
                                    extends_list.append(extension.name)
                        for c in klass.constructors:
                            api_category = 'Public'
                            permissions = []
                            if c.annotations:
                                for annotation in c.annotations:
                                    if annotation.name == "RequiresPermission":
                                        try:
                                            permissions.append(annotation.element.member)
                                        except:
                                            for anot in annotation.element:
                                                for k in anot.value.values:

                                                    permissions.append(k.member)
                            if class_api_category == 'Public':
                                if c.documentation:
                                    if '@hide' in c.documentation:
                                        api_category = 'Private'
                            else:
                                api_category = 'Private'
                            if c.documentation:
                                for p in permission_list:
                                    if p in c.documentation and "permission" in c.documentation:
                                        if p not in permissions:
                                            permissions.append(p)
                            args = []
                            for e in c.parameters:
                                arg_name = ""
                                if class_name:
                                    arg_name = e.type.name
                                    if str(e.type) != "BasicType":
                                        if str(e.type.sub_type) != "None":
                                            arg_name = argument_subtype(e.type.sub_type, arg_name)
                                    else:
                                        arg_name = e.type.name
                                is_array = ""
                                if e.type.dimensions:
                                    is_array = "[]" * len(e.type.dimensions)
                                type = get_package(_path, package_name, arg_name, imports, enums, overall_inner_classes, outer_class)
                                if is_array:
                                    type = type + is_array
                                args.append(type)
                            entry = {
                                "method": c.name,
                                "args": args,
                                "modifiers": list(c.modifiers),
                                "type": "constructor",
                                "api": api_category,
                                "permissions": permissions
                            }
                            found = False
                            for element in method_list:
                                if ", ".join(
                                        args) == str(element["args"]) and "constructor" == element["type"] and c.name == element["method"]:
                                    found = True
                            if not found:
                                method_list.append(entry)

                        for m in klass.methods:
                            api_category = 'Public'
                            permissions = []
                            if m.annotations:
                                for annotation in m.annotations:
                                    if annotation.name == "RequiresPermission":
                                        try:
                                            permissions.append(annotation.element.member)
                                        except:
                                            for anot in annotation.element:
                                                for k in anot.value.values:
                                                    
                                                    permissions.append(k.member)
                            if class_api_category == 'Public':
                                api_category = 'Public'
                                if m.documentation:
                                    if '@hide' in m.documentation:
                                        api_category = 'Private'

                            else:
                                api_category = 'Private'
                            if m.documentation:
                                for p in permission_list:
                                    if p in m.documentation and "permission" in m.documentation:
                                        if p not in permissions:
                                            permissions.append(p)

                            args = []
                            for e in m.parameters:
                                arg_name = e.type.name
                                if str(e.type) != "BasicType":
                                    if str(e.type.sub_type) != "None":
                                        arg_name = argument_subtype(e.type.sub_type, arg_name)
                                else:
                                    arg_name = e.type.name
                                is_array = ""
                                if e.type.dimensions:
                                    is_array = "[]" * len(e.type.dimensions)
                                type = get_package(_path, package_name, arg_name, imports, enums, overall_inner_classes, outer_class)
                                if is_array:
                                    type = type + is_array
                                args.append(type)
                            return_type = ""
                            if m.return_type:
                                is_array = ""
                                if m.return_type.dimensions:
                                    is_array = "[]" * len(m.return_type.dimensions)
                                for im in imports:
                                    separator = im.rfind(".")

                                    if str(m.return_type.name) == im[separator + 1:]:
                                        if is_array:
                                            return_type = im + is_array
                                        else:
                                            return_type = im
                                        break
                                    elif e.type.name in java_lang_package_classes_interfaces:
                                        if is_array:
                                            return_type = "java.lang." + m.return_type.name + is_array
                                        else:
                                            return_type = "java.lang." + m.return_type.name
                                        break
                                    elif str(m.return_type.name) == class_name:
                                        if is_array:
                                            return_type = package_name + "." + m.return_type.name + is_array
                                        else:
                                            return_type = package_name + "." + m.return_type.name
                                    else:

                                        if is_array:
                                            return_type = m.return_type.name + is_array
                                        else:
                                            return_type = m.return_type.name
                                entry = {

                                    "method": m.name,
                                    "args": args,
                                    "modifiers": list(m.modifiers),
                                    "type": return_type,
                                    "api": api_category,
                                    "permissions": permissions
                                }
                                found = False
                                for element in method_list:
                                    if ", ".join(args) == str(element['args']) and return_type == element[
                                        'type'] and m.name == element['method']:
                                        found = True
                                if not found:
                                    method_list.append(entry)
                            else:
                                entry = {

                                    "method": m.name,
                                    "args": args,
                                    "modifiers": list(m.modifiers),
                                    "type": "void",
                                    "api": api_category,
                                    "permissions": permissions

                                }
                                found = False
                                for element in method_list:
                                    if ", ".join(
                                            args) == str(element["args"]) and "void" == element["type"] and m.name == \
                                            element["method"]:
                                        found = True
                                if not found:
                                    method_list.append(entry)
                        if is_java:
                            # CLASS
                            entry = {"class": class_name,
                                     "type": class_type,
                                     "anotations": anotation_list,
                                     "modifiers": modifier_list,
                                     "implements": implements_list,
                                     "extends": extends_list,
                                     "methods": method_list,
                                     "imports": imports,
                                     "enumeration": enums,
                                     "api": class_api_category,
                                     "inner_classes": inner_classes_name}
                            class_list.append(entry)
                    #yellow_log(package_name + "." + outer_class)
            if class_list:
                # PACKAGE
                entry = {"package": package_name, "classes": class_list}
                package_list.append(entry)

    if extends_list:
        if not os.path.exists(DYPERMIN_ROOT + "/" + "data"):
            os.makedirs(DYPERMIN_ROOT + "/" + "data")
        file = open(DYPERMIN_ROOT + "/" + "data" + "/" + "ERROR.LOG", "w+")
        for element in error_list:
            file.write(element)
        file.close()
    js = json.dumps(package_list)
    parsed = json.loads(js)
    pbar.finish()
    return parsed, api_level
