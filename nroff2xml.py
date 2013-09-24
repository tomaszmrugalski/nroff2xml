#
# Experimental nroff2xml 0.0.1
# Author: Tomek Mrugalski
#

VERSION = '0.0.1'

import sys
import re

# Constants

PREAMBLE = '<?xml version="1.0" encoding="US-ASCII"?>\n';
DOCTYPE_BEGIN = '<!DOCTYPE rfc SYSTEM "rfc2629.dtd" [\n'
DOCTYPE_END = ']>\n'
STYLESHEET = '<?xml-stylesheet type="text/xsl" href="rfc2629.xslt" ?>'
HEADER_STRICT='<?rfc strict="yes" ?>\n'
HEADER_TOC='<?rfc toc="yes"?>\n'
HEADER_TOC_DEPTH='<?rfc tocdepth="4"?>\n'
HEADER_SYMREFS='<?rfc symrefs="yes"?>\n'
HEADER_SORTREFS='<?rfc sortrefs="yes" ?>\n'
HEADER_COMPACT='<?rfc compact="yes" ?>\n'
HEADER_SUBCOMPACT='<?rfc subcompact="no" ?>\n'
HEADER_CATEGORY='<rfc category="info" docName="draft-ietf-xml2rfc-template-05" ipr="trust200902">\n'

AUTHOR_TEMPLATE="""<author fullname="Unknown Person" initials="X" role="editor"
            surname="Unknown">
      <organization>Not converted</organization>
      <address>
        <postal>
          <street></street>
          <!-- Reorder these if your country does things differently -->
          <city>Unknown</city>
          <region></region>
          <code></code>
          <country>Unknown</country>
        </postal>
        <phone>+1 234 5678 9012</phone>
        <email>someone@example.com</email>
        <!-- uri and facsimile elements may also be added -->
      </address>
    </author>"""


