function u16_to_str(nbr)
  local byte0 = bit.band(bit.rshift(nbr, 0), 0xFF)
  local byte1 = bit.band(bit.rshift(nbr, 8), 0xFF)
  return string.char(byte0, byte1)
end

function u8_to_str(nbr)
  local byte0 = bit.band(nbr, 0xFF)
  return string.char(byte0)
end

HW_VER = 4
NBR_STRANDS = 1
if (HW_VER < 3) then
  NBR_STRANDS = 1
else
  NBR_STRANDS = 4
end
UDP_LISTEN_PORT = 10001
UDP_BROADCAST_PORT = 10000
UDP_BROADCAST_CONFIG_HW_VER = u8_to_str(HW_VER)
UDP_BROADCAST_CONFIG_PORT = u16_to_str(UDP_LISTEN_PORT)
UDP_BROADCAST_CONFIG_NBR_LEDS = u16_to_str(21)
UDP_BROADCAST_CONFIG_NBR_STRANDS = u8_to_str(NBR_STRANDS)
UDP_BROADCAST_CONFIG_NBR_BYTES_PER_LED = u8_to_str(4)

dofile('udp_broadcast.lua')
dofile('udp_listen.lua')

function on_connect()
  print("Connected to wifi as: " .. wifi.sta.getip())
  local ssid,password,bssid_set,bssid = wifi.sta.getconfig()
  print(
      "\nCurrent Station configuration:"
    .."\nSSID : "..ssid
    .."\nPassword  : "..password
    .."\nBSSID: "..bssid.."\n"
  )
  udp_listen_run()
  udp_broadcast_run()
end

udp_listen_init()
udp_broadcast_init()

enduser_setup.start(on_connect)
