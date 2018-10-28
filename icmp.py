#!/usr/python3
#########################
# Tim Lanzi				#
# COSC 370				#
# ICMP Pinger			#
#########################

import struct, sys, os, socket, time

# main ping function
def ping():
	# fetch destination IP address from command line arguments
	# ping localhost 20 times if no arguments
	if (len(sys.argv) == 1):
		dest = "127.0.0.1"
	else:
		dest = sys.argv[1]

	# convert internet address to IP address if needed
	try:
		if(socket.inet_aton(dest)):
			pass
	except:
		try:
			dest = socket.gethostbyname(dest)
		except:
			print("Could not resolve host")
			exit()

	# create raw socket
	sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_RAW,
							proto = socket.IPPROTO_ICMP)

	# set timeout to 1 sec per assignment
	sock.settimeout(1.0)

	# EXTRA CREDIT: use process id for the ID value in the ICMP message
	pid = os.getpid()

	# EXTRA CREDIT: get number of pings from command line
	if (len(sys.argv) == 3):
		pingCount = int(sys.argv[2])
	else:
		pingCount = 20		#default to 20 if no argument

	rtts = []
	numTimeout = 0

	for sequence in range(pingCount):
		print("Sending packet id {}, seq {}".format(pid, sequence))

		myChecksum  = 0		# make sure checksum is initialized to 0

		# packing an ICMP header
		# network byte order for the integers (!), echo request (8), code (0),
		# checksum (myChecksum), message id (pid), and sequence number
		header = struct.pack("!bbHHH", 8, 0, myChecksum, pid, sequence)

		# pack the time
		data = struct.pack("d", time.time())

		# calculate checksum
		myChecksum = calcChecksum(header + data)

		# pack new checksum
		header = struct.pack("!bbHHH", 8, 0, myChecksum, pid, sequence)

		# sending out header and data
		sock.sendto(header + data, (dest, 1))

		# record send time for appropriate sleep throttling
		sendTime = time.time()

		# try to receive a message from the socket
		recv = []
		try:
			recv = sock.recv(1024)
			recvTime = time.time()

			# look at the header to make sure it wasn't an outgoing message
			icmpHeader = recv[20:28]
			pktType, pktCode, pktChecksum, pktPID, pktSeq = struct.unpack("!bbHHH", icmpHeader)

			# try to receive again if it was the outgoing message
			if (pktType == 8):
				recv = sock.recv(1024)
				recvTime = time.time()
		except socket.timeout:
			numTimeout += 1
			print("Timed out")
			pass
		except socket.error:
			print("Unexpected error")
			raise

		# decode full IP buffer if we have receieved one
		if (len(recv) > 0):
			icmpHeader = recv[20:28]
			icmpData = recv[28:]

			pktType, pktCode, pktChecksum, pktPID, pktSeq = struct.unpack("!bbHHH", icmpHeader)

			# only try to decode the packet if it was sent from this client
			if (pktPID == pid):

				if (pktType == 0):
					# try to decode the double precision time that was encoded into the original message
					try:
						pktTime = struct.unpack("d", icmpData[0:8])
					except:
						print("Unexpected data size: ",icmpData)

					# calculate the RTT
					elapseTime = (recvTime - pktTime[0])*1000.0

					# print information about each ping
					print("Type: " + str(pktType) + "   Code: " + str(pktCode)
							+ "   ID: " + str(pktPID) + "   Sequence: " + str(pktSeq)
							 + "   Time: " + str(elapseTime) + "ms")

					# append RTT value for current ping to list of RTTs
					rtts.append(elapseTime)

			# EXTRA CREDIT: Decode ICMP response error codes
			if (pktType == 3):
				errDict(pktCode)

		# sets current sleep time to evenly space the pings
		nowTime = time.time()
		sleepTime = 1.0 - (nowTime-sendTime)
		if (sleepTime < 0):
			sleepTime = 0

		time.sleep(sleepTime)

	# calculate the stats on the list of RTTs
	avg, minimum, maximum = stats(rtts)

	# calculate packet loss
	pktLoss = (float(numTimeout) / float(pingCount)) * 100.0

	# print RTT stats
	print("\nMinimum RTT: " + str(minimum) + "ms   Maximum RTT: "
			+ str(maximum) + "ms   Average RTT: " + str(avg) + "ms   Packet Loss Rate: "
				+ str(pktLoss) + "%")


# function to calculate the minimum, maximum, and average RTT for each loop
def stats(rtts):

	# if all pings timed out return all stats as 0
	if(len(rtts) == 0):
		return 0.0, 0.0, 0.0

	# calculate min and max RTT
	minimum = min(rtts)
	maximum = max(rtts)

	# calculate average RTT
	average = sum(rtts)
	average = average / len(rtts)

	#return stats
	return average, minimum, maximum


# error dictionary
def errDict(code):
	if (code == 0):
		print("Net Unreachable")
	elif (code == 1):
		print("Host Unreachable")
	elif (code == 2):
		print("Protocol Unreachable")
	elif (code == 3):
		print("Port Unreachable")
	elif (code == 4):
		print("Error Code 4")
	elif (code == 5):
		print("Source Route Failed")
	elif (code == 6):
		print("Destination Network Unknown")
	elif (code == 7):
		print("Destination Host Unknown")
	elif (code == 8):
		print("Source Host Isolated")
	else:
		print("Error Code {}".format(code))


# function to calculate the checksum taken verbatim from RFC 1071 Section 4.1, converted to Python here
def calcChecksum(data):
	sum = 0
	count = len(data)
	i = 0

	# summing data array buffer 2 bytes at a time
	while (count > 1):
		tmp = (data[i] << 8) | data[i+1]
		sum += tmp
		count -= 2
		i += 2

	# add leftover byte
	if (count > 0):
		sum += data[len(data)-1]

	# fold 32 bit sum to 16 bits
	sum = (sum & 0xffff) + (sum >> 16)
	sum = (sum & 0xffff) + (sum >> 16)

	# 1's complement
	checksum = ~sum

	# make sure to return 16 bit value
	return checksum & 0xffff


if __name__ == "__main__":
	ping()
