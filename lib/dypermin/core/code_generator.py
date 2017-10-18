import json
import re
import uuid
try:
    from lib.dypermin.common.label import label
    from lib.dypermin.common.messages import error, magenta_log, yellow_log, blue_log, success
    from lib.dypermin.common.information import DYPERMIN_ROOT
    from lib.dypermin.core.sdk_analyzer import extractor
    from lib.dypermin.common.colors import *

except:
    print ("Error While Loading Dypermin's Modules")

basic_types = ['int', 'short', 'byte', 'long', 'double', 'char', 'float', 'boolean']

java_lang_package_classes = [ 'java.lang.Boolean','java.lang.Byte', 'java.lang.Character', 'java.lang.Class', 'java.lang.ClassLoader', 'java.lang.Compiler',
                                        'java.lang.Double', 'java.lang.Enum', 'java.lang.Float', 'java.lang.Integer', 'java.lang.Long', 'java.lang.Number',
                                        'java.lang.Object', 'java.lang.Package', 'java.lang.Process', 'java.lang.ProcessBuilder',
                                        'java.lang.ProcessBuilder.Redirect', 'java.lang.Runtime',
                                        'java.lang.Short','java.lang.StackTraceElement', 'java.lang.StrictMath', 'java.lang.String',
                                        'java.lang.StringBuffer', 'java.lang.StringBuilder', 'java.lang.System', 'java.lang.Thread' ,'java.lang.ThreadGroup',
                                        'java.lang.ThreadLocal', 'java.lang.Throwable', 'Void']

def constructor_policy(package, class_name, methods):
    constructors_ranks= []
    for method in methods:
        is_simple_object_constructor = True
        is_public_api = True
        is_simplest_object_constructor = True
        if len(methods) > 1:
            if "$" in class_name:
                print "[*]", "Todo Outer-Inner"
                return "HAS INNER"
            else:
                if method["api"] == "Public":
                    for arg in method["args"]:
                        if arg.replace("[]","")  != "android.content.Context" and arg.replace("[]","")  not in basic_types and arg.replace("[]","") != "java.lang.String":
                            ''' recursion for args '''
                            is_simple_object_constructor = False
                            break

                    if is_simple_object_constructor:
                        for arg in method["args"]:
                            if arg.replace("[]","")  != "android.content.Context" and arg.replace("[]","")  not in basic_types and arg.replace("[]",""):
                                is_simplest_object_constructor = False
                                break


                else:
                    is_public_api = False
                    for arg in method["args"]:
                        if arg.replace("[]","")  != "android.content.Context" and arg.replace("[]","")  not in basic_types and arg.replace("[]","")  not in java_lang_package_classes:
                            ''' recursion for args '''
                            is_simple_object_constructor = False
                            break

                    if is_simple_object_constructor:
                        for arg in method["args"]:
                            if arg.replace("[]","")  != "android.content.Context" and arg.replace("[]","")  not in basic_types and arg.replace("[]","")  != "java.lang.String":
                                is_simplest_object_constructor = False
                                break
            if method['args']:

                if is_simple_object_constructor:
                    if is_simplest_object_constructor:
                        if is_public_api:
                            constructors_ranks.append([8,method])
                        else:
                            constructors_ranks.append([7, method])
                    elif not is_simplest_object_constructor and package + "." + class_name not in method["args"]:
                        if is_public_api:
                            constructors_ranks.append([6,method])
                        else:
                            constructors_ranks.append([5, method])
                elif not is_simple_object_constructor and package + "." + class_name not in method["args"]:
                    if is_public_api:
                        constructors_ranks.append([2, method])
                    elif not is_public_api:
                        constructors_ranks.append([1, method])
            else:
                if is_public_api:
                    constructors_ranks.append([4, method])
                elif not is_public_api:
                    constructors_ranks.append([3, method])
        else:
            ret = methods[0]
    if len(methods) > 1:

        ret = sorted(constructors_ranks, reverse=True)[0][1]
    return ret

