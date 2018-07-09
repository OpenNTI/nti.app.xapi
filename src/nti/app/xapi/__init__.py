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

from zope import component

from nti.app.xapi.interfaces import IXAPIJobQueueFactory

#: Recorder job NTIID Type
RECORDER_JOB = u'RecorderJob'

#: Recorder jobs redis queue name
RECORDER_JOBS_QUEUE = '++etc++recorder++queue++jobs'

QUEUE_NAMES = (RECORDER_JOBS_QUEUE,)


def get_factory():
    return component.getUtility(IXAPIJobQueueFactory)
