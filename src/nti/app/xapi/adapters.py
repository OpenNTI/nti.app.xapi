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

from nti.dataserver.interfaces import IUser

from nti.externalization.oids import toExternalOID

from nti.xapi.entities import Agent
from nti.xapi.entities import AgentAccount

from nti.xapi.interfaces import IAgent

logger = __import__('logging').getLogger(__name__)


NT_ACCOUNT_HOMEPAGE_BASE = 'http://nextthought.com/'


def _account_homepage(account_type, base=NT_ACCOUNT_HOMEPAGE_BASE):
    return '%s/%s' % (NT_ACCOUNT_HOMEPAGE_BASE, account_type)


@interface.implementer(IAgent)
@component.adapter(IUser)
def user_as_agent(user):
    return IAgent(user, name="default")


@interface.implementer(IAgent)
@component.adapter(IUser)
def user_as_username_agent(user):
    username = getattr(user, 'username', user)
    account = AgentAccount(homePage=_account_homepage('username'), name=username)
    return Agent(account=account)


@interface.implementer(IAgent)
@component.adapter(IUser)
def user_as_psuedo_anonymous_agent(user):
    oid = toExternalOID(user)
    account = AgentAccount(homePage=_account_homepage('external_oid'), name=oid)
    return Agent(account=account)
