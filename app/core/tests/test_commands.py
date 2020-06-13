from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandsTestCase(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            print('on one')
            gi.return_value = True
            call_command('wait_for_db')
            print('end one..')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=None)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            print('on two')
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            print('end  two')
            self.assertEqual(gi.call_count, 6)