class Nroff2Xml:
    xml=''
    nroff=''
    sections_list = []
    references = dict()

    t_open = False # Are we curently in <t> tag?

    def readNroff(self, infile):
        with open(infile) as f:
            self.nroff = f.readlines()

        print("Read %d lines from %s file." % (len(self.nroff), infile))

    def startSection(self, lineno, section, section_title):
        self.sections_list.append([section, section_title, lineno])
        print("Starting section %s (%s) in line %d." % (section, section_title, lineno))

        if self.t_open:
            self.xml += "</t>\n"
            self.t_open = False

        self.xml += '<section title="' + section_title + '"> <!-- ' + section + ', line ' + str(lineno) + '-->\n'

    def endSection(self):
        end_section = self.sections_list.pop()
        print("Ending section " + end_section[0] + ", started in line " + str(end_section[2]))

        if self.t_open:
            self.xml += "</t>\n"
            self.t_open = False

        self.xml += '</section> <!-- ends: "' + end_section[0] + " from line " + str(end_section[2]) + '-->\n'

    def addPreamble(self):
        self.xml += PREAMBLE
        self.xml += DOCTYPE_BEGIN
        self.xml += DOCTYPE_END
        self.xml += STYLESHEET
        self.xml += HEADER_STRICT
        self.xml += HEADER_TOC
        self.xml += HEADER_TOC_DEPTH
        self.xml += HEADER_SYMREFS
        self.xml += HEADER_SORTREFS
        self.xml += HEADER_COMPACT
        self.xml += HEADER_SUBCOMPACT
        self.xml += HEADER_CATEGORY

    def extractTitle(self):
        return "Unknown"

    def extractShortTitle(self):
        return "Unknown(short)"

    def extractDate(self):
        return ["1", "January", "1900"]

    def addFront(self):
        self.xml += "<front>\n"
        self.xml += '<title abbrev="' + self.extractShortTitle() +'">' + self.extractTitle() + '</title>\n'

        self.xml += AUTHOR_TEMPLATE

        date = self.extractDate()
        self.xml += '<date day="' + date[0] + '" month="' + date[1] + '" year="' + date[2] + '" />\n'

        self.xml += "</front>\n\n"

    def convertText(self, line):
        if not len(self.sections_list):
            return

        line = line.replace("<", "&lt;", 999)
        line = line.replace(">", "&gt;", 999)

        if not len(line):
            if self.t_open:
                self.xml += "</t>\n"
                self.t_open = False
        else:
            # a line with text
            if self.t_open:
                self.xml += line + '\n'
            else:
                self.xml += "<t>" + line + '\n'
                self.t_open = True

    def findReferences(self):

        references_re = re.compile("^(\d+)\.? References*$")
        references_end1_re = re.compile("^A\. .*$")
        references_end2_re = re.compile("^Authors' Addresses")
        reference_num = re.compile("^\[(.+)\] (.+\.)$")
        nroff_control_re = re.compile("^\.")

        lineno = 0
        in_references = False

        self.references = {}

        ref = ""

        for line in self.nroff:
            lineno += 1

            if not in_references:
                m = references_re.match(line)
                if m is None:
                    continue
                else:
                    print("References start in line %d" % lineno)
                    in_references = True
                    continue

            if in_references:
                m = references_end1_re.match(line)
                if m is not None:
                    in_references = False
                    print("References end in line %d" % lineno)
                    break

                m = references_end2_re.match(line)
                if m is not None:
                    in_references = False
                    print("References end in line %d" % lineno)
                    break

            # ignore nroff control sequences
            if nroff_control_re.match(line) is not None:
                continue

            ref = ref + line.strip('\n\r')

            # ignore empty lines
            if not len(line.strip('\n\r')):

                m = reference_num.match(ref)
                if m is not None:
                    ref_id = m.groups()[0]
                    ref_value = m.groups()[1]
                    ref_value = ref_value.strip('\n\t')
                    print("%s: %s" % (ref_id, ref_value))
                    self.references[ref_id] = ref_value
                ref = ""
                continue


        print("Found %d references." % len(self.references))

        for key, value in self.references.items():
            print("Reference %s [%s]" % (key, value))


    def convert(self):

        section_re = re.compile("^\s*(\d+\.)(\d+\.)?(\d+\.)?(\d+\.)? (.+)*$") # Matches section number
        dotti0_re = re.compile("^\.ti\s*0\s*$") # matches .ti 0
        nroff_control_re = re.compile("^\.")

        self.xml += "<middle>\n"

        likely_section = False

        # List of section info structures
        self.sections_list = []

        lineno = 0
        for line in self.nroff:
            lineno += 1

            line = line.rstrip('\n\r')

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

                if level > len(self.sections_list) + 1:
                    print("\nError in line %d: parser thinks that the current section nest level is %d,\n"\
                          "but encountered a line that looks like level %d (%s). Sections levels can\n"\
                          "only increase by one.\n" % (lineno, len(self.sections_list), level, line))
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

                if level > len(self.sections_list):
                    self.startSection(lineno, section, section_title)
                else:
                    if level == len(self.sections_list):
                        self.endSection()
                        self.startSection(lineno, section, section_title)
                    else:
                        while level <= len(self.sections_list):
                            self.endSection()
                        self.startSection(lineno, section, section_title)

                continue # end of section title processing

            if nroff_control_re.search(line):
                continue

            # This is hopefully a regular text
            self.convertText(line)

            likely_section = False

        while len(self.sections_list):
            self.endSection()

        self.xml += "</middle>\n"

        return self.xml

    def addReferences(self):
        #self.xml += '<references title="Normative References">\n'
        #self.xml += '</references>\n'
        #self.xml += '<references title="Informative References">\n'
        #self.xml += '</references>\n'
        pass

    def addBack(self):
        self.xml += "<back>\n"

        self.addReferences()

        self.xml += "</back>\n"

    def addPostamble(self, infile):
        self.xml += "</rfc>\n"
        self.xml += "<!-- generated from file " + infile + " with nroff2xml " + VERSION \
            + " by Tomek Mrugalski -->\n"

    def writeXml(self, outfile):

        print("Writing XML output (%d bytes) to %s" % (len(self.xml), outfile))

        f = open(outfile, "w")

        f.write(self.xml)

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

        convert = Nroff2Xml()

        convert.readNroff(infile)

        convert.findReferences()

        convert.addPreamble()

        # Authors, Abstract, keywords, meta-data, date, title
        convert.addFront()

        # The actual content (<middle>)
        convert.convert()

        # References and appendices (<back>)
        convert.addBack()

        convert.addPostamble(infile)

        convert.writeXml(outfile)

if __name__ == "__main__":
    Nroff2Xml.main(sys.argv[1:])
