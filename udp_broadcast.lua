local UDP_BROADCAST_CONFIG = UDP_BROADCAST_CONFIG_PORT ..
                       UDP_BROADCAST_CONFIG_NBR_LEDS ..
                       UDP_BROADCAST_CONFIG_NBR_BYTES_PER_LED


function broadcast()
  sock = net.createConnection(net.UDP, 0)
  sock:connect(UDP_BROADCAST_PORT, '255.255.255.255')
  sock:send(UDP_BROADCAST_CONFIG,
  function()
    print('Broadcast 255.255.255.255:' .. UDP_BROADCAST_PORT)
  end)
  sock:close()
end

tmr.alarm(0, 2000, 1, broadcast)
