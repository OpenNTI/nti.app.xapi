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

import transaction

from zope import component
from zope import interface

from zope.event import notify

from zope.interface.interfaces import ObjectEvent

from nti.app.xapi import RECORDER_JOBS_QUEUE

from nti.app.xapi.common import to_nonstr_iterable

from nti.app.xapi.interfaces import IStatementRecordedEvent
from nti.app.xapi.interfaces import IStatementRecorder
from nti.app.xapi.interfaces import IStatementRecorderFactory

from nti.app.xapi.processing import put_generic_job

from nti.app.xapi.runner import process_statement

from nti.common.iterables import is_nonstr_iterable

from nti.transactions.transactions import OrderedNearEndObjectDataManager

from nti.xapi.interfaces import ILRSClient
from nti.xapi.interfaces import IStatement

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IStatementRecordedEvent)
class StatementRecordedEvent(ObjectEvent):

    @property
    def statement(self):
        return self.object


class AbstractStatementRecorder(object):
    """
    A base for StatementRecorder implementations.
    """

    def notify_statements_recorded(self, stmts):
        for stmt in stmts:
            notify(StatementRecordedEvent(stmt))

    def _do_record_statements(self, stmts):
        """
        Override to actually record or persist the statement
        """

    def record_statements(self, stmts):
        stmts = to_nonstr_iterable(stmts)
        for stmt in stmts:
            assert IStatement.providedBy(stmt), \
                   "Invalid statement %s" % type(stmt)

            if stmt.timestamp is None:
                stmt.timestamp = datetime.utcnow()

        self._do_record_statements(stmts)
        self.notify_statements_recorded(stmts)


@interface.implementer(IStatementRecorder)
class LRSStatementRecorder(AbstractStatementRecorder):
    """
    A statement recorder that looks up an ILRSClient and writes
    statements to it.
    """

    def __init__(self):
        self.client = component.queryUtility(ILRSClient)

    def _do_record_statements(self, stmts):
        recorder = self.client.save_statement
        if is_nonstr_iterable(stmts):
            recorder = self.client.save_statements
        logger.info('Persisting %i statements to lrs', len(stmts))
        recorder(stmts)

    def record_statements(self, stmts):
        if self.client is None:
            logger.warning('No LRSClient Found. Dropping statement(s)')
            return
        super(LRSStatementRecorder, self).record_statements(stmts)


@interface.implementer(IStatementRecorder)
class InMemoryStatementRecorder(AbstractStatementRecorder):

    def __init__(self):
        self.statements = []

    def _do_record_statements(self, stmts):
        for stmt in to_nonstr_iterable(stmts):
            self.statements.append(stmt)


@interface.implementer(IStatementRecorder)
class BufferingStatementRecorder(InMemoryStatementRecorder):

    def __init__(self, flush_to_recorder):
        super(BufferingStatementRecorder, self).__init__()
        flush_to_recorder.notify_statements_recorded = lambda unused_x: None
        self.flush_to_recorder = flush_to_recorder

    def flush(self):
        self.flush_to_recorder.record_statements(self.statements)
        self.statements = []


@interface.implementer(IStatementRecorder)
class SingleRedisStatementRecorder(object):

    def __init__(self):
        logger.info('Recording statements in redis')

    def _do_record_statements(self, stmts):
        result = []
        for statement in to_nonstr_iterable(stmts):
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


@component.adapter(IRequest)
@interface.implementer(IStatementRecorder)
def statement_recorder_for_request(unused_request=None):
    trans = transaction.get()
    # pylint: disable=protected-access
    rdm = next(
        (m for m in trans._resources if isinstance(m, XAPIStatementRecorderDataManager)), None
    )
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
