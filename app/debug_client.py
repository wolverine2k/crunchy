#!/usr/bin/env python
# encoding: utf-8
"""
debug_client.py

Created by Johannes Woolard on 2008-03-28.

The client for ../debug_server.py

Just has the one function, send_debug(debug_str) that sends the specified string to the server
"""

from System.Net.Sockets import Socket, ProtocolType, AddressFamily, SocketType, SocketAsyncEventArgs, SocketShutdown
from System.Net import DnsEndPoint
from System.Text import Encoding

from time import sleep

def send_debug(s):
    socket = Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp)
    async_args = SocketAsyncEventArgs()
    async_args.RemoteEndPoint = DnsEndPoint("localhost", 4511)
    async_args.SetBuffer(Encoding.UTF8.GetBytes(s), 0, len(Encoding.UTF8.GetBytes(s)))
    socket.ConnectAsync(async_args)
    #sleep(2)
    #if not socket.Connected:
    #    raise "Socket not connected"
    #socket.SendAsync(async_args)
    sleep(0.5)
    socket.Shutdown(SocketShutdown.Both)
    socket.Close()


if __name__ == '__main__':
    send_debug("hello world")

