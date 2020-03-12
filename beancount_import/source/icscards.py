# -*-coding: utf-8-*-
# coding=utf-8

"""ofxstatement transaction and balance source.

This module will convert files to (hidden) OFX files and will then process
those OFX files.  The OFX files will have the name of the input file with a
dot prefix and an .ofx suffix.  They will be created unless they are newer
than their input file, just like make does.


Data format
===========

See the corresponding section in ofx.py.


Specifying the source to beancount_import
=========================================

Within your Python script for invoking beancount_import, you might use an
expression like the following to specify the ofxstatement source:

    dict(module='beancount_import.source.ofxstatement',
         filenames=(
             glob.glob(os.path.join(journal_dir, 'data/institution1/*/*.pdf'))
             + glob.glob(os.path.join(journal_dir, 'data/institution2/*/*.csv'))
         ),
         cache_filename=os.path.join(journal_dir, 'data/ofxstatement_cache.pickle'),
    )

where `journal_dir` refers to the financial/ directory.

The `cache_filename` key is optional, but is recommended to speed up parsing if
you have a large amount of OFX data.  When using the `cache_filename` option,
adding and deleting OFX files is fine, but if you modify existing OFX files, you
must delete the cache file manually.


Specifying individual accounts
==============================

See the corresponding section in ofx.py.


Imported transaction format
===========================

See the corresponding section in ofx.py.

"""

from typing import List
import os
from subprocess import check_call, STDOUT

from . import ofx

class OfxStatementSource(ofx.OfxSource):
    def __init__(self,
                 filenames: List[str],
                 **kwargs) -> None:
        ofx_filenames = ofx.convert2ofx("nl-icscards", filenames)
        super().__init__(ofx_filenames=ofx_filenames, **kwargs)

    @property
    def name(self):
        return 'icscards'

def load(spec, log_status):
    return OfxStatementSource(log_status=log_status, **spec)
