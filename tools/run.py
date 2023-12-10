#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the Spart Parser GUI"""

import multiprocessing

from itaxotools.spart_parser.gui import run

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run()
