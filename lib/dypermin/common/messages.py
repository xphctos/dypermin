try:
    from lib.dypermin.common.colors import yellow, color, green, magenta, red, white, bold, blue
except:
    print ("Error While Loading Dypermin's Modules")


def error(message):
    print("%s" % bold(red(message)))


def success(message):
    print("%s" % bold(green(message)))


def yellow_log(message):
    print("%s" % bold(yellow(message)))


def blue_log(message):
    print("%s" % bold(blue(message)))


def log(message):
    print("%s" % bold(blue(message)))


def magenta_log(message):
    print("%s" % bold(magenta(message)))
