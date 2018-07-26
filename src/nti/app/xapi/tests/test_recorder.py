#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ 

import fudge

import unittest

from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import has_length

from nti.app.xapi.recorder import BufferingStatementRecorder
from nti.app.xapi.recorder import LRSStatementRecorder
from nti.app.xapi.recorder import InMemoryStatementRecorder

from nti.xapi.statement import Statement


class MockLRSClientStatementRecorder(LRSStatementRecorder):

    def __init__(self, mock_client):
        self.mock_client = mock_client

    def _lrs_client(self):
        return self.mock_client

    @property
    def client(self):
        return self._lrs_client()

    
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
        client = InMemoryStatementRecorder()
        client.record_statements(self.stmt)
        assert_that(client, has_property('statements', has_length(1)))

    def test_saves_multiple_stmt(self):
        client = InMemoryStatementRecorder()
        client.record_statements([self.stmt, self.stmt])
        assert_that(client, has_property('statements', has_length(2)))

    def test_requires_stmt(self):
        client = InMemoryStatementRecorder()
        with self.assertRaises(AssertionError):
            client.record_statements(object())


class TestBufferedRecorder(TestLRSStatementRecorder):

    def setUp(self):
        super(TestBufferedRecorder, self).setUp()
        self.backing = InMemoryStatementRecorder()
        self.recorder = BufferingStatementRecorder(self.backing)

    def test_saves_single_stmt(self):
        self.recorder.record_statements(self.stmt)
        assert_that(self.backing, has_property('statements', has_length(0)))
        self.recorder.flush()
        assert_that(self.backing, has_property('statements', has_length(1)))

    def test_saves_multiple_stmt(self):
        self.recorder.record_statements([self.stmt, self.stmt])
        assert_that(self.backing, has_property('statements', has_length(0)))
        self.recorder.flush()
        assert_that(self.backing, has_property('statements', has_length(2)))

    def test_requires_stmt(self):
        with self.assertRaises(AssertionError):
            self.recorder.record_statements(object())
