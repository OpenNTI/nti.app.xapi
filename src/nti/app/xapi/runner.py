#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from nti.xapi.interfaces import ILRSClient

logger = __import__('logging').getLogger(__name__)


def process_statement(stmt):
    client = component.getUtility(ILRSClient)
    if client.save_statement(stmt) is None:
        # raise exception to fail job
        raise Exception("Cannot save statement")
