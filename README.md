nroff2xml
=========

Simple tool that converts nroff I-D sources into xml2rfc format (xml)

Author: Tomek Mrugalski
Licence: to be determined, whatever open source license is acceptable
         for IETF (likely BSD or GPL license)

Usage:

python nroff2xml.py input-file.nroff

DONE:
- boilerplate xml structure
- section conversions
- text conversion
- convert references

TODO:
- RFC3315 section 5.6 is not converted
- string trimming breaks down all formatting
- convert authors list
- convert name
