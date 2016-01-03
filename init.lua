function u16_to_str(nbr)
  byte0 = bit.band(bit.rshift(nbr, 0), 0xFF)
  byte1 = bit.band(bit.rshift(nbr, 8), 0xFF)
  return string.char(byte0, byte1)
end

function u8_to_str(nbr)
  byte0 = bit.band(nbr, 0xFF)
  return string.char(byte0)
end

UDP_LISTEN_PORT = 10001
UDP_BROADCAST_PORT = 10000
UDP_BROADCAST_CONFIG_PORT = u16_to_str(UDP_BROADCAST_PORT)
UDP_BROADCAST_CONFIG_NBR_LEDS = u16_to_str(21)
UDP_BROADCAST_CONFIG_NBR_BYTES_PER_LED = u8_to_str(4)


function on_connect()
  print("Connected to wifi as: " .. wifi.sta.getip())
  ssid,password,bssid_set,bssid = wifi.sta.getconfig()
  print(
      "\nCurrent Station configuration:"
    .."\nSSID : "..ssid
    .."\nPassword  : "..password
    .."\nBSSID_set  : "..bssid_set
    .."\nBSSID: "..bssid.."\n"
  )
  dofile('udp_broadcast.lua')
  dofile('udp_listen.lua')
end

enduser_setup.start(on_connect)
