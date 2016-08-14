local last_anim_time = 0
local CLEAR_TIMEOUT = 10 * 1000 * 1000
local COLOR_OFF = string.char(0, 0, 0, 0)
local COLOR_GREEN = string.char(255, 0, 0, 255)
local server


function ledOutput(data)
  if HW_VER == 1 or HW_VER == 2 then
    -- HW_VER <= 2
    apa102.write(6, 5, data)
  else
    -- HW_VER >= 3  
    apa102.write(6, 7, data)
    apa102.write(3, 5, data)
    apa102.write(1, 2, data)
    apa102.write(4, 8, data)
  end
end

function fillColor(color)
  local colorAll = string.rep(color, 100)
  ledOutput(colorAll)
end

function timeoutClear()
  if (tmr.now() - last_anim_time) > CLEAR_TIMEOUT then
    fillColor(COLOR_OFF)
  end
end

function receive_handler(sock, data)
print("receive_handler")
  ledOutput(data)
  last_anim_time = tmr.now()
end

function udp_listen_init()
  fillColor(COLOR_OFF)
  tmr.alarm(1, 250, tmr.ALARM_AUTO, timeoutClear)
end

function udp_listen_run()
  server = net.createServer(net.UDP)
  server:on("receive", receive_handler)
  server:listen(UDP_LISTEN_PORT)
end
