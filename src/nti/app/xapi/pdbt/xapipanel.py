#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from pyramid_debugtoolbar.panels import DebugPanel

from pyramid.threadlocal import get_current_request

import simplejson as json

from zope import component

from zope.component import getGlobalSiteManager

from nti.app.xapi.interfaces import IStatementRecordedEvent

from nti.externalization.externalization import to_external_object

from nti.xapi.interfaces import IStatement


@component.adapter(IStatement, IStatementRecordedEvent)
def _on_statement_recorded(stmt, unused_event):
    request = get_current_request()
    if hasattr(request, '_nti_pdbt_xapi_statements'):
        # pylint: disable=protected-access
        request._nti_pdbt_xapi_statements.append(stmt)


gsm = getGlobalSiteManager()
gsm.registerHandler(_on_statement_recorded)
del gsm


class XAPIDebugPanel(DebugPanel):
    """
    A debug panel capturing xapi statements that are recorded
    during the request
    """
    name = 'xAPI'
    template = 'nti.app.xapi:pdbt/templates/xapipanel.dbtmako'

    def __init__(self, request):
        DebugPanel.__init__(self, request)
        self.statements = request._nti_pdbt_xapi_statements = []

    @property
    def nav_title(self):
        return self.name

    @property
    def title(self):
        return self.name

    @property
    def has_content(self):
        return bool(self.statements)

    @property
    def nav_subtitle(self):
        if self.statements:
            return "%d" % (len(self.statements))

    def process_response(self, unused_response):
        stmts = sorted(self.statements, key=lambda stmt: stmt.timestamp)
        self.data = {
            'statements': stmts,
            'source': [json.dumps(to_external_object(x), sort_keys=True) for x in stmts]
        }


def includeme(config):
    config.add_debugtoolbar_panel(XAPIDebugPanel)
