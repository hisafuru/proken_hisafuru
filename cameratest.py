import cv2
import whiteLineTrackingImage

#カメラの読み込み
camera = cv2.VideoCapture(0)
wt = whiteLineTrackingImage.TrackingLine()

while True:
    #フレーム取得
    ret, frame = camera.read()
    #フィルタ適用
    frame = wt.trackingWhiteLine(frame)
    #画面に表示
    cv2.imshow('camera', frame[0])

    # キー操作があればwhileループを抜ける
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 撮影用オブジェクトとウィンドウの解放
camera.release()
cv2.destroyAllWindows()
