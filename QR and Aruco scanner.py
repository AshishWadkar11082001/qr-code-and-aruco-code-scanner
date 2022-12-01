
import numpy as np
import cv2
from cv2 import aruco
import math
from pyzbar import pyzbar

def detect_Qr_details(image):
      
    Qr_codes_details = {}

    key = []
    value = []
    for qrcode in pyzbar.decode(image):
        codedata = qrcode.data.decode('utf-8')
        data = codedata
        
        points = (np.array([qrcode.polygon], np.int32))
        
        count = len(codedata)
        
        key.append(data)
 
        
    for i in range(count):
            decodedObjects = pyzbar.decode(image)
            decodedObjects_0 = decodedObjects[i]
            
            avg_x = int((int(decodedObjects_0.polygon[0][0]) + int(decodedObjects_0.polygon[1][0]) + int(decodedObjects_0.polygon[2][0]) + int(decodedObjects_0.polygon[3][0]))/4)
            
            avg_y = int((int(decodedObjects_0.polygon[0][1]) + int(decodedObjects_0.polygon[1][1]) + int(decodedObjects_0.polygon[2][1]) + int(decodedObjects_0.polygon[3][1]))/4)        
            value.append([avg_x,avg_y])
            
            Qr_codes_details = {}
    for j in range(count):
        Qr_codes_details[key[j]] = value[j]
    return Qr_codes_details    

def detect_ArUco_details(image):

    ArUco_details_dict = {} #should be sorted in ascending order of ids
    ArUco_corners = {}

    center_coordinate = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco,f'DICT_{5}X{5}_{250}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    bbox, ids,_ = aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)

    for t in range(len(ids)):
        ct = []
        for j in range(4):
            ct.append([int(bbox[t][0][j][0]), int(bbox[t][0][j][1])])
        ArUco_corners[ids[t][0]] = ct

    for ar in range(len(ids)):
        center_coordinate = []
        PI = 3.14159265359
        x = 0
        y = 0
        for t in range(4):
            x = x + bbox[ar][0][t][0]
            y = y + bbox[ar][0][t][1]
        center_coordinate = [int(x/4), int(y/4)]
        
        x_dist = center_coordinate[0] - bbox[ar][0][0][0]
        y_dist = center_coordinate[1] - bbox[ar][0][0][1]
        
        angle = ((math.atan2(x_dist , y_dist)) * 180 / PI) - 45
        if(int(angle)< -180 or int(angle) > 180):
            if(int(angle) < -180):
                angle = angle + 360
            else: angle = angle - 360

        ArUco_details_dict[int(ids[ar][0])] = [center_coordinate, int(angle)]

    return ArUco_details_dict, ArUco_corners 

# marking the Qr code with center and message

def mark_Qr_image(image, Qr_codes_details):
    for message, center in Qr_codes_details.items():
        encrypted_message = message
        x_center = int(center[0])
        y_center = int(center[1])
        
        cv2.circle(img, (x_center, y_center), 5, (0,0,255), -1)
        cv2.putText(image,str(encrypted_message),(x_center + 20, y_center+ 20),cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)

    return image

# marking the ArUco marker with the center, angle and corners

def mark_ArUco_image(image,ArUco_details_dict, ArUco_corners):

    for ids, details in ArUco_details_dict.items():
        center = details[0]
        cv2.circle(image, center, 5, (0,0,255), -1)

        corner = ArUco_corners[int(ids)]
        cv2.circle(image, (int(corner[0][0]), int(corner[0][1])), 5, (50, 50, 50), -1)
        cv2.circle(image, (int(corner[1][0]), int(corner[1][1])), 5, (0, 255, 0), -1)
        cv2.circle(image, (int(corner[2][0]), int(corner[2][1])), 5, (128, 0, 255), -1)
        cv2.circle(image, (int(corner[3][0]), int(corner[3][1])), 5, (255, 255, 255), -1)

        tl_tr_center_x = int((corner[0][0] + corner[1][0]) / 2)
        tl_tr_center_y = int((corner[0][1] + corner[1][1]) / 2) 

        cv2.line(image,center,(tl_tr_center_x, tl_tr_center_y),(255,0,0),5)
        display_offset = (2*int(math.sqrt((tl_tr_center_x - center[0])**2+(tl_tr_center_y - center[1])**2)))
        cv2.putText(image,str(ids),(center[0]+int(display_offset/2),center[1]),cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        angle = details[1]
        cv2.putText(image,str(angle),(center[0]-display_offset,center[1]),cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    return image

if __name__ == "__main__":

    # path directory of images in test_images folder
    img_dir_path = "test_cases/"

    # choose whether to test Qr or ArUco images
    choice = input('\nWhich images do you want to test ? => "q" or "a": ')

    if choice == 'q':

        marker = 'qr'

    else:

        marker = 'aruco'

    for file_num in range(0,2):
        img_file_path = img_dir_path +  marker + '_' + str(file_num) + '.png'

        # read image using opencv
        img = cv2.imread(img_file_path)

        print('\n============================================')
        print('\nFor '+ marker  +  str(file_num) + '.png')

        # testing for Qr images
        if choice == 'q':
            Qr_codes_details = detect_Qr_details(img)
            print("Detected details of Qr: " , Qr_codes_details)

            # displaying the marked image
            img = mark_Qr_image(img, Qr_codes_details)
            cv2.imshow("img",img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # testing for ArUco images
        else:    
            ArUco_details_dict, ArUco_corners = detect_ArUco_details(img)
            print("Detected details of ArUco: " , ArUco_details_dict)

            #displaying the marked image
            img = mark_ArUco_image(img, ArUco_details_dict, ArUco_corners)  
            cv2.imshow("img",img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()