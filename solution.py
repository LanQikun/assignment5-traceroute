from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.
    myChecksum = 0
    myID = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)

    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)

    # Don’t send the packet yet , just return the final packet in this function.
    #Fill in end

    # So the function ending should look like this

    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [] #This is your list to use when iterating through each trace 
    tracelist2 = [] #This is your list to contain all traces

    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist2.append([str(ttl), "*", "Request timed out."])
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist2.append([str(ttl), "*", "Request timed out."])
                    #Fill in end
            except timeout:
                continue

            else:
                #Fill in start
                #Fetch the icmp type from the IP packet
                ip = addr[0]
                header = recvPacket[20:28]
                icmpType, code, icmpChecksum, packetID, sequence = struct.unpack("bbHHh", header)

                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    host = (gethostbyaddr(ip))[0]
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    host = "hostname not returnable"
                    timePast = str(int((timeReceived - t) * 1000)) + "ms"
                    item = list(map(str, [ttl, timePast, ip, host]))
                    tracelist2.append(item)
                    continue
                    #Fill in end

                if icmpType == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +
                    bytes])[0]
                    #Fill in start
                    timePast = str(int((timeReceived - t) * 1000)) + "ms"
                    item = list(map(str, [ttl, timePast, ip, host]))
                    tracelist2.append(item)
                    #Fill in end
                elif icmpType == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    timePast = str(int((timeReceived - t) * 1000)) + "ms"
                    item = list(map(str, [ttl, timePast, ip, host]))
                    tracelist2.append(item)
                    #Fill in end
                elif icmpType == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    timePast = str(int((timeReceived - t) * 1000)) + "ms"
                    item = list(map(str, [ttl, timePast, ip, host]))
                    tracelist2.append(item)
                    return tracelist2
                    #Fill in end
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    timePast = str(int((timeReceived - t) * 1000)) + "ms"
                    item = list(map(str, [ttl, timePast, ip, host, "error"]))
                    tracelist2.append(item)
                    return tracelist2
                    #Fill in end
                break
            finally:
                mySocket.close()

    return tracelist2


if __name__ == '__main__':
    get_route("google.co.il")
    # x = get_route("google.co.il")
    # print(x)
