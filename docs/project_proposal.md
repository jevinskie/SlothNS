Nina Baker  
Jevin Sweval  
2011-02-15  
ECE 695b: Fault-Tolerant Computer System Design

Course Project Proposal
=======================

Distributed Denial of Service (DDoS) attacks are becoming increasingly common
and higher profile. Some recent examples of this trend are the crippling DDoS
attacks against MasterCard, Visa and PayPal websites in response to those
companies refusing to accept donations to WikiLeaks. We propose an extension to
DNS that permits randomization of the IP address of a service and a
proof-of-work system to lease access to the randomized IPs to requesting users.
By providing the service at unique, per-client, randomized IPs, DDoS attacks
are complicated by requiring a costly DNS lookup before an attacker created
each connection to a server.

The problem of massive unsolicited accesses denying service to legitimate users
is not new: spammers have been DDoSing users’ inboxes for many years. HashCash
was an innovative proof-of-work approach at reducing email spam. To send an
email using HashCash, the sender would perform an expensive (in terms of CPU
time and/or memory) computation (the proof of work function) to prove
to the recipient that they were a legitimate user without using cumbersome
systems like signed certificates. Spammers must also compute the costly
function to send emails, effectively throttling the spammers by making sending
emails “costly”. The properties of the proof-of-work function make verifying
the client computation very efficient even though computing the function is
very inefficient. Our approach also uses proof-of-work functions to throttle
access to valuable resources.

Proof-of-work computations only help show that a user is legitimate - they do
not actually control access to the desired service. To control access to the
service, we will firewall the service from any outside access. Service access
will only be provided by NAT tunnels from randomly generated IPs that are
unique per client. Use of randomized IPs prevents an attacker from specifying a
single IP to attack - each new client must access the service by first
performing the proof-of-work computation to obtain a unique, random IP. The
costly DNS look-up flips traditional workload and makes connection
establishment resource-costly to the client and resource-cheap to the server.

There are two main points of novelty that our project would bring to this
area of security work. First of all, we would make use of the greatly
broader address space of IPv6, in which a greater degree of randomization
can be used with a small impact on the utilization of the address space.
This will extend the work done in [1]. We will also base our work on the
DNS model, and modify it to incorporate the functionality of IP
randomization (per-client assignment) and proof-of-work cost assessment.
This solution will reduce the overhead present in [2], while also
incorporating the IP randomization feature that can thwart large scale
attacks that use pre-determined IP lists.

In our approach, we use a modified DNS server and client to provide a
unique, random IP of a service to only legitimate users. The client’s
proof-of-work is integrated into the DNS resolution process. A client who
wants to access a service will perform a DNS request on the hostname that
provides this service. In our example we will use the web server at
foo.com.The authoritative DNS server for foo.com has been modified to
include our proposed proof-of-work support. The DNS server will respond to
the initial DNS request by delegating the answer to another DNS server
(this delegated server may actually be the same DNS server that sent the
 initial DNS response) in addition to issuing a proof-of-work challenge to
the client (included as an additional DNS resource records). The server
computes the resource-costly challenge before sending the second DNS
request, which includes the challenge response, to the delegated DNS
server. Upon receiving the second DNS request, the DNS sever quickly (due
to the asymetrical properties of the proof-of-work function) checks
response to the challenge. If the response is valid, the DNS server will
request a new random IP to provide the service from.

To allocate a new, random IP to serve a client, we will utilize the vast
address space provided to us by IPv6. With IPv6, the first 64-bits of the
address specify a host. The last 64-bits of each IP address are defined as
an “interface identifier” and are routable in any way that the host
desires. The IP addresses returned by the second DNS request will be
randomized within those least-significant 64-bits. To connect these
randomized IPs to the actual service, the hosting computer will NAT the
random IP to the internal (no routes from external hosts) service. Within
the NAT capability, most likely Linux iptables, each random IP will be
paired to the requesting IP, preventing an attacker from sharing a random
IP with other attackers.

If our project is successful, it will provide a way to mitigate DDoS
attacks while requiring only a modified DNS client and server. No other
Internet technologies need to be modified to utilize our DDoS mitigation
strategy. We will be able to demonstrate, either through simulation or a
real world benchmark, that service degradation due to DDoS attacks is
reduced while still allowing access to legitimate users.

References
----------

[1] S. Antonatos, P. Akritidis, E.P. Markatos, K.G. Anagnostakis, “Defending
against hitlist worms using network address space randomization,” Computer
Networks, Volume 51, Issue 12, 22 August 2007, Pages 3471-3490, ISSN 1389-1286  
doi: 10.1016/j.comnet.2007.02.006.  
url: <http://www.sciencedirect.com/science/article/B6VRG-4N61FYX-2/2/95718ac3f33f2c1ef41e2e9c5dad4f17>

[2] Mankins, D.; Krishnan, R.; Boyd, C.; Zao, J.; Frentz, M.; , "Mitigating
distributed denial of service attacks with dynamic resource pricing," Computer
Security Applications Conference, 2001. ACSAC 2001. Proceedings 17th Annual ,
vol., no., pp. 411- 421, 10-14 Dec. 2001  
doi: 10.1109/ACSAC.2001.991558  
url: <http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=991558&isnumber=21388>

[3] Back, Adam; “Hashcash - A Denial of Service Counter-Measure,” 2002  
url: <http://hashcash.org/hashcash.pdf>
