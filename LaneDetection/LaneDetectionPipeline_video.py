import cv2
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
import math

# Loading image
cap = cv2.VideoCapture('solidWhiteRight.mp4')

def region_of_interest(img,vertices): # dio koji nam je bitan
	mask = np.zeros_like(img) # maska od nula, odnosno crne boje
	match_mask_color = (255,) * channels 
	cv2.fillPoly(mask, vertices, match_mask_color)
	masked_image = cv2.bitwise_and(img,mask)
	return masked_image

def draw_lines(img,lines, color=[255,0,0],thickness=3):
	line_img=np.zeros((img.shape[0],img.shape[1],img.shape[2]),dtype=np.uint8)
	img = np.copy(img)
	if lines is None:
		return
	for line in lines:
		for x1, y1, x2, y2 in line:
			cv2.line(line_img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
	img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)
	return img

def pipeline(image):
	min_y = image.shape[0] * (3 / 5) 
	max_y = image.shape[0]
	height,width,channels = img.shape
	left_bottom = [0,height]
	right_bottom = [width,height]
	apex = [width/2,height/2]
	vertices = np.array([[left_bottom, right_bottom, apex]], dtype=np.int32)
	gray_scale = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	cannyed_image = cv2.Canny(gray_scale,100,200)
	cropped_image = region_of_interest(
		cannyed_image,
		vertices,
	)
	lines = cv2.HoughLinesP(
		cropped_image,
		rho=6,
		theta=np.pi / 60,
		threshold=160,
		lines=np.array([]),
		minLineLength=40,
		maxLineGap=25)
	left_line_x = []
	left_line_y = []
	right_line_x = []
	right_line_y = []
	for line in lines:
		for x1,y1,x2,y2 in line:
			slope = (y2-y1)/(x2-x1)
			if math.fabs(slope) < 0.5 :
				continue
			if slope <= 0:
				left_line_x.extend([x1,x2])
				left_line_y.extend([y1,y2])
			else:
				right_line_x.extend([x1,x2])
				right_line_y.extend([y1,y2])

	poly_left = np.poly1d(np.polyfit(left_line_y,left_line_x,deg=1))
	left_x_start = int(poly_left(max_y))
	left_x_end = int(poly_left(min_y))
	poly_right = np.poly1d(np.polyfit(
				right_line_y,
				right_line_x,
				deg=1))
	right_x_start = int(poly_right(max_y))
	right_x_end = int(poly_right(min_y))
	line_image = draw_lines(
		img,
		[[
			[left_x_start, max_y, left_x_end, min_y],
			[right_x_start, max_y, right_x_end, min_y],
		]],
		thickness=5,
	)
	return line_image
while(cap.isOpened()):
	ret, img = cap.read()
	height,width,channels = img.shape
	left_bottom = [0,height]
	right_bottom = [width,height]
	apex = [width/2,height/2]
	vertices = np.array([[left_bottom, right_bottom, apex]], dtype=np.int32)
	final = pipeline(img)
	cv2.imshow('frame',final)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
#print(lines)
#cv2.imshow('img',final)
#plt.imshow(masked_image)
#plt.show()
cap.release()
cv2.destroyAllWindows()