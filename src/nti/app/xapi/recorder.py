#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class,no-value-for-parameter

from zope import component
from zope import interface

from nti.xapi.interfaces import ILRSClient

from nti.app.xapi.interfaces import IStatementRecorder

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IStatementRecorder)
class LRSStatementRecorder(object):
    """
    A statement recorder that looks up an ILRSClient and writes
    statements to it.
    """

    def _lrs_client(self):
        return component.queryUtility(ILRSClient)

    def record_statements(self, stmts):
        client = self._lrs_client()
        if client is None:
            logger.warning('No LRSClient Found. Dropping statements')

        recorder = client.save_statement
        if isinstance(stmts, (list, tuple,)):
            recorder = client.save_statements
        recorder(stmts)
