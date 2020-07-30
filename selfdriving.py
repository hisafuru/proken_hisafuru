import findWhiteLineMidPoint
import whiteLineTrackingImage
import carController
import cv2,math,time,dlib

class selfDriving:
    def __init__(self,default_speed):
        #各クラスの初期化
        self.Tracking = whiteLineTrackingImage.TrackingLine()
        self.capture = cv2.VideoCapture(0)
        #self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'));
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        self.default_speed = default_speed
        carController.set_speed(default_speed,default_speed)

        #使用する画像(カメラ)の大きさを保存
        ref,testimg = self.capture.read()
        print(testimg.shape)
        self.height = int(testimg.shape[0]/2)
        self.width = int(testimg.shape[1]/2)
        self.mid_height = int(math.ceil(self.height/4))
        self.mid_width = int(math.ceil(self.width/4))

        fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        w = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.video = cv2.VideoWriter('video.mp4', fourcc, fps, (w, h))

        self.coe = 1.2 #左右に曲がる時の強さ
        self.tracking_point = 5 #白線を検知する下からの位置
        self.obs_point = 200 #障害物を検知する下からの位置

        SvmFile = "./detector.svm"
        self.detector = dlib.simple_object_detector(SvmFile)

        print("Initialization finished")

    def startSelfDriving(self):

        print("Self driving start")

        mode = 0

        #起動後, ctrl+c押下まで自動で走る
        try:
            while True:
                start = time.time()
                ret, img = self.capture.read()
                #self.video.write(img)

                if ret:
                    img = cv2.resize(img, (self.width, self.height))
                    img_tracked_double = self.Tracking.trackingWhiteLine(img)
                    img_tracked = img_tracked_double[0]#白線のみフィルタリング
                    img_obstacle = img_tracked_double[1]#障害物のみフィルタリング
                    img_redlight = img_tracked_double[2]#赤いライトのみフィルタリング
                    img_orangelight = img_tracked_double[3]#オレンジのライトのみフィルタリング

                    #障害物対応
                    if self.find_obstacle(img_obstacle):
                        if self.find_crosswalk(img_tracked):
                            carController.stop()
                            continue
                        elif self.obs_in_crosswalk(img_tracked,img_obstacle):
                            carController.stop()
                            continue


                    #信号機対応
                    t = self.tracking_traffic_light(img)
                    print(t)
                    if t < 10 and self.light_is_red_or_orange(img_redlight,img_orangelight,t):
                        carController.stop()
                        print("stop")
                        continue

                    self.set_speed(img_tracked)
                    carController.go_forward()

        except KeyboardInterrupt:
            self.capture.release()
            carController.stop
            carController.destroy()
            exit(0)

    #信号機が赤色、もしくは黄色であるかどうか
    def light_is_red_or_orange(self,img_redlight,img_orangelight,top):
        for i in range(self.width):
            if img_orangelight[top+5][i] > 100:
                return True

        for i in range(self.width):
            if img_redlight[top+5][i] > 100:
                return True

        return False

    #信号機検知 ある場合は画像内で上からの位置を返す 無い場合は適当な大きな値を返している
    def tracking_traffic_light(self,img):
        start = time.time()
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        dets = self.detector(rgb[0:160])
        end = time.time()
        if len(dets):
            d = dets[0]
            print(d,"detect",start-end)
            return d.top()
        return 10000

    #障害物が横断歩道の上にあるか検知
    def obs_in_crosswalk(self,img_tracked,img_obstacle):
        #白線検知
        lr = self.find_bottom(img_tracked)
        left_bottom = lr[0]
        right_bottom = lr[1]

        #障害物検知
        obs = False
        obs_left = -1
        obs_right = -1
        for i in range(self.width):
            if img_obstacle[self.height-self.obs_point-10][i] > 150 and obs == False:
                obs = True
                obs_left = i
            elif img_obstacle[self.height-self.obs_point-10][i] < 150 and obs == True:
                obs_right = i
                break

        if left_bottom < obs_right and right_bottom > obs_left:
            return True
        else:
            return False

    #横断歩道があるかどうか検知
    def find_crosswalk(self,img_tracked):
        white = False
        count = 0
        crosswalk = False
        for i in range(self.mid_width):
            if img_tracked[self.height-self.obs_point+2][i] > 150 and white == False:
                white = True
                count+=1
            else:
                white = False
            if count > 5:
                crosswalk = True
                break

        return crosswalk

    #障害物検知があるかどうか検知
    def find_obstacle(self,img_obstacle):
        find = False
        for i in range(self.width):
            if img_obstacle[self.height-self.obs_point][i] > 150:
                find = True
                break

        return find

    #画像下部で白線がどこにあるかを返す
    def find_bottom(self,img_tracked):
        #画面一番下側のトラッキング
        count=0
        left_bottom = 0
        right_bottom = 0
        #画面下側、左のライン位置の確認
        for i in range(self.mid_width):
            if img_tracked[self.height-self.tracking_point][i] > 50:
                left_bottom = i
                break

        count=0
        #画面下側、右のライン位置の確認
        for i in range(self.width-1,self.mid_width,-1):
            if img_tracked[self.height-self.tracking_point][i] > 50:
                right_bottom = i
                break

        return [left_bottom,right_bottom]

    #速度セット
    def set_speed(self,img_tracked):
        rl = self.find_bottom(img_tracked)
        left_bottom = rl[0]
        right_bottom = self.width-1-rl[1]

        if left_bottom > right_bottom:
            carController.set_speed(int(self.default_speed*(1-left_bottom*self.coe/self.width)),self.default_speed)
            print("Turn right")
        else:
            carController.set_speed(self.default_speed,int(self.default_speed*(1-right_bottom*self.coe/self.width)))
            print("Turn left")

if __name__ == "__main__":
    #速度を引数として与えて初期化
    driving = selfDriving(1700)
    driving.startSelfDriving()
