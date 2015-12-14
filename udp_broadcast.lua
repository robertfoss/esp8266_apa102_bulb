function broadcast()
  sock = net.createConnection(net.UDP, 0)
  sock:connect(9998, '255.255.255.255')
  sock:send(wifi.sta.getip(), function()
    print('Broadcast local ip: ' .. wifi.sta.getip())
  end)
end

tmr.alarm(0, 2000, 1, broadcast)
