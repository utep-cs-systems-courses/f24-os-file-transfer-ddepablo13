#! /usr/bin/env python3
from sys import argv, exit

progName = argv[0]
del argv[0]

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),  # default 127.0.0.1:50001  -s --server give a server
    (('-?', '--usage'), "usage", False),  # boolean (set if present)    -? and --usage prints out how to use this program
)

def parseParams(_switchesVarDefaults):
    paramMap = {}
    swVarDefaultMap = {}  # map from cmd switch to param var name
    for switches, param, default in _switchesVarDefaults:
        for sw in switches:
            swVarDefaultMap[sw] = (param, default)
        paramMap[param] = default  # set default values
    try:
        while len(argv) >= 2:  # Ensure at least two arguments are left
            arg = argv[0]
            if arg.startswith('-'):
                paramVar, defaultVal = swVarDefaultMap.get(arg, (None, None))
                if paramVar is not None:
                    if defaultVal:
                        if len(argv) > 1:
                            val = argv[1]
                            del argv[0:2]
                            paramMap[paramVar] = val
                        else:
                            print("Missing value for switch:", arg)
                            exit(1)
                    else:
                        del argv[0]
                        paramMap[paramVar] = True
                else:
                    print("Unknown switch:", arg)
                    exit(1)
            else:
                break  # Stop parsing if an argument is not a switch
    except Exception as e:
        print("Problem parsing parameters (exception=%s)" % e)
        exit(1)
    return paramMap

def usage():
    print("%s usage:" % progName)
    for switches, param, default in switchesVarDefaults:
        for sw in switches:
            if default:
                print(" [%s %s]   (default = %s)" % (sw, param, default))
            else:
                print(" [%s]   (%s if present)" % (sw, param))
    exit(1)

paramMap = parseParams(switchesVarDefaults)

server, usage = paramMap["server"], paramMap["usage"]  # maps param name to value

if usage:
    usage()  # Prints out message

print("Server:", server)