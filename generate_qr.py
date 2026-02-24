import qrcode

url = "https://crowdtrackingsystem.onrender.com"  # replace with your IP

img = qrcode.make(url)
img.save("entry_qr.png")

print("QR Code Generated Successfully!")