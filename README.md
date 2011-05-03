What is it?
===========

SlothNS is an extension to DNS that aims to protect sensitive services
from DoS attacks by requiring the resolving client to perform a
proof-of-work (PoW) computation to obtain an IP. A PoW function is
costly (CPU time or RAM size) to compute, slowing down a DoS attack.
The returned IPs are randomized within 64-bits of the IPv6 address space
and each returned IP is tied to the requesting client &mdash; malicious
clients may not share resolved IPs to circumvent the system.

Please see `docs/project_proposal.md` for more information.

What works right now?
=====================

A very rough, prototype implementation of the idea is underway. A Twisted-based
DNS server is able to issue a PoW challenge and check the response before
returning a random IPv6 address. A Twisted-based resolver is provided to test
the server.

What remains to be done?
========================

 * Implement the new resolver in glibc to allow unmodified program to use SlothNS
 * Have the server register random resolved IPs with the system firewall to allow
   access to the protected service

Who is doing it?
================

The project authors are Nina Baker and Jevin Sweval.

Why are you doing it?
=====================

This project is for our [Fault-Tolerant Computer System Design class] [course_page]
at Purdue University.

[course_page]: https://engineering.purdue.edu/ee695b/public-web/

