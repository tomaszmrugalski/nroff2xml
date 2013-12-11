#
# nroff2xml 0.1.0
#
# Author: Tomek Mrugalski <tomasz(dot)mrugalski(at)gmail(dot)com>
#
# Copyright (c) 2013 IETF Trust and Tomek Mrugalski.
# All rights reserved.
#
# Released under simplified BSD license, see LICENSE file for details.
#
# Simple tool that converts nroff I-D sources into xml2rfc format (xml)
#
# Usage:
#
# python nroff2xml.py input-file.nroff [output-file.xml]
#
# This script was tested successfully on RFC3315.nroff and RFC3633.nroff.
# It may or may not work on other RFCs. RFC Editor keeps nroff files for
# most published RFCs, so you may ask them for an nroff file, if you need it.
#
# The script was tested with python 2.7.5 and 3.3.2.
#

VERSION='0.1.0'
AUTHOR='Tomek Mrugalski'

import sys
import re

# Constants
# These will be included in the output XML file. Some of them are obvious
# boilerplate and require update.

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

# Unfortunately, authors are not parsed/converted, so the script puts
# a boilerplate author there.
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



class Reference:
    """
    This class is used to keep external references found in the text.

    Each reference consists of anchor (e.g. [20]), a new anchor (e.g.
    RFC3315) and a text. That text is everything that is there in
    Normative or informative references (e.g. Deering, S. and R. Hinden,
    "Internet Protocol, Version 6 (IPv6)Specification", RFC 2460, December
    1998.).
    """
    anchor = ''
    new_anchor = 0
    text = ''

    def __init__(self, anchor, text):
        self.anchor = anchor
        self.new_anchor = "UNKNOWN" + anchor
        self.text = text

        rfc_regexp = re.compile("RFC\ ([0-9]+)")
        rfc = rfc_regexp.search(text)
        print(rfc)
        if rfc is not None:
            num = str(rfc.groups()[0])
            if len(num) < 4:
                num = "0" + num
            self.new_anchor = "RFC" + num

