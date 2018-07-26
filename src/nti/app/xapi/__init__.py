#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import zope.i18nmessageid
MessageFactory = zope.i18nmessageid.MessageFactory(__name__)

from pyramid.threadlocal import get_current_request

from zope import component

from nti.app.xapi.adapters import user_as_username_agent

from nti.app.xapi.interfaces import IStatementRecorder
from nti.app.xapi.interfaces import IXAPIJobQueueFactory

from nti.coremetadata.interfaces import SYSTEM_USER_ID
from nti.coremetadata.interfaces import SYSTEM_USER_NAME

#: Recorder job NTIID Type
RECORDER_JOB = u'RecorderJob'

#: Recorder jobs redis queue name
RECORDER_JOBS_QUEUE = '++etc++recorder++queue++jobs'

QUEUE_NAMES = (RECORDER_JOBS_QUEUE,)

logger = __import__('logging').getLogger(__name__)


def get_factory():
    return component.getUtility(IXAPIJobQueueFactory)


def record_statements(stmts, request=None):
    """
    A convenience function that records statements in the registered
    IStatementRecorder if it is available
    """
    if request is None:
        request = get_current_request()
    recorder = IStatementRecorder(request, None)
    if recorder is not None:
        # pylint: disable=too-many-function-args
        return recorder.record_statements(stmts)


def system_actor():
    agent = user_as_username_agent(SYSTEM_USER_ID)
    agent.name = SYSTEM_USER_NAME
    return agent
