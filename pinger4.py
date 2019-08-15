#####  for python 3.7  #####
#!/usr/bin/env python
#coding:utf-8
import os, sys, socket, struct, select, time

ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris.
def checksum(source_string):
  """
  I'm not too confident that this is right but testing seems
  to suggest that it gives the same answers as in_cksum in ping.c
  """
  #print('1')
  #print(source_string)
  sum = 0
  countTo = (len(source_string)/2)*2
  #print(countTo)
  count = 0
  while count<countTo:
    thisVal = source_string[count + 1]*256 + source_string[count]
    sum = sum + thisVal
    sum = sum & 0xffffffff # Necessary?
    count = count + 2
  if countTo<len(source_string):
    sum = sum + ord(source_string[len(source_string) - 1])
    sum = sum & 0xffffffff # Necessary?
  sum = (sum >> 16) + (sum & 0xffff)
  sum = sum + (sum >> 16)
  answer = ~sum
  answer = answer & 0xffff
  # Swap bytes. Bugger me if I know why.
  answer = answer >> 8 | (answer << 8 & 0xff00)
  #print('222')
  #print(answer)
  return answer
def receive_one_ping(my_socket, ID, timeout):
  """
  receive the ping from the socket.
  """
  timeLeft = timeout
  while True:
    startedSelect = time.time()
    whatReady = select.select([my_socket], [], [], timeLeft)
    howLongInSelect = (time.time() - startedSelect)
    if whatReady[0] == []: # Timeout
      return
    timeReceived = time.time()
    recPacket, addr = my_socket.recvfrom(1024)
    icmpHeader = recPacket[20:28]
    type, code, checksum, packetID, sequence = struct.unpack(
      "bbHHh", icmpHeader
    )
    if packetID == ID:
      bytesInDouble = struct.calcsize("d")
      timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
      return timeReceived - timeSent
    timeLeft = timeLeft - howLongInSelect
    if timeLeft <= 0:
      return
def send_one_ping(my_socket, dest_addr, ID):
  """
  Send one ping to the given >dest_addr<.
  """

  #print('11-1')
  #print(dest_addr)
  try :
    dest_addr = socket.gethostbyname(dest_addr)
  except :
    #print("socket error:2 - to be sure the network is connected  or [ %s ] is right" %dest_addr)
    pass
  # Header is type (8), code (8), checksum (16), id (16), sequence (16)
  #print('11-2')
  #print('the host is  : ' + dest_addr)
  my_checksum = 0
  #print('12')
  # Make a dummy heder with a 0 checksum.
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1) #压包
  #a1 = struct.unpack("bbHHh",header)  #my test
  #print('13')
  bytesInDouble = struct.calcsize("d")
  #print('14')
  data = (192 - bytesInDouble) * "Q"
  #print('15')
  data = struct.pack("d", time.time()) + bytes(data.encode('utf-8'))
  #print('16')
  # Calculate the checksum on the data and the dummy header.
  #print(header+data)
  #print("13-5")
  my_checksum = checksum(header + data)
  
  #print('13-2')
  # Now that we have the right checksum, we put that in. It's just easier
  # to make up a new header than to stuff it into the dummy.
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
  packet = header + data
  my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1
  #print('15')
def do_one(dest_addr, timeout):
  """
  Returns either the delay (in seconds) or none on timeout.
  """
  #print('3')
  icmp = socket.getprotobyname("icmp")
  #print('4')
  try:
    #print('5')
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    #print('6')
  except :
    #print('7')
    print('error:2')    
      #raise socket.error(msg)
    #raise # raise the original error
  #print('8')
  my_ID = os.getpid() & 0xFFFF
  #print('9')
  send_one_ping(my_socket, dest_addr, my_ID)
  #print('10')
  delay = receive_one_ping(my_socket, my_ID, timeout)
  my_socket.close()
  return delay
def verbose_ping(dest_addr, timeout = 2, count = 100):
  """
  Send >count< ping to >dest_addr< with the given >timeout< and display
  the result.
  """
  for i in range(count):
    print ("ping %s..." % dest_addr,)
    try:
      #print('1')
      delay = do_one(dest_addr, timeout)
    except :
      #print('2')
      print ("failed. (socket error:1 )" )
      break
    if delay == None:
      print ("failed. (timeout within %ssec.)" % timeout)
    else:
      delay = delay * 1000
      print( "get ping in %0.4fms" % delay)
	  
def return_delay(dest_addr, timeout = 2, count = 100):
  """
  Send >count< ping to >dest_addr< with the given >timeout< and display
  the result.
  """
  for i in range(count):
    #print ("ping %s..." % dest_addr,)
    try:
      #print('1')
      delay = do_one(dest_addr, timeout)
    except :
      #print('2')
      #print ("failed. (socket error:1 )" )
      delay='A'
      break
    '''
	if delay == None:
      delay == 'B'
      #print ("failed. (timeout within %ssec.)" % timeout)
    
	else:
      delay = delay * 1000
      print( "get ping in %0.4fms" % delay)
	  '''
  return delay
if __name__ == '__main__':
  verbose_ping("61.139.2.69",2,5)
