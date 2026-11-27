from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import typing as t
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from tests.helpers import caddy_output, utc
from tests.helpers import fixture as _fixture
from tutor import caddy, fmt
from tutor.exceptions import TutorError

PEBBLE = "pebble-14000-dir"
STAGING = caddy.LETSENCRYPT_STAGING


def fixture(name: str) -> str:
    return _fixture(os.path.join("caddy", name))


def certificate(
    issuer: str,
    name: str,
    not_before: datetime = utc(2026, 11, 18),
    lifetime: int = 6,
    ari_time: t.Optional[datetime] = None,
) -> caddy.StoredCertificate:
    validity = (not_before, not_before + timedelta(days=lifetime))
    return caddy.StoredCertificate(issuer, name, (name,), validity, ari_time)


def domain(name: str, *issuers: str) -> caddy.Domain:
    return caddy.Domain(name, issuers or (caddy.LETSENCRYPT,), False)


def http_config(
    *hosts: str, policies: t.Optional[list[t.Any]] = None, **server: t.Any
) -> dict[str, t.Any]:
    """
    Caddy JSON configuration with a single server.
    """
    server.setdefault("listen", [":443"])
    server["routes"] = [{"match": [{"host": [host]}]} for host in hosts]
    config: dict[str, t.Any] = {"apps": {"http": {"servers": {"srv0": server}}}}
    if policies is not None:
        config["apps"]["tls"] = {"automation": {"policies": policies}}
    return config


class CertificateTests(unittest.TestCase):
    def test_parse_validity(self) -> None:
        # Pebble certificate, followed by its intermediate certificate
        self.assertEqual(
            (utc(2026, 11, 18, 15, 16, 45), utc(2026, 11, 24, 15, 16, 44)),
            caddy.parse_validity(fixture("lms.example.test.crt")),
        )
        # Let's Encrypt certificate and chain
        self.assertEqual(
            (utc(2026, 11, 3, 13, 44, 34), utc(2027, 2, 1, 13, 44, 33)),
            caddy.parse_validity(fixture("letsencrypt.org.crt")),
        )
        # Caddy internal CA: 12 hours
        not_before, not_after = caddy.parse_validity(fixture("dev.localhost.crt"))
        self.assertEqual(timedelta(hours=12), not_after - not_before)
        # GeneralizedTime after 2049
        self.assertEqual(
            utc(2081, 8, 21, 15, 19, 44),
            caddy.parse_validity(fixture("gentime.crt"))[1],
        )

    def test_parse_stored_certificate(self) -> None:
        stored = caddy.parse_stored_certificate(
            "/data/caddy/certificates/pebble-14000-dir/lms.example.test/lms.example.test.crt",
            fixture("lms.example.test.crt"),
            fixture("lms.example.test.json"),
        )
        self.assertEqual(PEBBLE, stored.issuer)
        self.assertEqual("lms.example.test", stored.name_dir)
        self.assertEqual(("lms.example.test",), stored.names)
        self.assertEqual(utc(2026, 11, 22, 2, 24, 18), stored.ari_time)

        # Internal issuer, without ARI
        stored = caddy.parse_stored_certificate(
            "/certificates/local/dev.localhost/dev.localhost.crt",
            fixture("dev.localhost.crt"),
            '{"sans":["dev.localhost"],"issuer_data":null}',
        )
        self.assertEqual(("dev.localhost",), stored.names)
        self.assertIsNone(stored.ari_time)
        self.assertIsNotNone(stored.validity)

    def test_parse_stored_certificate_short_path(self) -> None:
        with self.assertRaises(TutorError) as context:
            caddy.parse_stored_certificate("a.test.crt", "", "")
        self.assertIn("Unexpected certificate path: a.test.crt", str(context.exception))

    def test_parse_stored_certificate_invalid(self) -> None:
        path = "/certificates/local/wildcard_.example.com/wildcard_.example.com.crt"
        truncated = (
            fixture("lms.example.test.crt")[:200] + "\n-----END CERTIFICATE-----"
        )
        for crt in ["", "garbage", truncated]:
            for metadata in ["", "{garbled", "[]", '{"sans": "x"}']:
                stored = caddy.parse_stored_certificate(path, crt, metadata)
                self.assertIsNone(stored.validity)
                self.assertIsNone(stored.ari_time)
                self.assertEqual(("wildcard_.example.com",), stored.names)

    def test_parse_go_time(self) -> None:
        self.assertEqual(
            utc(2026, 11, 18, 21, 16, 50),
            caddy.parse_go_time("2026-11-18T21:16:50.009906428Z"),
        )
        self.assertEqual(
            utc(2026, 11, 18, 19, 16, 50),
            caddy.parse_go_time("2026-11-18T21:16:50+02:00"),
        )
        self.assertIsNone(caddy.parse_go_time(None))
        self.assertIsNone(caddy.parse_go_time("2026-11-18"))
        self.assertIsNone(caddy.parse_go_time("2026-13-18T21:16:50Z"))


