function clear()
  local clearOne = string.char(0, 0, 0, 0)
  local clearAll = string.rep(clearOne, 100)
  -- v3 HW
  --apa102.write(6, 7, clearAll)
  --apa102.write(3, 5, clearAll)
  --apa102.write(1, 2, clearAll)
  --apa102.write(4, 8, clearAll)

  -- v2 HW
  apa102.write(6, 5, clearAll)
end

function timeoutClear()
  tmr.alarm(1, 5*1000, tmr.ALARM_SINGLE, clear)
end

function listen(s, data)
  -- v3 HW
  --apa102.write(6, 7, data)
  --apa102.write(3, 5, data)
  --apa102.write(1, 2, data)
  --apa102.write(4, 8, data)

  -- v2 HW
  apa102.write(6, 5, data)
  timeoutClear()
end


sock=net.createServer(net.UDP) 
sock:on("receive", listen)
sock:listen(UDP_LISTEN_PORT)