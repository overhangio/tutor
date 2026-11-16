# Tutor Ethical Vulnerability Disclosure Policy


## Reporting a Vulnerability

To ensure the health of the codebase and the larger Open edX and Tutor communities, please do not create GitHub issues for a security vulnerability. Report any security vulnerabilities or concerns by sending an email to [security.tutor@edly.io](mailto:security.tutor@edly.io). To ensure a timely triage and fix of the security issue, include as many details you can when reporting the vulnerability. Some pieces of information to consider:

* The nature of the vulnerability, e.g.
  * Authentication and Authorization
  * Data Integrity and Confidentiality
  * Security Configurations
  * Third-party dependencies
* The impact of the security risk
* A detailed description of the steps necessary to reproduce the issue
* The links to the vulnerable code
* The links to third-party libraries/packages if the vulnerability is present in such a dependency.

## Docker image vulnerability scanning

The Docker images published by Tutor are [scanned weekly](https://github.com/overhangio/tutor/actions/workflows/scan-images.yml) with [Trivy](https://trivy.dev), and the reports are published in this repository's [Security tab](https://github.com/overhangio/tutor/security/code-scanning). Findings are triaged as follows:

* Critical and high-severity findings in components that Tutor itself installs (base OS packages, Node.js, build tooling) are fixed in Tutor.
* Findings in Python and Node.js dependencies pinned by edx-platform are reported upstream to the [edx-platform](https://github.com/openedx/edx-platform) project, which owns those version pins.
* Findings with no released fix are excluded from the weekly reports, since no action is possible; most of them are Ubuntu kernel-header CVEs that do not apply to containers, which use the host kernel.

## Bug Bounty
Edly/Tutor does not offer a bug bounty for reported vulnerabilities.
