from jsonImageSender import jsonImageSender

sender = jsonImageSender("localhost",5000)
sender.newTexRectangle(1, "Mona_Lisa.jpg", 100, 300, 200, 200)