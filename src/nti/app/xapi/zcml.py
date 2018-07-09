#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.component.zcml import utility

from nti.app.xapi import QUEUE_NAMES

from nti.app.xapi.interfaces import IXAPIJobQueueFactory

from nti.asynchronous import get_job_queue as async_queue

from nti.asynchronous.interfaces import IRedisQueue

from nti.asynchronous.redis_queue import PriorityQueue as RedisQueue

from nti.coremetadata.interfaces import IRedisClient

logger = __import__('logging').getLogger(__name__)


class ImmediateQueueRunner(object):
    """
    A queue that immediately runs the given job. This is generally
    desired for test or dev mode.
    """

    def put(self, job, *unused_args, **unused_kwargs):
        job()


@interface.implementer(IXAPIJobQueueFactory)
class ImmediateQueueFactory(object):

    def get_queue(self, unused_name):
        return ImmediateQueueRunner()


@interface.implementer(IXAPIJobQueueFactory)
class XAPIRunnerQueueFactory(object):

    queue_interface = IRedisQueue

    def __init__(self, _context):
        for name in QUEUE_NAMES:
            queue = RedisQueue(self._redis, name)
            utility(_context, provides=IRedisQueue, component=queue, name=name)

    def _redis(self):  # pragma: no cover
        return component.queryUtility(IRedisClient)

    def get_queue(self, name):
        return async_queue(name, self.queue_interface)


def registerImmediateProcessingQueue(_context):
    logger.info("Registering immediate XAPI queue")
    factory = ImmediateQueueFactory()
    utility(_context, provides=IXAPIJobQueueFactory, component=factory)


def registerProcessingQueue(_context):
    logger.info("Registering XAPI redis queue")
    factory = XAPIRunnerQueueFactory(_context)
    utility(_context, provides=IXAPIJobQueueFactory, component=factory)
