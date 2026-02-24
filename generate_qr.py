import qrcode

url = "http://192.168.1.7:8000"  # replace with your IP

img = qrcode.make(url)
img.save("entry_qr.png")

print("QR Code Generated Successfully!")