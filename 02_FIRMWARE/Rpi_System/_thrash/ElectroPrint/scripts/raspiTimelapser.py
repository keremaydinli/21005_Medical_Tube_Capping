import argparse
import cv2
import os
import socket
import glob
import time

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--choose", help="Layer or minutes.")
parser.add_argument("-o", "--output", help="Your destination output file.")
parser.add_argument("-n", "--number", type=int, help="Number of layer or minutes.")
args = parser.parse_args()


WAIT_TIME = args.number
save_path = args.output + '/timelapse.mp4'

data = ""
frames_per_seconds = 10
cam = cv2.VideoCapture("http://localhost:8080/stream.mjpg")
timelapse_img_dir = 'images/timelapse/'


if not os.path.exists(timelapse_img_dir):
    os.mkdir(timelapse_img_dir)  # images location
	os.mkdir(timelapse_img_dir + args.output)  # video output location

def listening():
    global data
    s = socket.socket()
    port = 9999
    try:
        s.connect(('localhost', port))
    except:
        print('TimeLapse connection failed.')
    while True:
        data = s.recv(1024).decode()


def images_to_video(out, image_dir, clear_images=True):
    image_list = glob.glob(image_dir + "/*.jpg")
    sorted_images = sorted(image_list, key=os.path.getmtime)
    for file in sorted_images:
        print(file)
        image_frame = cv2.imread(file)
        out.write(image_frame)
        cv2.waitKey(0)
    if clear_images:
        '''
        Remove stored timelapse images
        '''
        for file in image_list:
            os.remove(file)


if __name__ == '__main__':

    i = 0
    listen = threading.Thread(target=listening)
    listen.start()
    if 'minute' in args.choose:
        tic = time.time()
        while True:
            ret, image = cam.read()
            if time.time() - tic > WAIT_TIME * 60 :
                i += 1
                filename = timelapse_img_dir + "/" + i + ".jpg"
                cv2.imwrite(filename, image)
                cv2.waitKey(1)
                tic = time.time()
            
    else:  # layer
        print('layer')
        while 'FINISH' not in data:
            if 'TAKE' in data:
                ret, image = cam.read()
                filename = timelapse_img_dir + "/" + i + ".jpg"
                i += 1
                cv2.imwrite(filename, image)
                cv2.waitKey(1)

                
    out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), frames_per_seconds, (1300,1920))
    images_to_video(out, timelapse_img_dir)  ## make video
    
    out.release()
    cv2.destroyAllWindows()

