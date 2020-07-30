import numpy as np
import cv2

class TrackingLine():

    def hog(self,img):
        win_size = (64, 64)
        block_size = (16, 16)
        block_stride = (4, 4)
        cell_size = (4, 4)
        bins = 9
        hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, bins)
        img = hog.compute(img)
        return img

    def canny(self,img):
        img = cv2.GaussianBlur(img,(7,7),3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(img,100,200)

    def trackingWhiteLine(self,img):

        img = cv2.GaussianBlur(img,(5,5),3)
        img1 = self.trackingWhite(img)
        img2 = self.trackingObstacle(img)
        img3 = self.trackingRedLight(img)
        img4 = self.trackingOrangeLight(img)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
        img4 = cv2.cvtColor(img4, cv2.COLOR_BGR2GRAY)

        return [img1,img2,img3,img4]

    def trackingWhiteEdge(self,img):
        img = self.trackingWhite(img)

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray,(7,7),3)
        img_canny = cv2.Canny(img_blur,100,130)

        return img_canny

    def trackingRedLight(self, img):
        #HSVに変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #信号機カラーの範囲
        #[色相0~360,彩度0~255,明度0~255]
        lower_white = np.array([150,50,230])
        upper_white = np.array([360,150,255])

        # 障害物意外にマスク
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        res_white = cv2.bitwise_and(img,img, mask= mask_white)

        img = cv2.cvtColor(res_white, cv2.COLOR_HSV2RGB)
        return img

    def trackingOrangeLight(self,img):
        #HSVに変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #信号機カラーの範囲
        #[色相0~360,彩度0~255,明度0~255]
        lower_white = np.array([20,100,240])
        upper_white = np.array([40,130,255])

        # 障害物意外にマスク
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        res_white = cv2.bitwise_and(img,img, mask= mask_white)

        img = cv2.cvtColor(res_white, cv2.COLOR_HSV2RGB)
        return img

    #hsv形式前提
    def trackingObstacle(self, img):
        #HSVに変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #障害物カラーの範囲
        #[色相0~360,彩度0~255,明度0~255]
        lower_white = np.array([0,180,170])
        upper_white = np.array([360,230,230])

        # 障害物意外にマスク
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        res_white = cv2.bitwise_and(img,img, mask= mask_white)

        img = cv2.cvtColor(res_white, cv2.COLOR_HSV2RGB)
        return img

    #hsv形式前提
    def trackingWhite(self,img):

        #先に白線だけを検出
        #HSVに変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #白の範囲
        #[色相0~360,彩度0~255,明度0~255]
        lower_white = np.array([0,0,240])
        upper_white = np.array([360,140,255])

        # 白以外にマスク
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        res_white = cv2.bitwise_and(img,img, mask= mask_white)

        #img = cv2.cvtColor(res_white, cv2.COLOR_HSV2RGB)
        return res_white

    def drawRedLineToWhiteLine(self,img):
        img_tracked = trackingWhileLine(img)

        #画像, ρ(中心からの距離)の精度, θ(中心からの角度)の精度, 直線とみなすための投票値
        #linesは(ρ,θ)の配列
        lines = cv2.HoughLines(img_tracked,1,np.pi/180,70)
        for line in lines:
            rho,theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

        return img


if __name__ == "__main__":

    TW = TrackingLine()
    img = cv2.imread("./testimg/testWhiteLine.png")
    #img = cv2.imread("./testimg/testWhiteLine.jpg")
    img = TW.trackingWhiteLine(img)
    print(img)
    #img = TW.trackingWhite(img)
    cv2.imwrite("./testimg/test_tracked.jpg",img)
