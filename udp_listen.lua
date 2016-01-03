function listen(s, data)
  apa102.write(1, 3, data)
end


sock=net.createServer(net.UDP) 
sock:on("receive", listen)
sock:listen(UDP_LISTEN_PORT)
