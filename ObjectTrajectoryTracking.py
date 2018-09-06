# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 15:22:01 2017

@author: pranjali
"""


from collections import deque
import numpy as np
import cv2
import imutils
import argparse
import time
from colorama import Back, Fore

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()

ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
THRESHOLD_LOW = (29,86,6);
THRESHOLD_HIGH = (64, 255, 255);
# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""
cam = cv2.VideoCapture(0)
BUF=30
PMAX=0.1
PMIN=0.001
TH=0
row=0
x=0
y=0
MAXVALUE=320*240
matrix=np.zeros((BUF,3))
binsum=0
binsum_prev=0

fps = cam.get(cv2.CAP_PROP_FPS)
print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)

# Number of frames to capture
num_frames = 64;
     
     
print "Capturing {0} frames".format(num_frames)
 
# Start time
start = time.time()
     
# Grab a few frames
for i in xrange(0, num_frames) :
    ret, frame = cam.read()
   
     
# End time
end = time.time()
 
# Time elapsed
seconds = end - start
print "Time taken : {0} seconds".format(seconds)
 
# Calculate frames per secon
fps  = num_frames / seconds;
print "Estimated frames per second : {0}".format(fps);




while(True):
    grabbed, frame = cam.read()
    frame = imutils.resize(frame, width=320, height=240)
    # Blur image to remove noise
    frame_filter = cv2.GaussianBlur(frame, (3, 3), 0)

    # Convert image from BGR to HSV
    frame_filter = cv2.cvtColor(frame_filter, cv2.COLOR_BGR2HSV)

    # Set pixels to white if in color range, others to black (binary bitmap)
    frame_binary = cv2.inRange(frame_filter.copy(), THRESHOLD_LOW, THRESHOLD_HIGH)
    frame_binary = cv2.erode(frame_binary, None, iterations=2)
    # Dilate image to make white blobs larger
    frame_binary = cv2.dilate(frame_binary, None, iterations = 2)
    matrix[row,0]=np.count_nonzero(frame_binary)
    
    #Calculate the number of binary ones in the 
    #previous and current frame
    binsum_prev=0.2*binsum+0.8*binsum_prev
    binsum=np.sum(frame_binary)
    
    

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
    cnts = cv2.findContours(frame_binary, cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

	# only proceed if at least one contour was found
    if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(255, 0, 0), 2)
			cv2.circle(frame, center, 5, (255, 0, 0), -1)

	# update the points queue
    pts.appendleft(center)
     	# loop over the set of tracked points
    for i in np.arange(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
                 
		# check to see if enough points have been accumulated in
		# the buffer
		if counter >= 10 and i == 1 and pts[-10] is not None:
			# compute the difference between the x and y
			# coordinates and re-initialize the direction
			# text variables
			dX = pts[-10][0] - pts[i][0]
			dY = pts[-10][1] - pts[i][1]
			(dirX, dirY) = ("", "")
 
			# ensure there is significant movement in the
			# x-direction
			if np.abs(dX) > 20:
				dirX = "East" if np.sign(dX) == 1 else "West"
 
			# ensure there is significant movement in the
			# y-direction
			if np.abs(dY) > 20:
				dirY = "North" if np.sign(dY) == 1 else "South"
 
			# handle when both directions are non-empty
			if dirX != "" and dirY != "":
				direction = "{}-{}".format(dirY, dirX)

 
			# otherwise, only one direction is non-empty
			else:
				direction = dirX if dirX != "" else dirY
    		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (255, 0, 255), thickness)
 
	# show the movement deltas and the direction of movement on
	# the frame
    cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (240, 50, 100), 3)
    cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (240, 50, 100), 1)
  
  #Initialise the matrix with x and y coordinates
    matrix[row,1]=x
    matrix[row,2]=y
    #Calculating the average of the sum(1st column) of matrix
    average=int(matrix[:,0].mean())
    print(average,matrix[row,0])
    if (average>(PMIN*MAXVALUE) and (average<PMAX*MAXVALUE)) and binsum<(binsum_prev+TH):
        output= "Receeding"
        print (Back.RED+Fore.BLACK+output)
        cv2.putText(frame, output, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (240, 50, 100), 3)
    elif (average>(PMIN*MAXVALUE) and (average<PMAX*MAXVALUE)) and binsum>(binsum_prev+TH):
        output= "Approaching"
        print (Back.BLUE+Fore.BLACK+output)
        cv2.putText(frame, output, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (240, 50, 100), 3)
    elif (average<PMIN*MAXVALUE):
        output= "Far Away"
        print (Back.GREEN+Fore.BLACK+output)
        cv2.putText(frame, output, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (240, 50, 100), 3)
    elif (average>=PMAX*MAXVALUE):
       output= "IMMINENT COLLISION" 
       cv2.putText(frame, output, (70, 100), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (0, 0, 255), 3)
       print (Back.YELLOW+Fore.BLACK+output)
       
    else:
        output= "Unconclusive"
        print (Back.RESET+Fore.RESET+output)
        cv2.putText(frame, output, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (240, 50, 100), 3)
        
    if row<BUF-1:
        row+=1
    else:
        row=0
        
    #Open the frame on screen 
    cv2.imshow("Frame", frame)
     
                
    key = cv2.waitKey(1) & 0xFF
    #Increment the counter
    counter += 1
   

	# If letter 'q' pressed, exit the loop
    if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
cam.release()
cv2.destroyAllWindows()