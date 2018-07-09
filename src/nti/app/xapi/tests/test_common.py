#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

import unittest

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that

from nti.app.xapi.common import get_site
from nti.app.xapi.common import unpickle
from nti.app.xapi.common import get_creator
from nti.app.xapi.common import pickle_dump
from nti.app.xapi.common import redis_client
from nti.app.xapi.common import is_nonstr_iterable


class TestCommon(unittest.TestCase):

    def test_get_site(self):
        assert_that(get_site(None, object()), is_(none()))

    def test_redis_client(self):
        assert_that(redis_client(), is_(none()))

    def test_get_creator(self):
        assert_that(get_creator('foo'), is_('foo'))

    def test_pickle(self):
        d = pickle_dump('foo')
        assert_that(d, is_not(none()))
        assert_that(unpickle(d), is_('foo'))

    def test_is_nonstr_iterable(self):
        assert_that(is_nonstr_iterable('d'), is_(False))
        assert_that(is_nonstr_iterable(object()), is_(False))
        
        assert_that(is_nonstr_iterable(set()), is_(True))
        assert_that(is_nonstr_iterable(list()), is_(True))
        assert_that(is_nonstr_iterable(tuple()), is_(True))

        def sample():
            yield 5
            
        assert_that(is_nonstr_iterable(sample()), is_(True))