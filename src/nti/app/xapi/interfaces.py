#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class,no-value-for-parameter

from zope import interface

from zope.interface.interfaces import IObjectEvent

from nti.schema.field import Object

from nti.xapi.interfaces import IStatement

class IXAPIJobQueueFactory(interface.Interface):
    """
    A factory for spark job queues.
    """

class IStatementRecorderFactory(interface.Interface):
    """
    A callable factory that produces IStatementRecorder implementations
    """

    def __call__():
        """
        Returns an implementation of IStatementRecorder
        """

class IStatementRecorder(interface.Interface):
    """
    An object capable of recording xapi statements
    """

    def record_statements(stmts):
        """
        Record the provided xapi statements.  Accepts a list
        of `nti.xapi.interfaces.IStatement` objects or a single IStatement object.
        """


class IStatementRecordedEvent(IObjectEvent):
    """
    An object event fired when a statement is recorded
    """

    statement = Object(IStatement,
                       title=u"The statement that was recorded",
                       required=True)