def has_abstract(args, data,from_class):
    is_abstract = False
    for arg in args:
        if arg.replace("[]", "")  != 'android.content.Context' and arg.replace("[]","")  not in basic_types and arg.replace("[]","")  not in java_lang_package_classes:
            for _package in data:

                package_name = _package["package"]
                for _class in _package["classes"]:
                    package_class = package_name + "." + _class['class']

                    if "$" in package_class:
                        package_class = package_class.replace("$", ".")
                    if "$" in arg:
                        package_class_arg = arg.replace("$", ".")
                    else:
                        package_class_arg = arg

                    if package_class == package_class_arg.replace("[]", ""):
                            mf = _class["modifiers"]
                            if 'abstract' in _class["modifiers"]:
                                return True
                            else:
                                for _method in _class["methods"]:
                                    method_type = _method["type"]
                                    if method_type == 'constructor':
                                        mf = _method["modifiers"]
                                        method_args = _method["args"]
                                        method_name = _method["method"]
                                        if _class[
                                            'type'] != 'Interface' and package_name + "." + method_name in method_args:
                                            print "HERE"
                                            return True
                                        if from_class in method_args:
                                            print "HERE"
                                            return True
                                        is_abstract = has_abstract(method_args, data, arg)
                                        if is_abstract:
                                            return True
                                    break


    return is_abstract

def has_interface(args, data, from_class):
    is_interface = False
    for arg in args:
        if arg.replace("[]", "") not in basic_types and arg.replace("[]", "")  not in java_lang_package_classes:
            #print '[*]', arg , "From: ", from_class
            found = False
            for _package in data:
                package_name = _package["package"]
                for _class in _package["classes"]:
                    package_class = package_name + "."+ _class['class']


                    if "$" in package_class:
                        package_class = package_class.replace("$", ".")

                    if "$" in arg:
                        package_class_arg = arg.replace("$", ".")

                    else:
                        package_class_arg = arg

                    if package_class == package_class_arg.replace("[]",""):
                        found = True
                        if _class["type"] == 'Interface':
                            blue_log('[Found Interface] ' + package_class)
                            return True
                        else:
                            for _method in _class["methods"]:
                                method_type = _method["type"]
                                if method_type == 'constructor':
                                    mf = _method["modifiers"]
                                    method_args = _method["args"]
                                    method_name = _method["method"]
                                    if _class['type'] != 'Interface' and package_name + "." + method_name in method_args:
                                        return False
                                    if from_class in method_args:
                                        return False
                                    is_interface = has_interface(method_args,data,arg)
                                    if is_interface:
                                        return True
                                break
            if not found:
                return True
    return is_interface

