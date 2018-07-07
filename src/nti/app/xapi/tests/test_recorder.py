#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import fudge

import unittest

from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import has_length

from nti.app.xapi.recorder import LRSStatementRecorder
from nti.app.xapi.recorder import InMemoryStartmentRecorder

from nti.xapi.statement import Statement


class MockLRSClientStatementRecorder(LRSStatementRecorder):

    def __init__(self, mock_client):
        super(LRSStatementRecorder, self).__init__()
        self.mock_client = mock_client

    def _lrs_client(self):
        return self.mock_client

    
class TestLRSStatementRecorder(unittest.TestCase):

    def setUp(self):
        self.stmt = Statement()

    @fudge.patch('nti.xapi.client.LRSClient')
    def test_saves_single_stmt(self, mock_client):
        mock_client.provides('save_statement').provides('save_statements')
        mock_client.expects('save_statement').with_args(self.stmt)
        client = MockLRSClientStatementRecorder(mock_client)
        client.record_statements(self.stmt)

    @fudge.patch('nti.xapi.client.LRSClient')
    def test_saves_multiple_stmt(self, mock_client):
        mock_client.provides('save_statement').provides('save_statements')
        mock_client.expects('save_statements').with_args([self.stmt])
        client = MockLRSClientStatementRecorder(mock_client)
        client.record_statements([self.stmt])


class TestInMemoryStatementRecorder(TestLRSStatementRecorder):

    def test_saves_single_stmt(self):
        client = InMemoryStartmentRecorder()
        client.record_statements(self.stmt)

        assert_that(client, has_property('statements', has_length(1)))

    def test_saves_multiple_stmt(self):
        client = InMemoryStartmentRecorder()
        client.record_statements([self.stmt, self.stmt])

        assert_that(client, has_property('statements', has_length(2)))

    def test_requires_stmt(self):
        client = InMemoryStartmentRecorder()
        with self.assertRaises(TypeError):
            client.record_statements(object())
