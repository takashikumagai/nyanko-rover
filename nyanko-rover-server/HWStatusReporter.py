#!/usr/bin/env python3

import time
import psutil
import vcgencmd

# Returns a string representing the system uptime
#
# Example of uptime command stdout:
#  17:17:04 up  2:30,  1 user,  load average: 0.67, 0.73, 1.22
def get_uptime():
    raw = subprocess.check_output('uptime').decode('utf8').replace(',','')
    words = raw.split()
    if 3 <= len(words):
        return words[2]
    else:
        return '?'

class HWStatusReporter:

    def get_hw_status():
        hw_status = {
            "uptime": get_uptime(),
            "temp": vcgencmd.measure_temp(),
            "cpu_usage": psutil.cpu_percent(),
            "camera": {"supported": vcgencmd.get_camera('supported'), "detected": vcgencmd.get_camera('detected')},
            "ip": '0.1.2.3',
            "public_ip": '4.5.6.7'
        }
        return hw_status

def run_test():
    pass

if __name__ == '__main__':
    run_test()
