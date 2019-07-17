#!/usr/bin/env python3
# A script to parse the CAIDA data - http://data.caida.org/datasets/as-organizations/
# The input format as noted in the README is as follows:
# Example format for quick reference in README.txt from data.caida.org/datasets
# AS format:
# format: aut|changed|aut_name|org_id|opaque_id|source
# 1|20120224|LVLT-1|LVLT-ARIN|e5e3b9c13678dfc483fb1f819d70883c_ARIN|ARIN
# format: org_id|changed|name|country|source
# LVLT-ARIN|20120130|Level 3 Communications, Inc.|US|ARIN
#
# The script gleans the data from the two sources and generates a flattened out structure
# that is convenient to parse, reason about and validate.
# Note: using a proto structure in lieu of a CSV might be cleaner and
# might be considered.
#

__author__ = "Abhishek Balaji Radhakrishnan"
__email__ = "<abhishek.rb19@gmail.com>"

import argparse
import csv
import logging
import time

from typing import Dict

ASN_ENTRY_PREAMBLE = " format:aut|changed|"
logger = logging.getLogger('caidaas2org')

# TODO: define classes as needed.
# TOOD: add meta data such as line number for more inspection

def parse_as2org_file(filename: str) -> (Dict, Dict):
    '''
    Parses the contents and returns an Org map and ASN map per spec.
    :param filename: CAIDA AS2Org filename
    :return: Org map and ASN map
    :rtype: dict, dict
    '''
    asn_map = {} # Keyed by ASN
    org_map = {} # Keyed by OrgID
    org_entries = True  # Assumption is that the Org entries always come first before the ASN entries.
    with open(filename) as infile:
        for line in infile:
            # ignore the headers to determine what will be processed.
            if line.startswith("#"):
                logger.debug("Ignoring  line %s", line)
                if ASN_ENTRY_PREAMBLE in line:
                    org_entries = False
                continue

            fields = line.split('|')
            logger.debug("Fields %s", fields)

            if org_entries:
                org_map[fields[0]] = {'Name': fields[2], 'Country': fields[3]}
            else:
                asn_map[fields[0]] = {'OrgID': fields[3], 'AsnFriendlyName': fields[2]}
    return org_map, asn_map


def main():
    # define flags options
    parser = argparse.ArgumentParser(description="A tool to convert CAIDA AS2ORG data"
                                                 " into a flattened out structure.")
    parser.add_argument("-l", "--log-level",
                        help="Log level to use.",
                        default=logging.WARN, action="store_true")

    parser.add_argument("-i", "--input-file", help="Input CAIDA file to process.",
                        default="resources/as2org/uncompressed/20190701.as-org2info.txt", action="store_true")

    parser.add_argument("-o", "--output-file", help="Output file to write to.",
                        default="parsed_20190701.as-org2info.txt", action="store_true")

    args = parser.parse_args()

    # initialize logger
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logger.setLevel(args.log_level)

    # some basic validations
    if not args.input_file:
        logger.error("No input file specified. Exiting...")
        parser.print_help()
        exit(1)

    logger.info("Starting to process %s", args.input_file)
    start = time.time()
    org_map, asn_map = parse_as2org_file(args.input_file)

    logger.debug("AsnMap %sl; OrgMap %s", asn_map, org_map)

    org_to_asn = {}  # Flattened out data gleaned from both the above sources. Keyed by Org Name

    for asn, asnd in asn_map.items():
        org_id = asnd['OrgID']
        asn_friendly = asnd['AsnFriendlyName']
        od = org_map[org_id]
        org_name = od['Name']
        country = od['Country']

        if org_name in org_to_asn:
            existing_val = org_to_asn[org_name]
            existing_val['OrgIDS'].append(org_id)
            existing_val['Locations'].append(country)
            existing_val['ASNS'].append(asn)
            existing_val['FriendlyNames'].append(asn_friendly)
        else:
            org_to_asn[org_name] = {'OrgIDS': [org_id],
                                    'Locations': [country],
                                    'ASNS': [asn],
                                    'FriendlyNames': [asn_friendly]
                                    }  # TODO: should be Sets(), but oh well.

    with open(args.output_file, 'w', newline='') as out:
        wr = csv.writer(out, delimiter='#', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        heads = ['org_name', 'asns', 'org_ids', 'locations', 'friendly_names']
        wr.writerow(heads)
        for org, orgd in sorted(org_to_asn.items()):
            org_ids_str = "$".join(orgd['OrgIDS'])
            asns_str = "$".join(orgd['ASNS'])
            friendly_names_str = "$".join(orgd['FriendlyNames'])
            locations_str = "$".join(orgd['Locations'])

            # This looks hacky. Using protos, might be cleaner.
            logger.info("Org %s - OrgIDS: %s; ASNS: %s; FriendlyNames %s; Locations: %s", org, org_ids_str, asns_str,
                        friendly_names_str, locations_str)
            wr.writerow([org, asns_str, org_ids_str, friendly_names_str, locations_str])

    end = time.time()
    logger.info("Done processing %s; Wrote to %s; Took, %s seconds", args.input_file, args.output_file, end - start)


if __name__ == "__main__":
    main()
