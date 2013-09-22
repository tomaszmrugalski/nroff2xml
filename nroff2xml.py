#
# Experimental nroff2xml 0.0.1
# Author: Tomek Mrugalski
#

import sys

def readNroff(infile):
    with open(infile) as f:
        content = f.readlines()

    print("Read %d lines from %s file." % (len(content), infile))
    return content

def writeXml(nroff, outfile):
    f = open(outfile, "w")
    
    f.write("<?xml version=\"1.0\" encoding=\"US-ASCII\"?>\n")

    print("Writing output to %s file." % (outfile))

    f.close()

def main(argv):
    if (len(argv)<1):
        print("At least one parameter is required: nroff input file")
        exit(-1)

    infile = argv[0]
    outfile = argv[0]
    if (outfile.endswith(".nroff")):
        outfile = outfile[:-6] + ".xml"

    if (len(argv)>=2):
        outfile = argv[1]

    print("Converting %s => %s" % (infile, outfile))

    nroff = readNroff(infile)

    writeXml(nroff, outfile)


if __name__ == "__main__":
    main(sys.argv[1:])
