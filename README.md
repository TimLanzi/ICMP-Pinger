# ICMP Pinger
A Python program to demonstrate the ICMP protocol. This program can take two command line arguments (both optional). The first argument is the desination IP address that you wish to ping, and the second argument being the number of pings. If either of these arguments are left out, the program will default to the IP address for localhost (127.0.0.1) and 20 pings.

The average RTT, maximum RTT, and minimum RTT will be printed upon completion, along with packet information being printed in real-time for each RTT. An error dictionary is also included in case an ICMP error code is encountered.
