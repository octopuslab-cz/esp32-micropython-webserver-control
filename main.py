from time import sleep
from machine import Pin
from utils.octopus_lib import w, getFree, getUid
from microWebSrv import MicroWebSrv
from components.led import Led
from components.rgb import Rgb
import json

neo = 30
np = Rgb(15,neo) # NeoPixel(Pin(15), 1)
led = Led(2)
# pwm


print("-"*50)
print("ftp or WebServer - ESP32 control led/pwm/rgb")
print("-"*50)


def _httpHandlerINFOPost(httpClient, httpResponse):
    infoDict = {}
    infoDict["deviceUID"] = getUid()
    infoDict["freeRAM"] = getFree()
    httpResponse.WriteResponseJSONOk(infoDict)


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
    for i in range(neo):
       np.color((red, green, blue),i)
    httpResponse.WriteResponseJSONOk()

btnum = 0

button = Pin(0, Pin.IN)
print("press button / CTRL+C or continue")
sleep(1)


for i in range(7):
    print("-",end="")
    if(not button.value()): btnum += 1 
    led.value(1)
    sleep(0.1)
    led.value(0)
    sleep(0.2)

w()

print("-"*50)  

if (btnum==0):
    print("button0 -> start WebServer www/control/")
    routeHandlers = [ ( "/info.json", "GET",  _httpHandlerINFOPost ),( "/control/led", "POST",  _httpHandlerLEDPost ),( "/control/pwm", "POST",  _httpHandlerPWMPost ), ( "/control/rgb", "POST",  _httpHandlerRGBPost ) ]
    srv = MicroWebSrv(routeHandlers=routeHandlers, webPath='/www/control/')
    srv.Start(threaded=False)
else:
    print("button1 -> start FTP")
    import ftp

print("="*50)
