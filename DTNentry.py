import sys, getopt
from Epidemic import *
from SprayandWait import *
from Prophet import *
from ThreeR import *
from FGDR import *
from FGProphet import *
from DTNgeneral import *

## python DTNentry.py -i <inputfile> -o <outputfile> -p protocol memory dumppolicy
## protocol: Ep / Pro / 3R / SW / FGDR
## memory: Unlimit / any number
## dumppolicy: F / L / R


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"i:o:p:",["ifile=","ofile=","protocol="])
    except getopt.GetoptError:
        print('Error')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-p", "--protocol"):
                protocol = arg
    if protocol == "Ep":
        ep = Epidemic()
        ep.assign_global_variables(opts, args)
        ep.running()
    elif protocol == "SW":
        sw = SprayandWait()
        sw.assign_global_variables(opts, args)
        sw.running()
    elif protocol == "Pro":
        pro = Prophet()
        pro.assign_global_variables(opts, args)
        pro.running()
    elif protocol == "3R":
        thr = ThreeR()
        thr.assign_global_variables(opts, args)
        thr.running()
    elif protocol =="FGDR":
        fgdr = FGDR()
        fgdr.assign_global_variables(opts, args)
        fgdr.running()
    elif protocol =="FGPro":
        fgdr = FGProphet()
        fgdr.assign_global_variables(opts, args)
        fgdr.running()


if __name__ == "__main__":
   main(sys.argv[1:])
