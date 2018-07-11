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

from nti.app.xapi import RECORDER_JOBS_QUEUE

from nti.app.xapi.common import to_nonstr_iterable

from nti.app.xapi.interfaces import IStatementRecorder

from nti.app.xapi.processing import put_generic_job

from nti.app.xapi.runner import process_statement

from nti.common.iterables import is_nonstr_iterable

from nti.xapi.interfaces import ILRSClient
from nti.xapi.interfaces import IStatement

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
            logger.warning('No LRSClient Found. Dropping statement(s)')
        else:
            recorder = client.save_statement
            if is_nonstr_iterable(stmts):
                recorder = client.save_statements
            recorder(stmts)


@interface.implementer(IStatementRecorder)
class InMemoryStartmentRecorder(object):

    def __init__(self):
        logger.warning('Recording statements in memory. Testing???')
        self.statements = []

    def record_statements(self, stmts):
        for stmt in to_nonstr_iterable(stmts):
            assert IStatement.providedBy(stmt), \
                   "Invalid statement %s" % type(stmt)
            self.statements.append(stmt)


@interface.implementer(IStatementRecorder)
class SingleRedisStartmentRecorder(object):

    def __init__(self):
        logger.info('Recording statements in redis')

    def record_statements(self, stmts):
        result = []
        for statement in to_nonstr_iterable(stmts):
            result.append(
                put_generic_job(RECORDER_JOBS_QUEUE, 
                                process_statement
                                (statement,))
            )
        return result
