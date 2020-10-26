from time import sleep
from machine import Pin
from utils.octopus_lib import w
from microWebSrv import MicroWebSrv
from components.led import Led
from components.rgb import Rgb
import json

np = Rgb(15) # NeoPixel(Pin(15), 1)
led = Led(2)
# pwm


print("-"*50)
print("ftp or WebServer - ESP32 control led/pwm/rgb")
print("-"*50)


def _httpHandlerLEDPost(httpClient, httpResponse):
    content = httpClient.ReadRequestContent()  # Read JSON color data
    jsc = json.loads(content)
    print("led: ", jsc)
    led.value(jsc)
    httpResponse.WriteResponseJSONOk()


def _httpHandlerPWMPost(httpClient, httpResponse):
    content = httpClient.ReadRequestContent()
    jsc = json.loads(content)
    print("pwm: ",jsc)
    # todo
    httpResponse.WriteResponseJSONOk()


def _httpHandlerRGBPost(httpClient, httpResponse):
    content = httpClient.ReadRequestContent()
    colors = json.loads(content)
    blue, green, red = [colors[k] for k in sorted(colors.keys())]
    np.color((red, green, blue))
    httpResponse.WriteResponseJSONOk()

btnum = 0

button = Pin(0, Pin.IN)
print("press button / CTRL+C or continue")
sleep(1)

for i in range(12):
    print("-",end="")
    if(not button.value()): btnum += 1 
    sleep(0.1)

w()
print("-"*50)

if (btnum==0):
    print("button0 -> start WebServer www/control/")
    routeHandlers = [ ( "/control/led", "POST",  _httpHandlerLEDPost ),( "/control/pwm", "POST",  _httpHandlerPWMPost ), ( "/control/rgb", "POST",  _httpHandlerRGBPost ) ]
    srv = MicroWebSrv(routeHandlers=routeHandlers, webPath='/www/control/')
    srv.Start(threaded=False)
else:
    print("button1 -> start FTP")
    import ftp

print("="*50)
