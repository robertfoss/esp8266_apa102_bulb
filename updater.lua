
function query_controller()
  if (CONTROLLER_IP == "") then
    return
  end

  http.get("http://CONTROLLER_IP/index", nil, function(code, data)
    if (code < 0) then
      print("HTTP request failed")
    else
      print(code, data)
    end
  end)
end


function calc_script_hash()
  local files = file.list();
  for k,v in pairs(files) do
    local hash = crypto.fhash("sha256", k)
    print("name:"..k..", hash:".. crypto.toHex(hash))
  end
end

calc_script_hash()

query_controller()


function updater_init()

end

function updater_start()
  srv=net.createServer(net.TCP)
  srv:listen(UDP_LISTEN_PORT,function(conn)
end