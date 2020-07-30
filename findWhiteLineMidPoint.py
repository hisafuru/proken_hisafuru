import whiteLineTrackingImage,math,cv2

class FindMidPoint:

    #白線の中点を計算
    #検出できない場合は-1を返す
    def calc(self,img,point):
        try:
            #現在の位置(白線を通ったらプラス1)
            current_point = 0
            #今白線内かどうか
            inWhiteLine = True
            #内側2つの点の位置を保存
            point_left = 0
            point_right = 0
            #画像の大きさを保存
            height = img.shape[0]
            width = img.shape[1]
            #中心配列だけ抜き取り
            img_mid = img[point]

            #内側の2点を検出
            for i in range(width):
                if img_mid[i] == 255 and inWhiteLine == False:
                    current_point += 1
                    inWhiteLine = True

                    #内側の2点なら記録
                    if current_point == 2:
                        point_left = i
                    elif current_point == 3:
                        point_right = i
                        break

                elif img_mid[i] == 0 and inWhiteLine == True:
                    inWhiteLine = False

            if point_left != 0 and point_right != 0:
                return (point_left+point_right)/2
            else:
                return -1
        except:
            return -1


import sys
if __name__ == "__main__":
    #第一にパスを指定すればその画像を使用
    #パスの指定が無ければカメラから読み込み

    args = sys.argv
    if len(args) == 2:
        print(args)
        path = args[1]
        img = cv2.imread(path)
    else:
        cap = cv2.VideoCapture(0)
        ref,img = cap.read()

    WT = whiteLineTrackingImage.trackingWhileLine()
    FM = FindMidPoint()

    img = WT.trackingWhiteLine(img)
    print(FM.calc(img))
