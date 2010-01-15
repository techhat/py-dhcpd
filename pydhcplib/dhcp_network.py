# -*- encoding: utf-8 -*-
"""
pydhcplib module: dhcp_network

Purpose
=======
 Processes DHCP packets.
 
Legal
=====
 This file is part of pydhcplib, but has been heavily adapted for
 use in staticDHCPd.
 pydhcplib is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 
 (C) Mathieu Ignacio, 2008 <mignacio@april.org>
 (C) Neil Tallim, 2009
"""
import select
import socket
import threading

import dhcp_packet

class DhcpNetwork:
	def __init__(self, listen_address, listen_port, emit_port):
		self.listen_address = listen_address
		self.listen_port = listen_port
		self.emit_port = emit_port
		
	# Networking stuff
	def BindToAddress(self) :
		try:
			if self.listen_address:
				self.response_socket.bind((self.listen_address, 0))
			self.dhcp_socket.bind(('', self.listen_port))
		except socket.error,msg:
			raise Exception('pydhcplib.DhcpNetwork socket unable to bind to address: %(err)s' % {'err': str(msg),})
			
	def CreateSocket(self) :
		try:
			self.dhcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			if self.listen_address:
				self.response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			else:
				self.response_socket = self.dhcp_socket
		except socket.error, msg:
			raise Exception('pydhcplib.DhcpNetwork socket creation error: %(err)s' % {'err': str(msg),})
			
		try:
			self.response_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		except socket.error, msg:
			raise Exception('pydhcplib.DhcpNetwork socket unable to set SO_BROADCAST: %(err)s' % {'err': str(msg),})
			
		try: 
			self.dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error, msg :
			raise Exception('pydhcplib.DhcpNetwork socket unable to set SO_REUSEADDR: %(err)s' % {'err': str(msg),})
			
	def GetNextDhcpPacket(self, timeout=60):
		"""
		Blocks for up to C{timeout} seconds while waiting for a packet to
		arrive; if one does, a thread is spawned to process it.
		
		@type timeout: int
		@param timeout: The number of seconds to wait before returning.
		
		@rtype: L{dhcp_packet.DhcpPacket}|None
		@return: The received packet, or None if nothing was received.
		"""
		data = None
		while not data:
			(data_input, data_output, data_except) = select.select([self.dhcp_socket], [], [], timeout)
			if data_input:
				(data, source_address) = self.dhcp_socket.recvfrom(4096)
			else:
				return None
				
			if data:
				packet = dhcp_packet.DhcpPacket()
				packet.source_address = source_address
				packet.DecodePacket(data)
				
				if packet.IsDhcpRequestPacket():
					threading.Thread(target=self.HandleDhcpRequest, args=(packet, source_address)).start()
				elif packet.IsDhcpDiscoverPacket():
					threading.Thread(target=self.HandleDhcpDiscover, args=(packet, source_address)).start()
				elif packet.IsDhcpInformPacket():
					threading.Thread(target=self.HandleDhcpInform, args=(packet, source_address)).start()
				elif packet.IsDhcpDeclinePacket():
					self.HandleDhcpDecline(packet, source_address)
				elif packet.IsDhcpReleasePacket():
					self.HandleDhcpRelease(packet, source_address)
				return packet
			return None
			
	def SendDhcpPacketTo(self, packet, ip, port):
		return self.response_socket.sendto(packet.EncodePacket(), (ip, port))
		
	# Server side Handle methods
	def HandleDhcpDiscover(self, packet, source_address):
		pass
		
	def HandleDhcpRequest(self, packet, source_address):
		pass
		
	def HandleDhcpInform(self, packet, source_address):
		pass
		
	def HandleDhcpDecline(self, packet, source_address):
		pass
		
	def HandleDhcpRelease(self, packet, source_address):
		pass
		