class NamesTests(unittest.TestCase):
    def test_storage_key(self) -> None:
        self.assertEqual("learn.example.com", caddy.storage_key("Learn.Example.com"))
        self.assertEqual("wildcard_.example.com", caddy.storage_key("*.example.com"))
        self.assertEqual("fd00--1", caddy.storage_key("fd00::1"))
        self.assertEqual("10.1.2.3", caddy.storage_key("10.1.2.3"))

    def test_issuer_key(self) -> None:
        for key, module, ca in [
            (caddy.LETSENCRYPT, "acme", None),
            (STAGING, "acme", "https://acme-staging-v02.api.letsencrypt.org/directory"),
            ("acme.zerossl.com-v2-dv90", "acme", "https://acme.zerossl.com/v2/DV90"),
            (PEBBLE, "acme", "https://pebble:14000/dir"),
            ("ca.test", "acme", "https://ca.test"),
            ("local", "internal", None),
            ("myca", "internal", "myca"),
            ("zerossl", "zerossl", None),
        ]:
            issuer = {"module": module, "ca": ca} if ca else {"module": module}
            self.assertEqual(key, caddy.issuer_key(issuer))

    def test_is_internal(self) -> None:
        for name in [
            "localhost",
            "dev.localhost",
            "a.local",
            "a.internal",
            "a.home.arpa",
        ]:
            self.assertTrue(caddy.is_internal(name), name)
        for name in ["127.0.0.1", "10.1.2.3", "192.168.1.1", "fd00::1", "::1"]:
            self.assertTrue(caddy.is_internal(name), name)
        for name in ["learn.example.com", "localhost.example.com", "203.0.113.5x"]:
            self.assertFalse(caddy.is_internal(name), name)
        self.assertFalse(caddy.is_internal("8.8.8.8"))


