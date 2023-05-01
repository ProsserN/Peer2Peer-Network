# peer2peer.py
# CIS-490A
# Tyler Prosser
# 26-4-23
#
# This program will combine the functionality of 
# the vincent client and server programs. specifically,
# the server functionality  is added to a copy of the client.
# Concretely,
# 1. the server variables ledger and client_dict are added. 
# 2. listen and handle incoming packets 
# 3. add getclientlist command 
# 4. handle rx of getclientlist command
# 5. everything that used to be sent to the server
#    send to everyone in clientdict
#
# This client program prints messages from the vincents
# server and allows users to type commands to be sent 
# to the server. The program binds to local UDP port 
# 15001. The receive loop runs as a separate thread so 
# that it does not block user input.
#
# VINCENTS PROTOCOL COMMANDS:
#  name - used to "register" a user, server ties name to (IP,PORT)
#  tx   - used to add a transaction/message to ledger
#  getledger - used to request full ledger be sent
#  getclientlist - this hsould be the first command ever done 
#                  done by someone joining the network 
# EXAMPLES
#  packet_msg = "name|John"
#  packet_msg = "tx|Hello world!"
#  packet_msg = "tx|John sends 10 coin to Aesha."
#
#---------------------------------------------------------------

import socket     # for network comm functionality
import threading  # for two "threads" of execution
import time
KNOWN_PEER_ADDR = ('35.223.209.58',15001) # (IP,Port) 

# variables from server.py
clientdict = {} # clientsdict[addr] = str name
ledger = ['\n-----------------\nVincents Ledger\n']

def receiver():
  """ This function is an infinite loop for receiving
  and printing packets on udp socket s which must have
  been established. """
  global clientdict
  global ledger
  while True:
    msg, addr = s.recvfrom(2048)
    print('Incoming msg:  ' + msg.decode())

     # server code for incoming packets 
    tokens = msg.decode().split('|')
    if len(tokens) > 2:
      # invalid transaction
      #reply = 'INVALID TRANSACTION:' + msg.decode()
      print(reply)
      #s.sendto(reply.encode(),addr)
    else:
      cmd = tokens[0]
      if cmd == 'name':
        # add name to client dict
        name = tokens[1]
        clientdict[addr] = name
        reply = 'Welcome new user: ' + name
        print(reply)
        # In peer2peer we do not need to notify anyone else of a new user 
        # nor do we need to send the ledger
        #-------------------------------------
        # notify everyone of new user
        # to handle the explosion 
        # for addr_i in clientdict:
        #  s.sendto(reply.encode(), addr_i)
        # send new user the ledger
        # ledger_str = ''.join(ledger) + '\n------------------'
        # s.sendto(ledger_str.encode(), addr)
      elif cmd == 'tx':
        # add transaction to ledger
        tx = tokens[1]
        if addr in clientdict:
          name = clientdict[addr]
          newtx = name + ': ' + tx
          print('RX:', newtx)
          ledger.append(newtx + '\n')
          #  with peer2peer no longer broadcast the transaction 
          # for addr_i in clientdict:
          # s.sendto(newtx.encode(), addr_i)
        else:
          reply = 'UNREGISTERED addr, send NAME packet first'
          s.sendto(reply.encode(),addr)
      elif cmd == 'getledger':
        ledger_str = ''.join(ledger) + '\n------------------'
        s.sendto(ledger_str.encode(), addr)
        print('sent ledger to:', addr)
      elif cmd == 'getclientdict': #clientdict
        clientdict_str = 'rxclientdict|'+ str(clientdict)
        s.sendto(clientdict_str.encode(), addr)
        print('sent clientdict to:', addr)
      elif cmd == 'rxclientdict': #clientdict
        clientdict_str = tokens[1]
        clientdict = eval(clientdict_str)
        print('clientdict:', clientdict)
      else:
        reply = 'UNRECOGNIZED CMD:' + cmd
        print(reply)
        #s.sendto(reply.encode(),addr)
     #end server for incoming packets

  #end while true

# MAIN
with socket.socket(type=socket.SOCK_DGRAM) as s:
  s.bind(('',15001))
  
  rx_thread = threading.Thread(target=receiver, daemon=True)
  rx_thread.start()
  print('rx Thread started')
  #getclientlist from a known peer
  s.sendto(b'name|Tyler1', KNOWN_PEER_ADDR)
  s.sendto(b'getclientdict', KNOWN_PEER_ADDR)
  s.sendto(b'getledger', KNOWN_PEER_ADDR)
  print('initalization packets sent')

  while True:
    time.sleep(3) # wait 1 sec before allowing another cmd
    print('   VinCents client, enter cmd: [name/tx/getledger/exit]')
    user_input = input(': ')
    if user_input == 'exit':
      break
    if user_input == '':
      continue
    tokens = user_input.split('|')
    cmd = tokens[0]
    if cmd not in ['name','tx','getledger','getclientdict','showledger']:
      print('   unrecognized command:', user_input)
      continue
    elif cmd == 'getledger':
      s.sendto(b'getledger', KNOWN_PEER_ADDR)
      print('-->CMD SENT: getledger')
    elif len(tokens) != 2:
      print('   invalid syntax')
    elif cmd == 'name' or cmd == 'tx':
      ledger += tokens[1] + '\n'
      s.sendto(user_input.encode(), KNOWN_PEER_ADDR)
      print('-->CMD SENT: ', user_input)
    elif cmd == 'showlegder':
      print('ledger:', ledger)

print('VINCENTS CLIENT COMPLETE')