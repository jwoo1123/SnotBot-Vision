import numpy as np
import cv2

cap = cv2.VideoCapture(1)

ret, frame = cap.read()
roi_corners = []
roi_selected = False

def draw_circle(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_corners.append((x,y))

cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)

while(True):
    ret, frame = cap.read()

    if len(roi_corners) < 2:
        for i in roi_corners:
            cv2.circle(frame, (i[0], i[1]), 5, (0, 0, 255), -1)

    elif len(roi_corners) == 2:
        (x1, y1, x2, y2) = (roi_corners[0][0], roi_corners[0][1], roi_corners[1][0], roi_corners[1][1])
        track_window = (x1, y1, x2-x1, y2-y1)
        roi = frame[y1:y2, x1:x2]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 60., 30.)), np.array((180., 255., 255.)))
        roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0,180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        
        roi_selected = True
        roi_corners = []

    if roi_selected:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0,180], 1)

        ret, track_window = cv2.CamShift(dst, track_window, term_crit)

        pts = cv2.cv.BoxPoints(ret)
        pts = np.int0(pts)
        cv2.polylines(frame, [pts], True, (0, 255, 255))

    
    cv2.imshow('image', frame)

    if cv2.waitKey(60) & 0xFF == 27:
        break

cv2.destroyAllWindows()
cap.release()
