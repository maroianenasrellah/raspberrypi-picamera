#!/usr/bin/python
# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import picamera
import picamera.array
import time

threshold = 10    # How Much pixel changes
sensitivity = 100 # How many pixels change

def takeMotionImage(width, height):
    with picamera.PiCamera() as camera:
        time.sleep(1)
        camera.resolution = (width, height)
        with picamera.array.PiRGBArray(camera) as stream:
            camera.exposure_mode = 'auto'
            camera.awb_mode = 'auto'
            camera.capture(stream, format='rgb')
            return stream.array

def scanMotion(width, height):
    motionFound = False
    data1 = takeMotionImage(width, height)
    while not motionFound:
        data2 = takeMotionImage(width, height)
        diffCount = 0;
        for w in range(0, width):
            for h in range(0, height):
                # get the diff of the pixel. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[h][w][1]) - int(data2[h][w][1]))
                if  diff > threshold:
                    diffCount += 1
            if diffCount > sensitivity:
                break;
        if diffCount > sensitivity:
            motionFound = True
        else:
            data2 = data1
    return motionFound

def motionDetection():
    print ("Scanning for Motion threshold=%i sensitivity=%i... " % (threshold, sensitivity))
    while True:
        if scanMotion(224, 160):
            print ("Motion detected")
            # initialize the video stream and allow the camera sensor to warm up
            print("[INFO] starting video stream...")
            # vs = VideoStream(src=0).start()
            vs = VideoStream(usePiCamera=True).start()
            time.sleep(2.0)
             
            # open the output CSV file for writing and initialize the set of
            # barcodes found thus far
            #csv = open(args["output"], "w")
            found = set()
            # loop over the frames from the video stream
            while True:
                    # grab the frame from the threaded video stream and resize it to
                    # have a maximum width of 400 pixels
                    frame = vs.read()
                    frame = imutils.resize(frame, width=400)
             
                    # find the barcodes in the frame and decode each of the barcodes
                    barcodes = pyzbar.decode(frame)
                    # loop over the detected barcodes
                    for barcode in barcodes:
                            # extract the bounding box location of the barcode and draw
                            # the bounding box surrounding the barcode on the image
                            (x, y, w, h) = barcode.rect
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
             
                            # the barcode data is a bytes object so if we want to draw it
                            # on our output image we need to convert it to a string first
                            barcodeData = barcode.data.decode("utf-8")
                            print("Scanned Barcode ",barcodeData)
                            barcodeType = barcode.type
             
                            # draw the barcode data and barcode type on the image
                            text = "{} ({})".format(barcodeData, barcodeType)
                            cv2.putText(frame, text, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
             
                            # if the barcode text is currently not in our CSV file, write
                            # the timestamp + barcode to disk and update the set
                            if barcodeData not in found:
                                    csv.write("{},{}\n".format(datetime.datetime.now(),
                                            barcodeData))
                                    csv.flush()
                                    found.add(barcodeData)
                                    # show the output frame
                    cv2.imshow("Barcode Scanner", frame)
                    key = cv2.waitKey(1) & 0xFF
        else:
            print ("Motion not detected")

if __name__ == '__main__':
    try:
        motionDetection()
    finally:
        print ("Exiting Program")