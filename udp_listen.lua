function listen(s, data)
  ws2812.writergb(4, data)
end


sock=net.createServer(net.UDP) 
sock:on("receive", listen)
sock:listen(9999)