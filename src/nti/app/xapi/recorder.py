#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class,no-value-for-parameter

from datetime import datetime

from pyramid.interfaces import IRequest

from pyramid.threadlocal import get_current_request

import transaction

from zope import component
from zope import interface

from nti.app.xapi import RECORDER_JOBS_QUEUE

from nti.app.xapi.common import to_nonstr_iterable

from nti.app.xapi.interfaces import IStatementRecorder
from nti.app.xapi.interfaces import IStatementRecorderFactory

from nti.app.xapi.processing import put_generic_job

from nti.app.xapi.runner import process_statement

from nti.common.iterables import is_nonstr_iterable

from nti.transactions.transactions import OrderedNearEndObjectDataManager

from nti.xapi.interfaces import ILRSClient
from nti.xapi.interfaces import IStatement

logger = __import__('logging').getLogger(__name__)


def _on_statement_recorded(stmt):
    if stmt.timestamp is None:
        stmt.timestamp = datetime.utcnow()


@interface.implementer(IStatementRecorder)
class LRSStatementRecorder(object):
    """
    A statement recorder that looks up an ILRSClient and writes
    statements to it.
    """

    def __init__(self):
        self.client = component.queryUtility(ILRSClient)
        
    def record_statements(self, stmts):
        client = self.client
        if client is None:
            logger.warning('No LRSClient Found. Dropping statement(s)')
        else:
            recorder = client.save_statement
            if is_nonstr_iterable(stmts):
                recorder = client.save_statements
            
            for stmt in stmts:
                assert IStatement.providedBy(stmt), \
                   "Invalid statement %s" % type(stmt)
                _on_statement_recorded(stmt)
            logger.info('Persisting %i statements to lrs', len(stmts))
            recorder(stmts)


@interface.implementer(IStatementRecorder)
class InMemoryStatementRecorder(object):

    def __init__(self):
        self.statements = []

    def record_statements(self, stmts):
        for stmt in to_nonstr_iterable(stmts):
            assert IStatement.providedBy(stmt), \
                   "Invalid statement %s" % type(stmt)
            _on_statement_recorded(stmt)
            self.statements.append(stmt)


@interface.implementer(IStatementRecorder)
class BufferingStatementRecorder(InMemoryStatementRecorder):

    def __init__(self, flush_to_recorder):
        super(BufferingStatementRecorder, self).__init__()
        self.flush_to_recorder = flush_to_recorder

    def flush(self):
        self.flush_to_recorder.record_statements(self.statements)
        self.statements = []


@interface.implementer(IStatementRecorder)
class SingleRedisStatementRecorder(object):

    def __init__(self):
        logger.info('Recording statements in redis')

    def record_statements(self, stmts):
        result = []
        for statement in to_nonstr_iterable(stmts):
            _on_statement_recorded(statement)
            result.append(
                put_generic_job(RECORDER_JOBS_QUEUE, 
                                process_statement
                                (statement,))
            )
        return result


class XAPIStatementRecorderDataManager(OrderedNearEndObjectDataManager):

    def __init__(self, recorder):
        super(XAPIStatementRecorderDataManager, self).__init__(target=recorder, call=recorder.flush)

    @property
    def recorder(self):
        return self.target


@interface.implementer(IStatementRecorder)
@component.adapter(IRequest)
def statement_recorder_for_request(request=None):
    trans = transaction.get()

    rdm = next((m for m in trans._resources if isinstance(m, XAPIStatementRecorderDataManager)), None)
    if rdm is None:
        recorder = component.getUtility(IStatementRecorderFactory)()
        rdm = XAPIStatementRecorderDataManager(recorder)
        trans.join(rdm)

    return rdm.recorder


@interface.implementer(IStatementRecorderFactory)
def recorder_factory():
    """
    A callable that creates a recorder
    """
    return BufferingStatementRecorder(LRSStatementRecorder())