def method_codegen(uid, package_name, class_name, method_name, method_type, mf, method_args, data, sdk_path):
    code = ""
    imports = []
    arg_type = ""
    arg_object = ""
    temp_code = ""

    for arg in method_args:
        if arg.replace("[]", "") == "int":
            c_type = "Integer"
            s_type = "int"
            t_value = "1"
        elif arg.replace("[]", "") == "short":
            c_type = "Short"
            s_type = "short"
            t_value = "1"
        elif arg.replace("[]", "") == "byte":
            c_type = "Byte"
            s_type = "byte"
            t_value = "1"
        elif arg.replace("[]", "") == "long":
            c_type = "Long"
            s_type = "long"
            t_value = "1"
        elif arg.replace("[]", "") == "double":
            c_type = "Double"
            s_type = "double"
            t_value = "1"
        elif arg.replace("[]", "") == "char":
            c_type = "Character"
            s_type = "char"
            t_value = "'1'"
        elif arg.replace("[]", "") == "float":
            c_type = "Float"
            s_type = "float"
            t_value = "1"
        elif arg.replace("[]", "") == "boolean":
            c_type = "Boolean"
            s_type = "boolean"
            t_value = "true"
        if arg.replace("[]", "") in basic_types:
            if "[]" not in arg:
                if not arg_type:
                    arg_type += ", " + c_type + ".TYPE"
                else:
                    arg_type += ", " + c_type + ".TYPE"
                if not arg_object:
                    arg_object += "," + t_value
                else:
                    arg_object += "," + t_value
            else:
                counter = arg.count('[]')
                if not arg_type:
                    arg_type += ", " + s_type + "[]" * counter + ".class"
                else:
                    arg_type += ", " + s_type + "[]" * counter + ".class"
                if not arg_object:
                    values = "{" + t_value + ", " + t_value +", " + t_value +"}"
                    for i in xrange(1, counter):
                        values = values + "," + values
                    arg_object += ",new " + s_type + "[]" * counter + "{" * int(counter-1) + values + "}"*int(counter-1)
                else:
                    values = "{" + t_value + ", " + t_value + ", " + t_value + "}"
                    for i in xrange(1, counter):
                        values = values + "," + t_value
                    arg_object += ", " + "new " + s_type + "[]" * counter + "{" * int(counter-1) + values + "}"*int(counter-1)


        elif arg == "android.content.Context":
            _uid = str(uuid.uuid4()).replace("-", "_")
            code += '\t\t\tContext object_%s = App.getContext();\n' % (_uid)
            arg_type += ",%s.class" % ("Context")
            if "import android.content.Context;\n" not in imports:
                imports.append("import android.content.Context;\n")
            arg_object += ", " + " object_%s" % (_uid)

        elif arg == "java.lang.String":
            uid_s = str(uuid.uuid4()).replace("-", "_")
            code += '\t\tString object_%s = new String("%s");\n' % (uid_s, uid_s)
            arg_type += ", %s.class" % ("String")
            arg_object += ", " + " object_%s" % (uid_s)

        else:
            separator = arg.rfind(".")
            if '.'  in arg:
                this_package = arg[:separator]
                this_class = arg[separator + 1:]
            else:
                this_package = package_name
                this_class = arg
            con = constructor_codegen(this_package, this_class ,data, sdk_path)

            temp_code += con[0]
            for im in con[2]:
                if im not in imports:
                    imports.append(im)
            arg_type += ", %s.class" % (this_class)
            arg_object += ", (%s) object_%s" % (this_class, con[1])

    code += "try{\n"
    if temp_code is not "":
        code += "\t\t\t\t/**/\n"
    code += "\t" + temp_code
    if temp_code is not "":
        code += "\t\t\t\t/**/\n"
    code += "\t\t\t\t/*%s %s %s %s(%s)*/\n" % (" ".join(mf), method_type, package_name + "." + class_name, method_name, ", ".join(method_args))
    code += '\tMethod method%s = Class.forName("%s").getDeclaredMethod("%s"%s);\n' % (
        method_name, package_name + "." + class_name, method_name, arg_type)
    if mf:
        if mf[0] == "private" or mf[0] == "protected":
            code += '\tmethod%s.setAccessible(true);\n' % (method_name)
    if uid:
        code += "\tmethod%s.invoke(object_%s%s);\n" % (method_name, uid, arg_object)
    else:
        code += "\tmethod%s.invoke(%s%s);\n" % (method_name, "null", arg_object)
    code += '\tSystem.out.println("%s %s %s %s(%s)" + " No Error");\n' % (package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += "}\n"
    code += "catch (Exception e) {\n"
    code += "\tStringWriter sw = new StringWriter();\n"
    code += "\tPrintWriter pw = new PrintWriter(sw);\n"
    code += "\te.printStackTrace(pw);\n"
    code += "\tString error = sw.toString();\n"
    code += '\tString pattern1 = ".permission.[A-Z_]+";\n'
    code += '\tString pattern2 = "[cC]arrier [Pp]rivilege";\n'
    code += '\tString pattern3 = "java.lang.SecurityException: Requires ([A-Za-z_]+)";\n'
    code += '\tPattern r1 = Pattern.compile(pattern1);\n'
    code += '\tPattern r2 = Pattern.compile(pattern2);\n'
    code += '\tPattern r3 = Pattern.compile(pattern3);\n'
    code += '\tMatcher m1 = r1.matcher(error);\n'
    code += '\tMatcher m2 = r2.matcher(error);\n'
    code += '\tMatcher m3 = r3.matcher(error);\n'
    code += '\tif (m1.find()) {\n'
    code += '\t\tsb.append("%s %s %s %s(%s) " +  m1.group(0));\n' % (package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += '\t\tSystem.out.println("%s %s %s %s(%s) "  +  m1.group(0));\n' % (  package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += '\t\tSystem.out.println("Permission-Extracted:" + " " + sb.toString());\n'
    code += '\t}else if (m2.find()) {\n'
    code += '\t\tsb.append("%s %s %s %s(%s) " +  m2.group(0));\n' % (package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += '\t\tSystem.out.println("%s %s %s %s(%s) "  +  m2.group(0));\n' % (package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += '\t\tSystem.out.println("Permission-Extracted:" + " " + sb.toString());\n'
    code += '\t}else if (m3.find()) {\n'
    code += '\t\tsb.append("%s %s %s %s(%s) " + "android.permission." +  m3.group(1));\n' % ( package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += '\t\tSystem.out.println("%s %s %s %s(%s) "  +  m3.group(1));\n' % ( package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += '\t\tSystem.out.println("Permission-Extracted:" + " " + sb.toString());\n'
    code += '\t}else{\n'
    code += '\t\te.printStackTrace();\n'
    code += '\t\tSystem.out.println("%s %s %s %s(%s) "  + error);\n' % ( package_name + "." + class_name, " ".join(mf), method_type, method_name, ", ".join(method_args))
    code += '\t}\n'
    if "import java.util.regex.Matcher;\n" not in imports:
        imports.append("import java.util.regex.Matcher;\n")
    if "import java.util.regex.Pattern;\n" not in imports:
        imports.append("import java.util.regex.Pattern;\n")

    code += "}\n"
    return [code , imports]

def con_args_gen(args,data, sdk_path):
    arg_type = ""
    arg_object = ""
    code = ""
    imports = []
    if len(args) > 0:
        for arg in args:
            if arg.replace("[]", "") == "int":
                c_type = "Integer"
                s_type = "int"
                t_value = "1"
            elif arg.replace("[]", "") == "short":
                c_type = "Short"
                s_type = "short"
                t_value = "1"
            elif arg.replace("[]", "") == "byte":
                c_type = "Byte"
                s_type = "byte"
                t_value = "1"
            elif arg.replace("[]", "") == "long":
                c_type = "Long"
                s_type = "long"
                t_value = "1"
            elif arg.replace("[]", "") == "double":
                c_type = "Double"
                s_type = "double"
                t_value = "1"
            elif arg.replace("[]", "") == "char":
                c_type = "Character"
                s_type = "char"
                t_value = "'1'"
            elif arg.replace("[]", "") == "float":
                c_type = "Float"
                s_type = "float"
                t_value = "1"
            elif arg.replace("[]", "") == "boolean":
                c_type = "Boolean"
                s_type = "boolean"
                t_value = "true"
            if arg.replace("[]", "") in basic_types:
                if "[]" not in arg:
                    if not arg_type:
                        arg_type = c_type +".TYPE"
                    else:
                        arg_type = arg_type + ", " + c_type +".TYPE"
                    if not arg_object:
                        arg_object = t_value
                    else:
                        arg_object = arg_object + ", " + t_value
                else:
                    counter = arg.count('[]')
                    if not arg_type:
                        arg_type = s_type + "[]" * counter + ".class"
                    else:
                        arg_type = arg_type + ", " + s_type + "[]" * counter + ".class"
                    if not arg_object:
                        values = "{" + t_value + ", " + t_value + ", " + t_value + "}"
                        for i in xrange(1, counter):
                            values = values + "," + values
                        arg_object = "new " + s_type + "[]" * counter + "{" * int(counter-1) + values + "}"*int(counter-1)
                    else:
                        values = "{" + t_value + ", " + t_value + ", " + t_value + "}"
                        for i in xrange (1, counter):
                            values = values + "," + values
                        arg_object = arg_object + ", " + "new " + s_type + "[]" * counter + "{" * int(counter-1) + values + "}"* int(counter-1)


            elif arg == "android.content.Context":

                uid = str(uuid.uuid4()).replace("-", "_")
                code += '\t\t\t\tContext object_%s = App.getContext();\n' % (uid)
                if not arg_type:
                    arg_type = "%s.class" % ("Context")
                else:
                    arg_type = arg_type + ", " + " %s.class" % ("Context")
                if "import android.content.Context;\n" not in imports:
                    imports.append("import android.content.Context;\n")
                if not arg_object:
                    arg_object = " object_%s" % (uid)
                else:
                    arg_object = arg_object + ", " + " object_%s" % (uid)
                '''
            elif arg == "java.lang.String":
                uid_s = str(uuid.uuid4()).replace("-", "_")
                code += '\t\tString object_%s = new String("Test");\n' % (uid_s)
                if not arg_type:
                    arg_type = "%s.class" % ("String")
                else:
                    arg_type = arg_type + ", " + " %s.class" % ("String")
                if not arg_object:
                    arg_object = " object_%s" % (uid_s)
                else:
                    arg_object = arg_object + ", " + " object_%s" % (uid_s)
                '''
            else:
                separator = arg.rfind(".")
                package = arg[:separator]
                _class = arg[separator + 1:]
                con = constructor_codegen(package, _class, data, sdk_path)

                code += con[0]
                for im in con[2]:
                    if im not in imports:
                        imports.append(im)
                if not arg_type:
                    arg_type = "%s.class" % (_class)
                else:
                    arg_type = arg_type + ", " + " %s.class " % (_class)
                if not arg_object:
                    arg_object = "(%s) object_%s" % (_class, con[1])
                else:
                    arg_object = arg_object + ", " + "(%s) object_%s" % (_class, con[1])

    return [code, arg_type, arg_object, imports]

def constructor_codegen(_package_name, _class_name, _data, sdk_path):
    constructor_list = []
    code = ""
    imports = []
    uid = ""
    arg_type = ""
    arg_object = ""
    candidate_constructor_list = []
    found = False
    for _package in _data:
        package_name = _package["package"]
        if package_name == _package_name:
            for _class in _package["classes"]:
                if _class["type"] == "Class" :
                    class_name = _class["class"]
                    if _class_name == class_name:
                        found = True
                        for _method in _class["methods"]:
                            if _method["type"] == 'constructor':
                                constructor_list.append(_method)
                                if not has_interface( _method["args"], _data, class_name):
                                    if not has_abstract(_method["args"], _data, class_name):
                                        candidate_constructor_list.append(_method)
                        if found:
                            break
            if found:
                break
    if candidate_constructor_list and constructor_list:
        method = constructor_policy(package_name, class_name, candidate_constructor_list)
        modifiers = method["modifiers"]
        package_name = _package_name
        class_name = _class_name
        argument_code = con_args_gen(method["args"], _data, sdk_path)
        code += argument_code[0]
        arg_type += argument_code[1]
        arg_object += argument_code[2]
        if not arg_object:
            arg_object = "new Object[]{}"
            arg_type = "null"
        for im in argument_code[3]:
            if im not in imports:
                imports.append(im)
        imp = "import " + package_name + "." + class_name + ";\n"
        if imp not in imports:
            imports.append(imp)
        uid = str(uuid.uuid4()).replace("-", "_")
        code += '\t\t\t/* %s %s %s(%s)*/\n' %(" ".join(modifiers), package_name+"."+ class_name, class_name, ", ".join(method["args"]))
        code += '\tString string_%s = "%s";\n' % (uid, package_name + "." + class_name)
        code += '\tClass<?> class_%s = Class.forName(string_%s);\n' % (uid, uid)
        #getDeclaredConstructor
        code += '\t Constructor<?> constructor_%s = class_%s.getDeclaredConstructor(%s);\n' % (uid, uid, arg_type)
        if modifiers:
            if modifiers[0] == "private" or modifiers[0] == "protected":
                code += '\tconstructor_%s.setAccessible(true);\n' % (uid)
        code += '\tObject object_%s = constructor_%s.newInstance(%s);\n' % (uid, uid, arg_object)

    if not candidate_constructor_list and constructor_list:
        if class_name.endswith("Manager") or class_name.endswith("Manager") and not candidate_constructor_list[0]['args'] :
            class_file = sdk_path + package_name.replace(".","/") + "/" + class_name + ".java"
            file = open(class_file, "r")
            file_code = file.read()
            file.close()
            reg = "(?:.getSystemService\()(Context.[A-Z_]+)"
            result = re.findall(reg, file_code)
            if result:
                token = result[0]
                #print token
                imp = "import " + package_name + "." + class_name + ";\n"
                imports.append(imp)
                imp = "import " + "android.content.Context;\n"
                imports.append(imp)
                uid = str(uuid.uuid4()).replace("-", "_")
                code = "%s object_%s = (%s)getSystemService(%s);\n" %(class_name, uid, class_name, token)

    return [code, uid, imports]

def code_generator(data, package_name, class_name, method_name,method_type, mf, method_args, sdk_path):
    tests = ()
    if "static" in mf:
        if method_type != "constructor":
            meth = method_codegen("", package_name, class_name, method_name,
                                  method_type, mf, method_args, data, sdk_path)
            code = "package ssl.ds.unipi.gr.permissionscnanner;\n"
            imports = []
            for im in meth[1]:
                if im not in imports:

                    imports.append(im)
            for im in imports:
                code += im
            code += "import java.io.PrintWriter;\n"
            code += "import java.io.StringWriter;\n"
            code += "import android.util.Log;\n"
            code += "import android.support.v7.app.AppCompatActivity;\n"
            code += "import android.os.Bundle;\n"
            code += "import java.lang.reflect.Method;\n"
            code += "import java.lang.reflect.Constructor;\n"
            code += "public class MainActivity extends AppCompatActivity {\n"
            code += "\t@Override\n"
            code += "\tprotected void onCreate(Bundle savedInstanceState) {\n"
            code += "\t\tsuper.onCreate(savedInstanceState);\n"
            code += "\t\tsetContentView(R.layout.activity_main);\n"
            code += "\t\tStringBuilder sb = new StringBuilder();\n"
            code += meth[0]
            code += "\t}\n"
            code += "}\n"
            tests = ([code, package_name, class_name, mf, method_type, method_name, method_args])

    else:
        con = constructor_codegen(package_name, class_name, data, sdk_path)
        if method_type != "constructor":
            meth = method_codegen(con[1], package_name, class_name, method_name,
                                  method_type, mf, method_args, data, sdk_path)
            code = "package ssl.ds.unipi.gr.permissionscnanner;\n"
            code += "import android.support.v7.app.AppCompatActivity;\n"
            code += "import android.os.Bundle;\n"
            code += "import java.lang.reflect.Method;\n"
            code += "import java.lang.reflect.Constructor;\n"
            code += "import java.io.PrintWriter;\n"
            code += "import java.io.StringWriter;\n"
            code += "import android.util.Log;\n"
            imports = []
            for im in con[2]:
                if im not in imports:
                    imports.append(im)

            for im in meth[1]:
                if im not in imports:
                    imports.append(im)
            for im in imports:
                code += im
            code += "public class MainActivity extends AppCompatActivity {\n"
            code += "\t@Override\n"
            code += "\tprotected void onCreate(Bundle savedInstanceState) {\n"
            code += "\t\tsuper.onCreate(savedInstanceState);\n"
            code += "\t\tsetContentView(R.layout.activity_main);\n"
            code += "\t\tStringBuilder sb = new StringBuilder();\n"
            code += "\t\ttry{\n"
            code += con[0]
            code += meth[0]
            code += "}\n"
            code += "catch (Exception e) {\n"
            code += "\te.printStackTrace();\n"
            code += "}\n"
            code += "\t}\n"
            code += "}\n"
            tests = ([code, package_name, class_name, mf, method_type, method_name, method_args])
    return tests