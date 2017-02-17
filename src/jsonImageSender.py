import base64, pycurl, json

class jsonImageSender:
    def newTexRectangle(self,canvasNo,filename,x,y,width,height,coorSys):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            url = "http://" + self.HOST + ":" + self.PORT + "/api/newTexRectangle"
            data = json.dumps({"canvasNo" : canvasNo, 
                               "x" : x, 
                               "y" : y, 
                               "width" : width, 
                               "height" : height, 
                               "textureData" : encoded_string, 
                               "extension" : extension,
                               "coorSys" : coorSys})
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, data)
            c.perform()
            
    def newTexRectangleWithID(self,ID,canvasNo,filename,x,y,width,height,coorSys):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            url = "http://" + self.HOST + ":" + self.PORT + "/api/newTexRectangleWithID"
            data = json.dumps({"ID" : ID,
                               "canvasNo" : canvasNo, 
                               "x" : x, 
                               "y" : y, 
                               "width" : width, 
                               "height" : height, 
                               "textureData" : encoded_string, 
                               "extension" : extension,
                               "coorSys" : coorSys})
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, data)
            c.perform()
            
    def setTexRectangleTexture(self,elementNo,filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            url = "http://" + self.HOST + ":" + self.PORT + "/api/setTexRectangleTexture"
            data = json.dumps({"elementNo" : elementNo, 
                               "textureData" : encoded_string, 
                               "extension" : extension})
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, data)
            c.perform()
            
    def __init__(self,HOST,PORT):
        self.HOST = HOST
        self.PORT = str(PORT)