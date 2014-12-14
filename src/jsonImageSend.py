import base64, urllib, pycurl, json

with open("Mona_Lisa.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
    url = "http://localhost:5000/api/newTexRectangle"
    data = json.dumps({"windowNo" : 1, 
                       "x" : 100, 
                       "y" : 300, 
                       "width" : 200, 
                       "height" : 200, 
                       "textureData" : encoded_string, 
                       "extension" : "jpg"})
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, data)
    c.perform()