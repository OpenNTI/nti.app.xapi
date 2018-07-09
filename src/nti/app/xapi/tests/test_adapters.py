#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that
from hamcrest import contains_string
from hamcrest import has_properties
from hamcrest import has_property
from hamcrest import is_not as does_not

from zope import component

from nti.dataserver.users import User

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans
from nti.dataserver.tests.mock_dataserver import DataserverLayerTest

from nti.app.xapi.tests import SharedConfiguringTestLayer

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.xapi.interfaces import IAgent


class TestUserToAgent(DataserverLayerTest):

    layer = SharedConfiguringTestLayer

    @WithMockDSTrans
    def test_user_to_agent_default(self):
        user = User.create_user(self.ds, username=u'foo@bar')
        agent = IAgent(user)
        account = agent.account

        assert_that(account, has_properties('homePage', 'http://nextthought.com/username',
                                            'name', 'foo@bar'))

    @WithMockDSTrans
    def test_user_to_agent_username(self):
        user = User.create_user(self.ds, username=u'foo@bar')
        agent = component.getAdapter(user, IAgent, name='username')
        account = agent.account

        assert_that(account, has_properties('homePage', 'http://nextthought.com/username',
                                            'name', 'foo@bar'))

    @WithMockDSTrans
    def test_user_to_agent_anonymous(self):
        user = User.create_user(self.ds, username=u'foo@bar')
        agent = component.getAdapter(user, IAgent, name='anonymous')
        account = agent.account

        assert_that(account, has_properties('homePage', 'http://nextthought.com/external_oid',
                                            'name', does_not(contains_string('foo@bar'))))

        from_external = find_object_with_ntiid(agent.account.name)
        assert_that(from_external, has_property('username', 'foo@bar'))
