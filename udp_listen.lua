function clear()
  local clearOne = string.char(0, 0, 0, 0)
  local clearAll = string.rep(clearOne, 100)
  apa102.write(6, 5, clearAll)
end

function timeoutClear()
  tmr.alarm(1, 5*1000, tmr.ALARM_SINGLE, clear)
end

function listen(s, data)
  apa102.write(6, 5, data)
  timeoutClear()
end


sock=net.createServer(net.UDP) 
sock:on("receive", listen)
sock:listen(UDP_LISTEN_PORT)