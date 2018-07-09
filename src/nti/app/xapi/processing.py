#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time

from zope import component

from zope.component.hooks import getSite
from zope.component.hooks import site as current_site

from nti.app.xapi import RECORDER_JOB
 
from nti.app.xapi import get_factory 

from nti.app.xapi.common import get_site
from nti.app.xapi.common import get_creator

from nti.asynchronous import create_job

from nti.coremetadata.interfaces import IDataserver

from nti.coremetadata.utils import current_principal

from nti.ntiids.ntiids import make_ntiid
from nti.ntiids.ntiids import make_specific_safe

from nti.site.site import get_site_for_site_names

from nti.site.transient import TrivialSite

from nti.zodb.containers import time_to_64bit_int

logger = __import__('logging').getLogger(__name__)


def dataserver_folder():
    dataserver = component.getUtility(IDataserver)
    return dataserver.root_folder['dataserver2']


def do_execute_generic_job(*args, **kwargs):
    func, args = args[0], args[1:]
    return func(*args, **kwargs)


def get_job_site(job_site_name=None):
    old_site = getSite()
    if job_site_name is None:
        job_site = old_site
    else:
        ds_folder = dataserver_folder()
        with current_site(ds_folder):
            job_site = get_site_for_site_names((job_site_name,))
        # check we have a valid site
        if job_site is None or isinstance(job_site, TrivialSite):
            raise ValueError('No site found for (%s)' % job_site_name)
    return job_site


def execute_job(job_runner, *args, **kwargs):
    """
    Performs the actual execution of a job.  We'll attempt to do
    so in the site the event occurred in, otherwise, we'll run in
    whatever site we are currently in.
    """
    event_site_name = kwargs.pop('site_name', None)
    event_site = get_job_site(event_site_name)
    with current_site(event_site):
        return job_runner(*args, **kwargs)


def execute_generic_job(*args, **kwargs):
    return execute_job(do_execute_generic_job, *args, **kwargs)


def get_job_queue(name):
    factory = get_factory()
    return factory.get_queue(name)


def generate_job_id():
    creator = get_creator(current_principal())
    current_time = time_to_64bit_int(time.time())
    specific = u"%s_%s" % (creator, current_time)
    specific = make_specific_safe(specific)
    return make_ntiid(nttype=RECORDER_JOB, specific=specific)


def put_generic_job(queue_name, func, args=(), kws=None, 
                    job_id=None, site_name=None):
    job_id = job_id or generate_job_id()
    queue = get_job_queue(queue_name)
    # validate
    args = args or ()
    # always provided site name
    kws = dict(kws or {})
    kws['site_name'] = get_site(site_name)
    job = create_job(execute_generic_job,
                     func,
                     *args,
                     **kws)
    job.id = job_id
    queue.put(job)
    return job
