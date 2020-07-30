import cv2
import whiteLineTrackingImage

#フィルタ適用前、フィルタ適用後の画像をtestimgに保存

capture = cv2.VideoCapture(0)
ret, frame = capture.read()
cv2.imwrite("./testimg/original.png",frame)
TW = whiteLineTrackingImage.TrackingLine()
img = TW.trackingWhiteLine(frame)
cv2.imwrite("./testimg/test_tracked.png",img)
