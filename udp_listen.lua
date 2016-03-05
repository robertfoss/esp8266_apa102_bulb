function clear()
  local clearOne = string.char(0, 0, 0, 0)
  local clearAll = string.rep(clearOne, 100)
  apa102.write(6, 7, clearAll)
  apa102.write(3, 5, clearAll)
  apa102.write(1, 2, clearAll)
  apa102.write(4, 8, clearAll)
end

function timeoutClear()
  tmr.alarm(1, 5*1000, tmr.ALARM_SINGLE, clear)
end

function listen(s, data)
  apa102.write(6, 7, data)
  apa102.write(3, 5, data)
  apa102.write(1, 2, data)
  apa102.write(4, 8, data)
  timeoutClear()
end


sock=net.createServer(net.UDP) 
sock:on("receive", listen)
sock:listen(UDP_LISTEN_PORT)

gpio.mode(0, gpio.OUTPUT)
gpio.mode(5, gpio.OUTPUT)
