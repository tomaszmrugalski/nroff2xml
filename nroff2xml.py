#
# Experimental nroff2xml 0.0.1
# Author: Tomek Mrugalski
#

import sys
import re

# Constants

PREAMBLE = '<?xml version="1.0" encoding="US-ASCII"?>\n';
DOCTYPE_BEGIN = '<!DOCTYPE rfc SYSTEM "rfc2629.dtd" [\n'

DOCTYPE_END = ']>\n'

STYLESHEET = '<?xml-stylesheet type="text/xsl" href="rfc2629.xslt" ?>'

HEADER_STRICT='<?rfc strict="yes" ?>\n'
HEADER_TOC='<?rfc toc="yes"?>\n'





def readNroff(infile):
    with open(infile) as f:
        content = f.readlines()

    print("Read %d lines from %s file." % (len(content), infile))

    return content

def convert(nroff):
    xml = PREAMBLE
    xml += DOCTYPE_BEGIN

    section_re = re.compile("(\d+\.)(\d+\.)*(\d+\.)* ") # Matches section number
    dotti0_re = re.compile("^\.ti\s*0\s*$") # matches .ti 0

    likely_section = False

    lineno = 0
    for line in nroff:
        lineno += 1

        if dotti0_re.search(line):
            likely_section = True
            print ("### Found section begin in line %d" % lineno)
            continue

        s = section_re.search(line)

        section_lv1 = 0
        section_lv2 = 0
        section_lv3 = 0

        if (s is not None):
            #print (s.groups(), s.groups()[0])

            # get 0th group, remove the last char (.) and convert to int
            section_lv1 = int(s.groups()[0][:-1])

            if s.groups()[1] is None:
                level = 1
            else:
                if s.groups()[2] is None:
                    level = 2
                    section_lv2 = int(s.groups()[1][:-1])
                else:
                    level = 3
                    section_lv3 = int(s.groups()[2][:-1])
            if level == 1:
                print("%d: %s" % (section_lv1, line))
            if level == 2:
                print("%d.%d: %s" % (section_lv1, section_lv2, line))
            if level == 3:
                print("%d.%d.%d: %s" % (section_lv1, section_lv2, section_lv3, line))



        likely_section = False

    return xml

def writeXml(xml, outfile):
    f = open(outfile, "w")

    f.write(xml)

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

    print("Reading %s" % infile)
    nroff = readNroff(infile)
    print("Read %d lines." % len(nroff))

    print("Converting %s => %s" % (infile, outfile))
    xml = convert(nroff)

    print("Writing XML output (%d bytes) to %s" % (len(xml), outfile))

    writeXml(xml, outfile)

if __name__ == "__main__":
    main(sys.argv[1:])