class ScriptTests(unittest.TestCase):
    def test_script(self) -> None:
        script = caddy.script()
        self.assertNotIn(".key", script)
        self.assertIn("caddy adapt --config /etc/caddy/Caddyfile", script)
        # The default site port of the container is not overridden
        self.assertNotIn("default_site_port=", script)

    @unittest.skipIf(shutil.which("sh") is None, "sh is not available")
    def test_script_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            # Fake caddy executable
            bin_dir = os.path.join(root, "bin")
            os.makedirs(bin_dir)
            with open(os.path.join(bin_dir, "caddy"), "w", encoding="utf-8") as f:
                f.write(
                    '#!/bin/sh\n[ "$1 $3" = "adapt /etc/caddy/Caddyfile" ] || exit 1\n'
                    'echo \'{"apps": {}}\'\necho "some warning" >&2\n'
                )
            os.chmod(os.path.join(bin_dir, "caddy"), 0o755)
            running_config_path = os.path.join(root, "autosave.json")
            with open(running_config_path, "w", encoding="utf-8") as f:
                f.write('{"apps":{}}')
            certificates_dir = os.path.join(root, "certificates")
            name_dir = os.path.join(certificates_dir, PEBBLE, "lms.example.test")
            os.makedirs(name_dir)
            for name in ["lms.example.test.crt", "lms.example.test.json"]:
                with open(os.path.join(name_dir, name), "w", encoding="utf-8") as f:
                    f.write(fixture(name))
            with open(os.path.join(name_dir, "lms.example.test.key"), "w") as f:
                f.write("-----BEGIN EC PRIVATE KEY-----\nsecret\n")

            def run(certificates_dir: str, **env: str) -> str:
                env["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
                return subprocess.run(
                    ["sh", "-c", caddy.script(certificates_dir, running_config_path)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    env=env,
                    check=True,
                ).stdout.decode()

            output = run(certificates_dir)
            self.assertNotIn("PRIVATE", output)
            self.assertNotIn("secret", output)
            parsed = caddy.parse_output(output)
            self.assertEqual("", parsed.default_site_port)
            self.assertEqual({"apps": {}}, parsed.adapted)
            self.assertEqual(parsed.adapted, parsed.running)
            self.assertEqual(1, len(parsed.stored))
            self.assertEqual(("lms.example.test",), parsed.stored[0].names)
            self.assertEqual(PEBBLE, parsed.stored[0].issuer)
            self.assertEqual(utc(2026, 11, 22, 2, 24, 18), parsed.stored[0].ari_time)

            # No certificates directory, Caddy started without HTTPS
            output = run(os.path.join(root, "missing"), default_site_port=":80")
            parsed = caddy.parse_output(output)
            self.assertEqual([], parsed.stored)
            self.assertEqual(":80", parsed.default_site_port)


class ParseOutputTests(unittest.TestCase):
    def test_parse_output(self) -> None:
        output = caddy_output(
            '{"apps": {}}',
            certificates=[
                (
                    "/data/caddy/certificates/local/dev.localhost/dev.localhost.crt",
                    fixture("dev.localhost.crt"),
                    '{"sans":["dev.localhost"],"issuer_data":null}',
                )
            ],
        )
        # Text before the first section is ignored, and so are CRLF line endings
        parsed = caddy.parse_output("preamble\n" + output.replace("\n", "\r\n"))
        self.assertEqual({"apps": {}}, parsed.adapted)
        self.assertIsNone(parsed.running)
        self.assertEqual(1, len(parsed.stored))
        self.assertEqual(("dev.localhost",), parsed.stored[0].names)

    def test_parse_output_errors(self) -> None:
        output = caddy_output("{}")
        with self.assertRaises(TutorError) as context:
            caddy.parse_output(output.replace(f"{caddy.SEPARATOR} end", ""))
        self.assertIn("incomplete", str(context.exception))
        with self.assertRaises(TutorError) as context:
            caddy.parse_output(
                output.replace("adapt-status 0\n", "adapt-status 1\nError: bad line\n")
            )
        self.assertIn("Error: bad line", str(context.exception))
        with self.assertRaises(TutorError):
            caddy.parse_output(caddy_output("[]"))


class ManagedDomainsTests(unittest.TestCase):
    def test_tutor_caddyfile(self) -> None:
        adapted = json.loads(fixture("adapted-tutor.json"))
        self.assertEqual(
            [
                domain("learn.example.com"),
                domain("meilisearch.learn.example.com"),
                domain("studio.learn.example.com"),
            ],
            caddy.managed_domains(adapted),
        )

    def names(self, adapted: dict[str, t.Any]) -> list[str]:
        return [d.name for d in caddy.managed_domains(adapted)]

    def test_servers(self) -> None:
        self.assertEqual(["a.test"], self.names(http_config("A.test")))
        self.assertEqual(
            ["a.test"], self.names(http_config("a.test", listen=[":8443"]))
        )
        self.assertEqual(
            ["a.test"], self.names(http_config("a.test", listen=["tcp/:443"]))
        )
        # HTTP sites, or HTTPS disabled
        self.assertEqual([], self.names(http_config("a.test", listen=[":80"])))
        self.assertEqual([], self.names(http_config("a.test", listen=["0.0.0.0:80"])))
        config = http_config("a.test", listen=[":8080"])
        config["apps"]["http"]["http_port"] = 8080
        self.assertEqual([], self.names(config))
        for disabled in [{"disable": True}, {"disable_certificates": True}]:
            config = http_config("a.test", automatic_https=disabled)
            self.assertEqual([], self.names(config))

    def test_hosts(self) -> None:
        skip = {"skip": ["A.test"], "skip_certificates": ["b.test"]}
        config = http_config("a.test", "b.test", "c.test", automatic_https=skip)
        self.assertEqual(["c.test"], self.names(config))
        # The configuration is compared with the running one later: leave it unchanged
        self.assertEqual(["A.test"], skip["skip"])
        null_skip = {"skip": None, "skip_certificates": None}
        config = http_config("a.test", automatic_https=null_skip)
        self.assertEqual(["a.test"], self.names(config))
        self.assertEqual(
            ["*.wild.test"],
            self.names(http_config("{http.request.host}", "*.wild.test", "a..test")),
        )

    def test_internal(self) -> None:
        domains = caddy.managed_domains(
            http_config("dev.localhost", "10.1.2.3", "fd00::1")
        )
        self.assertEqual(3, len(domains))
        for d in domains:
            self.assertEqual((caddy.INTERNAL,), d.issuers)
            self.assertTrue(d.internal)

    def test_public_ip(self) -> None:
        # Without automation policies, IP addresses get an internal certificate
        self.assertEqual(
            [caddy.Domain("1.2.3.4", (caddy.INTERNAL,), True)],
            caddy.managed_domains(http_config("1.2.3.4")),
        )
        policies = [{"issuers": [{"module": "acme"}]}]
        self.assertEqual(
            [caddy.Domain("1.2.3.4", (caddy.LETSENCRYPT,), False)],
            caddy.managed_domains(http_config("1.2.3.4", policies=policies)),
        )

    def test_policies(self) -> None:
        # A single site with "tls internal": other sites use the default issuer
        policies = [
            {"subjects": ["a.test"]},
            {"subjects": ["b.test"], "issuers": [{"module": "internal"}]},
        ]
        self.assertEqual(
            [
                caddy.Domain("a.test", (caddy.LETSENCRYPT,), False),
                caddy.Domain("b.test", (caddy.INTERNAL,), True),
                caddy.Domain("c.test", (caddy.LETSENCRYPT,), False),
            ],
            caddy.managed_domains(
                http_config("a.test", "b.test", "c.test", policies=policies)
            ),
        )
        # Global "acme_ca" option
        pebble = {"module": "acme", "ca": "https://pebble:14000/dir"}
        policies = [{"subjects": ["dev.localhost"]}, {"issuers": [pebble]}]
        self.assertEqual(
            [
                caddy.Domain("a.test", (PEBBLE,), False),
                caddy.Domain("dev.localhost", (caddy.INTERNAL,), True),
            ],
            caddy.managed_domains(
                http_config("a.test", "dev.localhost", policies=policies)
            ),
        )
        # An internal name with an issuer of its own ("tls { issuer acme }"), next to
        # an internal name without one, as adapted by Caddy 2.11.7
        policies = [
            {"subjects": ["a.localhost"], "issuers": [pebble]},
            {"subjects": ["b.localhost"]},
            {"issuers": [pebble]},
        ]
        self.assertEqual(
            [
                caddy.Domain("a.localhost", (PEBBLE,), False),
                caddy.Domain("b.localhost", (caddy.INTERNAL,), True),
            ],
            caddy.managed_domains(
                http_config("a.localhost", "b.localhost", policies=policies)
            ),
        )
        # Global "email" option
        zerossl = {"module": "acme", "ca": "https://acme.zerossl.com/v2/DV90"}
        policies = [{"subjects": ["a.test"], "issuers": [{"module": "acme"}, zerossl]}]
        self.assertEqual(
            [
                caddy.Domain(
                    "a.test", (caddy.LETSENCRYPT, "acme.zerossl.com-v2-dv90"), False
                )
            ],
            caddy.managed_domains(http_config("a.test", policies=policies)),
        )
        # Global "local_certs" option
        policies = [{"issuers": [{"module": "internal"}]}]
        self.assertEqual(
            [caddy.Domain("a.test", (caddy.INTERNAL,), True)],
            caddy.managed_domains(http_config("a.test", policies=policies)),
        )


class ReportTests(unittest.TestCase):
    def statuses(self, report: caddy.Report) -> list[tuple[str, str, str]]:
        return [(row.domain, row.status, row.issuer) for row in report.rows]

    def test_no_certificate(self) -> None:
        domains = [domain("a.test"), caddy.Domain("dev.localhost", ("local",), True)]
        report = caddy.build_report(domains, [], utc(2026, 11, 18))
        self.assertEqual(
            [
                ("a.test", caddy.STATUS_MISSING, caddy.LETSENCRYPT),
                ("dev.localhost", caddy.STATUS_MISSING, "local"),
            ],
            self.statuses(report),
        )
        self.assertEqual([domains[0]], report.new)
        self.assertEqual(0, report.stored_count)

    def test_status(self) -> None:
        domains = [domain("a.test")]
        ari_time = utc(2026, 11, 22)
        stored = [certificate(caddy.LETSENCRYPT, "a.test", ari_time=ari_time)]

        def status(now: datetime) -> str:
            report = caddy.build_report(domains, stored, now)
            self.assertEqual([], report.new)
            return report.rows[0].status

        self.assertEqual(caddy.STATUS_VALID, status(utc(2026, 11, 21)))
        self.assertEqual(caddy.STATUS_RENEWAL_DUE, status(utc(2026, 11, 22)))
        self.assertEqual(caddy.STATUS_EXPIRED, status(utc(2026, 11, 24)))

    def test_renewal_time(self) -> None:
        # Caddy renews at the ARI time, or when a third of the lifetime remains, if
        # that comes first
        validity = (utc(2026, 11, 18), utc(2026, 11, 24))
        self.assertEqual(
            (utc(2026, 11, 21), False), caddy.renewal_time(validity, utc(2026, 11, 21))
        )
        self.assertEqual(
            (utc(2026, 11, 22), False), caddy.renewal_time(validity, utc(2026, 11, 23))
        )
        # Without ARI, or with the ARI time of the previous certificate
        self.assertEqual((utc(2026, 11, 22), True), caddy.renewal_time(validity, None))
        self.assertEqual(
            (utc(2026, 11, 22), True), caddy.renewal_time(validity, utc(2026, 11, 10))
        )
        stored = [certificate(caddy.LETSENCRYPT, "a.test", ari_time=utc(2026, 11, 23))]
        report = caddy.build_report([domain("a.test")], stored, utc(2026, 11, 22, 12))
        self.assertEqual(caddy.STATUS_RENEWAL_DUE, report.rows[0].status)

    def test_issuers(self) -> None:
        domains = [domain("a.test"), domain("b.test"), domain("c.test")]
        stored = [
            certificate(STAGING, "a.test"),
            certificate(caddy.LETSENCRYPT, "a.test"),
            certificate(STAGING, "b.test"),
            certificate(caddy.LETSENCRYPT, "old.test"),
        ]
        report = caddy.build_report(domains, stored, utc(2026, 11, 19))
        self.assertEqual(
            [
                ("a.test", caddy.STATUS_VALID, caddy.LETSENCRYPT),
                ("a.test", caddy.STATUS_NOT_USED, STAGING),
                ("b.test", caddy.STATUS_MISSING, caddy.LETSENCRYPT),
                ("b.test", caddy.STATUS_NOT_USED, STAGING),
                ("c.test", caddy.STATUS_MISSING, caddy.LETSENCRYPT),
                ("old.test", caddy.STATUS_NOT_CONFIGURED, caddy.LETSENCRYPT),
            ],
            self.statuses(report),
        )
        self.assertEqual(["b.test", "c.test"], [d.name for d in report.new])
        self.assertEqual(4, report.stored_count)

    def test_most_recent_certificate(self) -> None:
        domains = [domain("a.test", PEBBLE, caddy.LETSENCRYPT)]
        stored = [
            certificate(PEBBLE, "a.test", utc(2026, 11, 1)),
            certificate(caddy.LETSENCRYPT, "a.test", utc(2026, 11, 10)),
        ]
        report = caddy.build_report(domains, stored, utc(2026, 11, 12))
        self.assertEqual(stored[1], report.rows[0].certificate)
        self.assertEqual(caddy.STATUS_NOT_USED, report.rows[1].status)

        # We cannot tell whether an unreadable certificate is the most recent one:
        # report it, rather than an older one
        stored[1] = caddy.StoredCertificate(
            caddy.LETSENCRYPT, "a.test", ("a.test",), None, None
        )
        report = caddy.build_report(domains, stored, utc(2026, 11, 12))
        self.assertEqual(stored[1], report.rows[0].certificate)
        self.assertEqual(caddy.STATUS_UNREADABLE, report.rows[0].status)
        self.assertEqual(caddy.STATUS_NOT_USED, report.rows[1].status)

    def test_wildcard_and_unreadable(self) -> None:
        domains = [domain("*.wild.test"), domain("a.test")]
        stored = [
            certificate(caddy.LETSENCRYPT, "wildcard_.wild.test"),
            caddy.StoredCertificate(
                caddy.LETSENCRYPT, "a.test", ("a.test",), None, None
            ),
            caddy.StoredCertificate(
                "local", "x.test", ("x.test", "y.test"), None, None
            ),
        ]
        report = caddy.build_report(domains, stored, utc(2026, 11, 19))
        self.assertEqual(
            [
                ("*.wild.test", caddy.STATUS_VALID, caddy.LETSENCRYPT),
                ("a.test", caddy.STATUS_UNREADABLE, caddy.LETSENCRYPT),
                ("x.test, y.test", caddy.STATUS_UNREADABLE, "local"),
            ],
            self.statuses(report),
        )
        self.assertEqual([], report.new)
        # The unreadable certificate of a.test is in use
        self.assertEqual((3, 2), (report.stored_count, report.in_use_count))


class FormatReportTests(unittest.TestCase):
    def format_report(self, report: caddy.Report, now: datetime) -> list[str]:
        return [
            " | ".join(column.strip() for column in line.split("\t"))
            for line in caddy.format_report(report, now, "tutor logs").splitlines()
        ]

    def test_format_report(self) -> None:
        domains = [domain("a.test"), domain("b.test"), domain("c.test")]
        stored = [
            certificate(caddy.LETSENCRYPT, "a.test", ari_time=utc(2026, 11, 21, 2, 24)),
            certificate(caddy.LETSENCRYPT, "b.test", lifetime=3),
            certificate(STAGING, "c.test", lifetime=9),
        ]
        now = utc(2026, 11, 23)
        lines = self.format_report(caddy.build_report(domains, stored, now), now)
        self.assertEqual(
            [
                "DOMAIN | STATUS | ISSUER | EXPIRES (UTC) | RENEWAL (UTC)",
                "a.test | renewal due | Let's Encrypt | 2026-11-24 00:00 (in 1 day) | 2026-11-21 02:24",
                "b.test | expired | Let's Encrypt | 2026-11-21 00:00 (2 days ago) | ~2026-11-20 00:00",
                "c.test | missing (will be requested) | Let's Encrypt | - | -",
                "c.test | not used | Let's Encrypt (staging) | 2026-11-27 00:00 (in 4 days) | -",
                "",
                "Certificates stored by Caddy: 3, of which 2 are in use.",
            ],
            lines[:7],
        )
        self.assertTrue(lines[7].startswith("Renewals due: 2. Caddy renews"))
        self.assertEqual("New certificates that Caddy will request: 1.", lines[8])
        self.assertEqual(
            "If they remain missing, check the Caddy logs with `tutor logs`.", lines[9]
        )
        self.assertIn("50 new certificates per registered domain", lines[10])
        self.assertIn(caddy.DOCS_URL, lines[10])
        self.assertTrue(lines[11].startswith("~: estimated renewal date"))
        self.assertEqual(12, len(lines))

    def test_format_report_summary(self) -> None:
        # Not Let's Encrypt, nothing estimated, nothing new
        now = utc(2026, 11, 22, 12)
        ari_time = utc(2026, 11, 21)
        stored = [
            certificate(PEBBLE, "a.test", ari_time=ari_time),
            certificate(caddy.LETSENCRYPT, "a.test", not_before=utc(2026, 11, 10)),
        ]
        report = caddy.build_report([domain("a.test", PEBBLE)], stored, now)
        self.assertEqual(
            [
                "Certificates stored by Caddy: 2, of which 1 is in use.",
                "Renewals due: 1.",
                "New certificates that Caddy will request: 0.",
            ],
            self.format_report(report, now)[-3:],
        )
        lines = self.format_report(report, utc(2026, 11, 23, 19))
        self.assertIn("(in 5 hours)", lines[1])
        lines = self.format_report(report, utc(2026, 11, 23, 23, 59, 30))
        self.assertIn("(in less than a minute)", lines[1])

    def test_relative_time(self) -> None:
        now = utc(2026, 11, 23, 12)
        for when, text in [
            (utc(2026, 11, 23, 12, 1), "in 1 minute"),
            (utc(2026, 11, 23, 12, 59, 59), "in 59 minutes"),
            (utc(2026, 11, 23, 13), "in 1 hour"),
            (utc(2026, 11, 23, 11, 15), "45 minutes ago"),
            (utc(2026, 11, 22, 10), "1 day ago"),
            (utc(2026, 11, 23, 12, 0, 59), "in less than a minute"),
            (utc(2026, 11, 23, 11, 59, 30), "less than a minute ago"),
        ]:
            self.assertEqual(text, caddy._relative_time(when, now))


class PrintCertificatesTests(unittest.TestCase):
    def print_certificates(
        self, output: str, **config: t.Any
    ) -> tuple[list[str], MagicMock]:
        run_script = MagicMock(return_value=output.encode())
        with patch.object(fmt, "echo") as echo:
            with patch.object(caddy, "utcnow", return_value=utc(2026, 11, 19)):
                caddy.print_certificates(
                    {"ENABLE_HTTPS": True, **config},
                    run_script,
                    "tutor local start -d caddy",
                    "tutor local reboot -d caddy",
                    "tutor local logs caddy",
                )
        return [str(call.args[0]) for call in echo.call_args_list], run_script

    def test_not_running(self) -> None:
        run_script = MagicMock(side_effect=TutorError("Command failed"))
        with self.assertRaises(TutorError) as context:
            caddy.print_certificates(
                {"ENABLE_HTTPS": True}, run_script, "start", "restart", "logs"
            )
        self.assertIn("Is it running? Start it with `start`.", str(context.exception))

    def test_invalid_caddyfile(self) -> None:
        output = caddy_output("").replace(
            "adapt-status 0\n", "adapt-status 1\nno such file\n"
        )
        run_script = MagicMock(return_value=output.encode())
        with self.assertRaises(TutorError) as context:
            caddy.print_certificates(
                {"ENABLE_HTTPS": True}, run_script, "start", "restart", "logs"
            )
        self.assertIn("no such file", str(context.exception))
        self.assertIn("restart Caddy with `restart`", str(context.exception))

    def test_disabled(self) -> None:
        output, run_script = self.print_certificates("", ENABLE_HTTPS=False)
        self.assertIn("ENABLE_HTTPS is false", output[0])
        run_script.assert_not_called()
        output, run_script = self.print_certificates("", ENABLE_WEB_PROXY=False)
        self.assertIn("ENABLE_WEB_PROXY is false", output[0])
        run_script.assert_not_called()

    def test_started_without_https(self) -> None:
        adapted = json.dumps(http_config("a.test", listen=[":80"]))
        output, _ = self.print_certificates(
            caddy_output(adapted, adapted, default_site_port=":80")
        )
        self.assertEqual(1, len(output))
        self.assertIn("started before HTTPS was enabled", output[0])
        self.assertIn("`tutor local reboot -d caddy`", output[0])

    def test_no_certificates(self) -> None:
        # Automatic HTTPS is disabled, even though some certificates are stored
        path = f"{caddy.CERTIFICATES_DIR}/{caddy.LETSENCRYPT}/a.test/a.test.crt"
        adapted = http_config("a.test", automatic_https={"disable": True})
        output, _ = self.print_certificates(
            caddy_output(json.dumps(adapted), certificates=[(path, "crt", "")])
        )
        self.assertEqual(1, len(output))
        self.assertIn('"auto_https off"', output[0])
        adapted = http_config("a.test", listen=[":80"])
        output, _ = self.print_certificates(caddy_output(json.dumps(adapted)))
        self.assertIn("does not obtain SSL/TLS certificates automatically", output[0])
        adapted = http_config("a.test", automatic_https={"disable_certificates": True})
        output, _ = self.print_certificates(caddy_output(json.dumps(adapted)))
        self.assertIn("does not obtain SSL/TLS certificates automatically", output[0])

    def test_storage_module(self) -> None:
        adapted = http_config("a.test")
        adapted["storage"] = {"module": "redis"}
        output, _ = self.print_certificates(caddy_output(json.dumps(adapted)))
        self.assertEqual(1, len(output))
        self.assertIn('"redis" storage module', output[0])

    def test_running_configuration(self) -> None:
        adapted = json.dumps(http_config("a.test"))
        output, _ = self.print_certificates(caddy_output(adapted, running=adapted))
        self.assertEqual(1, len(output))
        self.assertIn("a.test", output[0])
        output, _ = self.print_certificates(caddy_output(adapted, running="{}"))
        self.assertEqual(2, len(output))
        self.assertIn("older configuration than its Caddyfile", output[1])
        self.assertIn("`tutor local reboot -d caddy`", output[1])

    def test_expired(self) -> None:
        adapted = json.dumps(http_config("lms.example.test"))
        path = f"{caddy.CERTIFICATES_DIR}/{caddy.LETSENCRYPT}/lms.example.test/lms.example.test.crt"
        certificates = [(path, fixture("lms.example.test.crt"), "")]
        output, _ = self.print_certificates(
            caddy_output(adapted, adapted, certificates)
        )
        self.assertEqual(1, len(output))
        with patch.object(caddy, "utcnow", return_value=utc(2026, 12, 1)):
            run_script = MagicMock(
                return_value=caddy_output(adapted, adapted, certificates).encode()
            )
            with patch.object(fmt, "echo") as echo:
                caddy.print_certificates(
                    {"ENABLE_HTTPS": True},
                    run_script,
                    "start",
                    "restart",
                    "tutor local logs caddy",
                )
        alerts = [str(call.args[0]) for call in echo.call_args_list][1:]
        self.assertEqual(1, len(alerts))
        self.assertIn("could not renew them: lms.example.test.", alerts[0])
        self.assertIn("`tutor local logs caddy`", alerts[0])
