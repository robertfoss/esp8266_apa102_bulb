local UDP_BROADCAST_CONFIG = UDP_BROADCAST_CONFIG_HW_VER ..
                       UDP_BROADCAST_CONFIG_PORT ..
                       UDP_BROADCAST_CONFIG_NBR_LEDS ..
                       UDP_BROADCAST_CONFIG_NBR_STRANDS ..
                       UDP_BROADCAST_CONFIG_NBR_BYTES_PER_LED


function broadcast()
  sock = net.createUDPSocket()
  sock:send(UDP_BROADCAST_PORT,
            '255.255.255.255',
            UDP_BROADCAST_CONFIG)
  sock:close()
  print('Broadcast 255.255.255.255:' .. UDP_BROADCAST_PORT)
end

function udp_broadcast_init()
end

function udp_broadcast_run()
  tmr.alarm(0, 2000, 1, broadcast)
end
