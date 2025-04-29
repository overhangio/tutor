import unittest

from tutor.commands import dev

from .base import TestCommandMixin


class DevTests(unittest.TestCase, TestCommandMixin):
    def test_dev_help(self) -> None:
        result = self.invoke(["dev", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)


class HostsParsing(unittest.TestCase):
    def test_host_port_single(self) -> None:
        ps_output = """{"Publishers":[{"PublishedPort":8000}]}"""
        host_port = dev.parse_ports(ps_output)
        self.assertEqual(host_port, [8000])

    def test_host_port_single_empty(self) -> None:
        ps_output = """{"Publishers":[{"PublishedPort":0}]}"""
        host_port = dev.parse_ports(ps_output)
        self.assertEqual(host_port, [])

    def test_host_port_multiple_services(self) -> None:
        ps_output = """{"Publishers":[{"PublishedPort":0}]}
        {"Publishers":[{"PublishedPort":8000}]}
        {"Publishers":[{"PublishedPort":8001}]}"""

        host_port = dev.parse_ports(ps_output)
        self.assertEqual(host_port, [8000, 8001])

    def test_host_port_multiple_publishers(self) -> None:
        ps_output = """{"Publishers":[{"PublishedPort":0}, {"PublishedPort":3276}, {"PublishedPort":8000}]}"""

        host_port = dev.parse_ports(ps_output)
        self.assertEqual(host_port, [3276, 8000])

    def test_host_port_multiple_services_publishers(self) -> None:
        ps_output = """{"Publishers":[{"PublishedPort":0}, {"PublishedPort":3276}, {"PublishedPort":8000}]}
        {"Publishers":[{"PublishedPort":0}, {"PublishedPort":8001}, {"PublishedPort":8002}]}"""
        host_port = dev.parse_ports(ps_output)
        self.assertEqual(host_port, [3276, 8000, 8001, 8002])
