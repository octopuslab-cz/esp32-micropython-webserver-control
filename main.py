from time import sleep
from machine import Pin
from utils.octopus_lib import w, getFree, getUid, randint
from microWebSrv import MicroWebSrv
from components.led import Led
from components.rgb import Rgb
import json

neo = 30 # number of Leds
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


cnt = 0
def _httpHandlerDATAPost(httpClient, httpResponse):
    global cnt
    val = 100
    num = 20
    cnt = cnt + 1
    dataDict = {}
    dataDict["cnt"] = cnt
    dataDict["num"] = 30
    dataDict["10"] = 200
    dataDict["20"] = 100
    dataDict["30"] = 0
    for i in range(num):
        val = val + randint(-10,10)
        dataDict[i*10 + 40] = val

    dataDict["val"] = val
    
    httpResponse.WriteResponseJSONOk(dataDict)


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


def _httpHandlerCOMMPost(httpClient, httpResponse):
    data  = httpClient.ReadRequestContentAsJSON()
    responseCode = 500
    content = None

    print(data)

    if len(data) < 1:
        responseCode = 400
        content = "Missing data"
        httpResponse.WriteResponse(code=400, headers = None, contentType = "text/plain", contentCharset = "UTF-8", content = content)
        return

    comm = data[0]
    commval= data[1] if len(data) > 1 else ""

    print(data[0], data[1])
    responseCode = 201

    httpResponse.WriteResponse( code=responseCode, headers = None, contentType = "text/plain", contentCharset = "UTF-8", content = content)


def _httpHandlerEXPANDPost(httpClient, httpResponse):
        """
        if expander is None:
            print("I2C expander is not initialized!")
            httpResponse.WriteResponseOk(None)
            return        
        """
        from components.i2c_expander import neg
        data = httpClient.ReadRequestContent()
        print("i2c_expander.data: " + str(data) + str(bin(int(data))))

        try:
            expander.write_8bit(neg(int(data)))
        except Exception as e:
            print("Exception: {0}".format(e))
            raise
        finally:
            httpResponse.WriteResponseOk(None)


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
    routeHandlers = [ ( "/control/expander", "POST",  _httpHandlerEXPANDPost ),( "/command", "POST",  _httpHandlerCOMMPost ),( "/info.json", "GET",  _httpHandlerINFOPost ),( "/data.json", "GET",  _httpHandlerDATAPost ),( "/control/led", "POST",  _httpHandlerLEDPost ),( "/control/pwm", "POST",  _httpHandlerPWMPost ), ( "/control/rgb", "POST",  _httpHandlerRGBPost ) ]
    srv = MicroWebSrv(routeHandlers=routeHandlers, webPath='/www/control/')
    srv.Start(threaded=False)
else:
    print("button1 -> start FTP")
    import ftp

print("="*50)
