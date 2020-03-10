# -*-coding: utf-8-*-
# coding=utf-8

"""ICScards.nl transaction and balance source.

Data format
===========

To use, first download transaction (and balance) data into a directory on the
filesystem.

The transactions files are in PDF format and the oxfconverter plugin
nl-icscards is used to create an OFX file from it.

So the suggested workflow is:
1) Download the transaction statements from https://icscards.nl.
2) Place those PDF files in the data directory structure (see below).
3) Then this beancount_import module will take care of the rest.

You might have a directory structure like:

    financial/
      data/
        icscards/
          account_id/
            Rekeningoverzicht-54280230027-2020-01.pdf


The `Rekeningoverzicht-54280230027-2020-01.pdf` file should be a PDF file
containing all downloaded transactions, in the normal PDF download format
provided by ICScards.  See the `testdata/source/icscards` directory for an
example.

Specifying the source to beancount_import
=========================================

Within your Python script for invoking beancount_import, you might use an
expression like the following to specify the icscards source:

    dict(module='beancount_import.source.icscards',
         filenames=(
             glob.glob(os.path.join(journal_dir, 'data/icscards/*/*.pdf'))
         ),
    )

where `journal_dir` refers to the financial/ directory.

Imported transaction format
===========================

See the ofx.py module.

"""

from typing import List
import os
from subprocess import check_call, STDOUT

from . import ofx

class ICScardsSource(ofx.OfxSource):
    def __init__(self,
                 filenames: List[str],
                 **kwargs) -> None:
        ofx_filenames = []
        for file in [os.path.realpath(x) for x in filenames]:
            ofx_file = file + '.ofx'
            ofx_file_newer = False
            try:
                if os.stat(ofx_file).st_mtime > os.stat(file).st_mtime:
                    ofx_file_newer = True
            except:
                pass

            if not(ofx_file_newer):
                # Create a process for ofxstatement
                ofxstatement = ["ofxstatement", "convert", "-t", "nl-icscards"]
                ofxstatement.extend([file, ofx_file])
                check_call(ofxstatement, stderr=STDOUT)
            ofx_filenames.append(ofx_file)

        super().__init__(ofx_filenames=ofx_filenames, **kwargs)

    @property
    def name(self):
        return 'icscards'

def load(spec, log_status):
    return ICScardsSource(log_status=log_status, **spec)
