from m5stack import lcd
import utime
import network


def connect_wifi(wifi_configs, timeout_sec=10):
    'Connect to wifi described in wifi_configs'
    wlan = network.WLAN(network.STA_IF)  # create station interface
    wlan.active(True)                    # activate the interface
    for net in wlan.scan():
        ssid = net[0].decode()
        for candidate_config in wifi_configs:
            if ssid == str(candidate_config['SSID']):
                lcd.println('Connecting to ' + ssid)
                wlan.connect(ssid, candidate_config['PASSWD'])
                start_date = utime.time()
                while not wlan.isconnected():
                    now = utime.time()
                    lcd.print('.')
                    if now - start_date > timeout_sec:
                        break
                    utime.sleep(1)
                if wlan.isconnected():
                    lcd.println('Success to connect')
                    return True
                else:
                    lcd.println('Failed to connect')
                    return False
    return False
