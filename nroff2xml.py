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

    section_re = re.compile("^\s*(\d+\.)(\d+\.)?(\d+\.)?(\d+\.)? (.+)*$") # Matches section number
    dotti0_re = re.compile("^\.ti\s*0\s*$") # matches .ti 0

    likely_section = False

    # List of section info structures
    sections_list = []

    lineno = 0
    for line in nroff:
        lineno += 1

        if dotti0_re.search(line):
            likely_section = True
            #print ("### Found section begin in line %d" % lineno)
            continue

        s = section_re.search(line)

        section_lv1 = 0
        section_lv2 = 0
        section_lv3 = 0
        section_lv4 = 0

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
                    if s.groups()[3] is None:
                        level = 3
                        section_lv2 = int(s.groups()[1][:-1])
                        section_lv3 = int(s.groups()[2][:-1])
                    else:
                        level = 4
                        section_lv2 = int(s.groups()[1][:-1])
                        section_lv3 = int(s.groups()[2][:-1])
                        section_lv4 = int(s.groups()[3][:-1])

            if level > len(sections_list) + 1:
                print("\nError in line %d: parser thinks that the current section nest level is %d,\n"\
                      "but encountered a line that looks like level %d (%s). Sections levels can\n"\
                      "only increase by one.\n" % (lineno, len(sections_list), level, line))
                sys.exit(1)
            
            section_title = s.groups()[4]

            if level == 1:
                section = ("%d" % section_lv1)
            if level == 2:
                section = ("%d.%d" % (section_lv1, section_lv2))
            if level == 3:
                section = ("%d.%d.%d" % (section_lv1, section_lv2, section_lv3))
            if level == 4:
                section = ("%d.%d.%d.%d" % (section_lv1, section_lv2, section_lv3, section_lv4))

            if level > len(sections_list):
                sections_list = startSection(sections_list, lineno, section, section_title)
            else:
                if level == len(sections_list):
                    sections_list = endSection(sections_list)
                    sections_list = startSection(sections_list, lineno, section, section_title)
                else:
                    while level <= len(sections_list):
                        print("New level: %d, existing level: %d" % (level, len(sections_list)))
                        sections_list = endSection(sections_list)
                    sections_list = startSection(sections_list, lineno, section, section_title)

        likely_section = False

    return xml

def startSection(sections_list, lineno, section, section_title):
    sections_list.append([lineno, section])
    print("Starting section %s (%s) in line %d." % (section, section_title, lineno))

    return sections_list

def endSection(sections_list):
    end_section = sections_list.pop()
    print(">")
    return sections_list

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