class Nroff2Xml:
    """
    This is the main converter class.

    See main() method to understand the control flow. In essence, the code
    first loads nroff as a text file, then parses it to find referneces,
    and then goes through it again converting to XML as it goes.

    """
    xml=''
    nroff=''
    sections_list = []
    references = dict()

    t_open = False # Are we curently in <t> tag?

    # reads nroff file and stores its value in self.nroff
    def readNroff(self, infile):
        with open(infile) as f:
            self.nroff = f.readlines()

        print("Read %d lines from %s file." % (len(self.nroff), infile))

    """
    Starts a new section. Closes any open <t> tag before adding new <section>
    tag.
    """
    def startSection(self, lineno, section, section_title):
        self.sections_list.append([section, section_title, lineno])
        print("Starting section %s (%s) in line %d." % (section, section_title, lineno))

        if self.t_open:
            self.xml += "</t>\n"
            self.t_open = False

        self.xml += '<section title="' + section_title + '"> <!-- ' + section + ', line ' + str(lineno) + '-->\n'

    """
    Ends section. Closes any open <t> tag before closing </section>
    """
    def endSection(self):
        end_section = self.sections_list.pop()
        print("Ending section " + end_section[0] + ", started in line " + str(end_section[2]))

        if self.t_open:
            self.xml += "</t>\n"
            self.t_open = False

        self.xml += '</section> <!-- ends: "' + end_section[0] + " from line " + str(end_section[2]) + '-->\n'

    """
    Adds preamble. Unfortunately most of it is a boilerplate.
    However, it attempts to add references!
    """
    def addPreamble(self):
        self.xml += PREAMBLE

        self.xml += DOCTYPE_BEGIN
        for key, value in self.references.items():
            if value.new_anchor.find("RFC") == -1:
                continue

            rfc = value.new_anchor[3:]
            if len(rfc) == 3:
                rfc = "0" + rfc

            self.xml += "<!ENTITY " + value.new_anchor + " PUBLIC \"\" \"http://xml.resource.org/public/rfc/bibxml/reference.RFC." \
                + rfc + ".xml\">\n"
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

    """
    Supposed to extract title. @TODO
    """
    def extractTitle(self):
        return "Unknown"

    """
    Supposed to extract short title. @TODO
    """
    def extractShortTitle(self):
        return "Unknown(short)"

    """
    Supposed to extract publication date. @TODO
    """
    def extractDate(self):
        return ["1", "January", "1900"]

    """
    Adds <front> tag that includes title, author, date for now.
    It should feature additional stuff, like workgroup.
    """
    def addFront(self):
        self.xml += "<front>\n"
        self.xml += '<title abbrev="' + self.extractShortTitle() +'">' + self.extractTitle() + '</title>\n'

        self.xml += AUTHOR_TEMPLATE

        date = self.extractDate()
        self.xml += '<date day="' + date[0] + '" month="' + date[1] + '" year="' + date[2] + '" />\n'

        self.xml += "</front>\n\n"


    """
    Replaces references in a given line, e.g. replaces [20] with
    <xref target="RFC3315" />
    """
    def expandReferences(self, line):
        for key, value in self.references.items():
            old_anchor = "[" + str(value.anchor) + "]"
            new_anchor = "<xref target=\"" + str(value.new_anchor) + "\"/>"
            line = line.replace(old_anchor, new_anchor)
        return line

    """
    Converts regular text uses in paragraphs. Sanitization (<,> removal) is also
    performed. If there is an empty line, it is treated as end of paragraph,
    so </t> is inserted.
    """
    def convertText(self, line):
        if not len(self.sections_list):
            return

        line = line.replace("<", "&lt;", 999)
        line = line.replace(">", "&gt;", 999)

        line = self.expandReferences(line)

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

    """
    Attempts to find references in the text.

    Note: This was tested on only two RFCs (3315, 3633) from 2003.
    The references style likely evolved over time, so those regexps
    will probably need tuning.
    """
    def findReferences(self):

        references_re = re.compile("^(\d+)\.? +References*$")
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
                    self.references[ref_id] = Reference(ref_id, ref_value)
                ref = ""
                continue


        print("Found %d references." % len(self.references))

        for key, value in self.references.items():
            print("Reference %s [%s]" % (key, value.text))


    """
    The actual text convesion happens here. It goes through the main part (<middle>)
    of the text and converts its body to XML. It assumes that the sections numbers
    are up to 4 levels deep (e.g. 1.1.1.1).
    """
    def convert(self):

        # Matches section number
        section_re = re.compile("^\s*(\d+\.)(\d+\.)?(\d+\.)?(\d+\.)? (.+)*$")

        # Matches .ti 0 (section headers)
        dotti0_re = re.compile("^\.ti\s*0\s*$")

        # nroff control sequences
        nroff_control_re = re.compile("^\.")

        # Table of Contents
        toc_re = re.compile("^Table [Oo]f [Cc]ontents");

        self.xml += "<middle>\n"

        in_toc = False
        toc_line_begin = 0

        # List of section info structures
        self.sections_list = []

        lineno = 0
        for line in self.nroff:
            lineno += 1

            line = line.rstrip('\n\r')

            if dotti0_re.search(line):
                if in_toc:
                    in_toc = False
                    print("Skipping table of contents (lines %d-%d)" % (toc_line_begin, lineno))
                continue

            if toc_re.search(line):
                in_toc = True
                toc_line_begin = lineno
                continue

            if in_toc:
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

        while len(self.sections_list):
            self.endSection()

        self.xml += "</middle>\n"

        return self.xml

    """
    Generates a references list at the end of the text.
    It don't understand the differences between normative and informative
    references and treats all references as normative. @TODO
    """
    def addReferences(self):
        self.xml += '<references title="Normative References">\n'
        for key, value in self.references.items():

            if value.new_anchor.find("RFC") == -1:
                self.xml += "<reference anchor=\"" + value.new_anchor + "\">\n"
                self.xml += "  <front>\n"
                self.xml += "    <title>" + value.text + "</title>\n"
                self.xml += "    <author><organization>?</organization></author>\n"
                self.xml += "    <date year=\"1900\" />\n"
                self.xml += "  </front>\n"
                self.xml += "</reference>\n"
            else:
                self.xml += "    &" + str(value.new_anchor) + ";\n"
                self.xml += "    <!-- " + str(value.text) + " -->\n"

        self.xml += '</references>\n'

    """
    Generates <back> content. Currently there's only references tag in it.
    """
    def addBack(self):
        self.xml += "<back>\n"

        self.addReferences()

        self.xml += "</back>\n"

    """
    Adds postable
    """
    def addPostamble(self, infile):
        self.xml += "</rfc>\n"
        self.xml += "<!-- generated from file " + infile + " with nroff2xml " + VERSION \
            + " by " + AUTHOR + " -->\n"

    """
    Writes generated XML to a file.
    """
    def writeXml(self, outfile):

        print("Writing XML output (%d bytes) to %s" % (len(self.xml), outfile))

        f = open(outfile, "w")

        f.write(self.xml)

        f.close()

    """
    Complete conversion routing.
    """
    def main(self, argv):
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
    x = Nroff2Xml()
    x.main(sys.argv[1:])
