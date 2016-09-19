#include <stdint.h>

#include <ESP8266WiFi.h>
#include <HardwareSerial.h>
#include <WiFiUdp.h>
#include <Ticker.h>
#include "config.h"
#include "main.h"

#include "broadcaster.h"


static IPAddress broadcastIP(255, 255, 255, 255);
static WiFiUDP udp;
static Ticker ticker;
static uint8_t buffer[15];


static void broadcast()
{
    udp.beginPacket(broadcastIP, CONF_BROADCAST_PORT);
    udp.write(buffer, sizeof(buffer));
    udp.endPacket();
    Serial.println("Broadcasting: " + broadcastIP.toString() + ":" + CONF_BROADCAST_PORT);
}

void broadcaster_run()
{
    Serial.println("Broadcaster run");

    uint8_t hw_ver = CONF_HW_VER;
    memcpy(&buffer[0], &hw_ver, 1);
    uint16_t fw_ver = CONF_FW_VER;
    memcpy(&buffer[1], &fw_ver, 2);
    uint16_t listen_port = CONF_LISTEN_PORT;
    memcpy(&buffer[3], &listen_port, 2);
    uint16_t num_leds = CONF_NUM_LEDS;
    memcpy(&buffer[5], &num_leds, 2);
    uint8_t num_strands = CONF_NUM_STRANDS;
    memcpy(&buffer[7], &num_strands, 1);
    uint8_t bpp = CONF_BYTES_PER_PIXEL;
    memcpy(&buffer[8], &bpp, 1);
    WiFi.macAddress(&buffer[9]);

    ticker.attach(CONF_BROADCAST_PERIOD, broadcast);
    broadcast();
}
