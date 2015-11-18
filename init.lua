function on_connect()
  print("Connected to wifi as: " .. wifi.sta.getip())
  ssid,password,bssid_set,bssid = wifi.sta.getconfig()
  print(
      "\nCurrent Station configuration:\nSSID : "..ssid
    .."\nPassword  : "..password
    .."\nBSSID_set  : "..bssid_set
    .."\nBSSID: "..bssid.."\n"
  )
  dofile("udp_broadcast.lua")
  dofile("udp_listen.lua")
end

function on_error(err, str)
  print("ERROR #" .. err .. ": " .. str)
end

function on_debug(str)
  print("DEBUG: " .. str)
end

enduser_setup.start(on_connect, on_error, on_debug)
