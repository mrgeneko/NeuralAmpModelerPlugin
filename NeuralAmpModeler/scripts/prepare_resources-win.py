#!/usr/bin/env python3

# Keeps the VERSIONINFO block in resources/main.rc in step with config.h.
#
# The previous version of this script was commented out in full, and could not
# safely be re-enabled as written: it opened main.rc with mode "w" and wrote
# only a VERSIONINFO block, which would have discarded every resource
# declaration in the file -- the fonts, SVGs, bitmaps and dialogs the plug-in
# actually loads. This rewrites the handful of values that track config.h and
# leaves the rest of the file untouched.

import os, re, sys

scriptpath = os.path.dirname(os.path.realpath(__file__))
projectpath = os.path.abspath(os.path.join(scriptpath, os.pardir))

IPLUG2_ROOT = "../../iPlug2"

sys.path.insert(0, os.path.join(scriptpath, IPLUG2_ROOT + "/Scripts"))

from parse_config import parse_config


def main():
    config = parse_config(projectpath)

    rcpath = os.path.join(projectpath, "resources", "main.rc")

    with open(rcpath, "r") as f:
        rc = f.read()

    comma_version = "{},{},{},0".format(
        config["MAJOR_STR"], config["MINOR_STR"], config["BUGFIX_STR"]
    )

    # CompanyName is synced from PLUG_MFR because main.rc had drifted to
    # "GeneKo" while config.h said "Gene Ko" -- the spaceless form belongs to
    # BUNDLE_MFR, which builds the com.GeneKo.* bundle identifiers and must stay
    # as it is. Leaving names unsynced is what allowed that to diverge.
    substitutions = [
        (r"(^\s*FILEVERSION\s+)[\d,]+", r"\g<1>" + comma_version),
        (r"(^\s*PRODUCTVERSION\s+)[\d,]+", r"\g<1>" + comma_version),
        (r'(VALUE "FileVersion",\s*")[^"]*"', r"\g<1>" + config["FULL_VER_STR"] + '"'),
        (r'(VALUE "ProductVersion",\s*")[^"]*"', r"\g<1>" + config["FULL_VER_STR"] + '"'),
        (
            r'(VALUE "LegalCopyright",\s*")[^"]*"',
            r"\g<1>" + config["PLUG_COPYRIGHT_STR"] + '"',
        ),
        (r'(VALUE "CompanyName",\s*")[^"]*"', r"\g<1>" + config["PLUG_MFR"] + '"'),
    ]

    for pattern, replacement in substitutions:
        rc, count = re.subn(pattern, replacement, rc, flags=re.MULTILINE)

        # A silent no-op here would ship stale version and copyright strings in
        # the binaries' file properties, which is exactly how main.rc came to
        # claim version 0.0.1 and "Copyright 2020 Acme Inc".
        if count == 0:
            raise RuntimeError(
                "no VERSIONINFO match for " + pattern + " in " + rcpath
            )

    with open(rcpath, "w") as f:
        f.write(rc)

    print(
        "main.rc VERSIONINFO set to "
        + config["FULL_VER_STR"]
        + ", "
        + config["PLUG_COPYRIGHT_STR"]
    )


if __name__ == "__main__":
    main()
