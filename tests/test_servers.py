"""
Tests for server module
"""
import unittest
from ipaddress import IPv4Address, IPv6Address

from marshmallow import ValidationError

from app import servers


class ListServersTests(unittest.TestCase):
    """
    Class for list_servers tests
    """

    # def test_list_servers(self):
    #     """
    #     Tests if a dictionary of servers is returned when added
    #     """
    #     expected_result = {}

    #     servers.add_server(
    #         'DCS Server 2', '10.56.0.175', 10309, 'DCS')
    #     servers.add_server(
    #         'Arma Stasi Altis', '10.56.0.180', 2303, 'STEAM')
    #     servers.add_server(
    #         'Sprace Engineers URBW', '10.56.0.175', 27019, 'SPACE_ENGINEERS')

    #     self.assertEqual(servers.list_servers(), expected_result)


class AddServersTests(unittest.TestCase):
    """
    Class for add_servers tests
    """

    def test_add_servers_positive(self):
        """
        Tests if Server objects are created with valid values
        """
        dcs_server = servers.add_server(
            'DCS Server 1', '10.56.0.175', 10309, 'DCS')
        arma_server = servers.add_server(
            'Arma Server 1', '172.16.69.180', 2303, 'STEAM')
        se_server = servers.add_server(
            'Space Engineers Server 1', 'fe80::a00:20ff:feb9:17fa', 27019, 'SPACE_ENGINEERS')

        self.assertEqual(dcs_server['name'], 'DCS Server 1')
        self.assertEqual(dcs_server['ip_address'], IPv4Address('10.56.0.175'))
        self.assertEqual(dcs_server['port'], 10309)
        self.assertEqual(dcs_server['server_type'], servers.ServerType.DCS)
        self.assertEqual(arma_server['name'], 'Arma Server 1')
        self.assertEqual(arma_server['ip_address'],
                         IPv4Address('172.16.69.180'))
        self.assertEqual(arma_server['port'], 2303)
        self.assertEqual(arma_server['server_type'], servers.ServerType.STEAM)
        self.assertEqual(se_server['name'], 'Space Engineers Server 1')
        self.assertEqual(se_server['ip_address'],
                         IPv6Address('fe80::a00:20ff:feb9:17fa'))
        self.assertEqual(se_server['port'], 27019)
        self.assertEqual(se_server['server_type'],
                         servers.ServerType.SPACE_ENGINEERS)

    def test_add_servers_invalid_server_type(self):
        """
        Tests if a marshmallow.exceptions.ValidationError is thrown if an invalid type is specified
        """

        self.assertRaises(ValidationError, servers.add_server,
                          'Test', '10.0.0.1', 1000, 'FAIL')

    def test_add_servers_duplicate_name(self):
        """
        Tests if a ValueError is thrown if a duplicate server name is specified
        """
        servers.add_server('Test1', '10.0.0.1', 1000, 'DCS')

        self.assertRaises(ValueError, servers.add_server,
                          'Test1', '10.0.0.1', 1000, 'DCS')

    def test_add_servers_invalid_port(self):
        """
        Tests if a ValueError is thrown if a port outside valid 1-65535 range is set
        """

        self.assertRaises(ValidationError, servers.add_server,
                          'Test2', '10.0.0.1', 65536, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test3', '10.0.0.1', -1, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test4', '10.0.0.1', 0, 'DCS')

    def test_add_servers_invalid_ipv4(self):
        """
        Tests if a ValueError is thrown if an invalid IPv4 address is supplied
        """

        self.assertRaises(ValidationError, servers.add_server,
                          'Test5', '12345', 1000, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test6', '256.256.256.256', 1000, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test7', '1.2.3.4.5', 1000, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test8', 'string', 1000, 'DCS')

    def test_add_servers_invalid_ipv6(self):
        """
        Tests if a ValueError is thrown if an invalid IPv6 address is supplied
        """

        self.assertRaises(ValidationError, servers.add_server,
                          'Test9', '12345', 1000, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test10', '256.256.256.256', 1000, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test11', '1.2.3.4.5', 1000, 'DCS')
        self.assertRaises(ValidationError, servers.add_server,
                          'Test12', 'string', 1000, 'DCS')


class DeleteServersTests(unittest.TestCase):
    """
    Class for add_servers tests
    """

    def test_delete_servers_positive(self):
        """
        Tests if Server is successfully deleted
        """

        servers.add_server('Delete me', '10.56.0.175', 10309, 'DCS')

        self.assertIsNone(servers.delete_server('Delete me'))

    def test_delete_servers_raise_key_error(self):
        """
        Tests if KeyError is raised if server doesn't exist
        """

        with self.assertRaises(KeyError):
            servers.delete_server('I dont exist')


class UpdateServersTests(unittest.TestCase):
    """
    Class for add_servers tests
    """

    def test_update_servers_positive(self):
        """
        Tests if Server is successfully updated
        """

        servers.add_server('Update me', '10.0.0.1', 1000, 'DCS')
        server_info = {
            'name': 'Update me',
            'ip_address': '1.1.1.1',
            'port': 1000,
            'server_type': 'DCS',
            'password': 'password'
        }

        self.assertIsNone(servers.update_server('Update me', server_info))

    def test_update_servers_invalid_type(self):
        """
        Tests if Server is successfully updated
        """

        with self.assertRaises(ValidationError):
            server_info = {
                'name': 'Update me',
                'ip_address': '1.1.1.1',
                'port': 1000,
                'server_type': 'Fail',
                'password': 'password'
            }
            servers.update_server('Update me', server_info)


class SerialiseDeserialiseServersTest(unittest.TestCase):
    """
    Class to test data (de)serialisation
    """

    def test_data_serialise_equal_deserialise(self):
        """
        Tests that objects are successfully serialised to disk
        """
        servers.delete_server('*')

        server_list = {}
        server_list['DCS Server Serialise'] = servers.add_server(
            'DCS Server Serialise', '10.56.0.175', 10309, 'DCS')
        server_list['Arma Server Serialise'] = servers.add_server(
            'Arma Server Serialise', '172.16.69.180', 2303, 'STEAM')
        server_list['Space Engineers Server Serialise'] = servers.add_server(
            'Space Engineers Server Serialise', 'fe80::a00:20ff:feb9:17fa',
            27019, 'SPACE_ENGINEERS')

        self.assertIsNone(servers.save_servers())
        self.assertIsNone(servers.load_servers())
        print(servers.list_servers())
        print(server_list)
        self.assertEqual(servers.list_servers(), server_list)


if __name__ == '__main__':
    unittest.main()
