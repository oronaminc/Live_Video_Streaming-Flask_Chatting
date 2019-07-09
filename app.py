import pusher
from flask import Flask, render_template, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy 
import dlib
from cv2 import *
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'

# setting Pusher to sending and receiving message
pusher_client = pusher.Pusher(
  app_id='804079',
  key='863815cdc4ae6cb2b486',
  secret='f6deb50ddc0827e14cad',
  cluster='ap3',
  ssl=True
)

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    message = db.Column(db.String(500))


# this variable will hold the coordinates of the mouse click events.
mousePoints = []

# this variable will hold the coordinates of the blow object position(rectangle position)
blow_x, blow_x1, blow_y, blow_y1 = 0,0,0,0

@app.route('/')
def index():

    messages = Message.query.all()

    cap = cv2.VideoCapture(0)

    # saving first frame image shot
    ret, frame = cap.read()
    cap.release()
    cv2.imwrite("static/bg.jpg", frame)

    time_str = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return render_template('index.html', time=time_str, messages=messages, visitor_ip=str(request.remote_addr))
    #return render_template('index.html', messages=messages)



def mouseEventHandler(event, x, y, flags, param):
    # references to the global mousePoints variable
    global mousePoints

    # if the left mouse button was clicked, record the starting coordinates.
    if event == cv2.EVENT_LBUTTONDOWN:
        mousePoints = [(x, y)]

    # when the left mouse button is released, record the ending coordinates.
    elif event == cv2.EVENT_LBUTTONUP:
        mousePoints.append((x, y))



def gen():
    cam = VideoCapture(0)

    # maniplate encoding levels 0 ~ 100
    encode_param = [int(IMWRITE_JPEG_QUALITY), 100]

    # using cv2.bgsegm.createBackgroundSubtractorMOG() remove background
    bgSubtractor = cv2.bgsegm.createBackgroundSubtractorMOG()

    # this variable will hold the coordinates of the mouse click events.
    global mousePoints

    # this variable will hold the coordinates of the blow object position(rectangle position)
    global blow_x, blow_x1, blow_y, blow_y1

    # create a named window in OpenCV and attach the mouse event handler to it.
    cv2.namedWindow("Webcam stream")
    cv2.setMouseCallback("Webcam stream", mouseEventHandler)

    # initialize the correlation tracker.
    tracker = dlib.correlation_tracker()

    # this is the variable indicating whether to track the object or not.
    tracked = False

    # this is the variable indicating whether to blow the object or not.
    blowed = False

    # this is the variable indicating blowing object
    ob = False

    # this is the variable changing chroma_key background imgae
    chroma_key = False

    # read background image to inpaint object which is tracking
    bg = cv2.imread("static/bg.jpg")
    
    while True:

        # capture the keyboard event in the OpenCV window.
        ch = 0xFF & cv2.waitKey(1)

        # start capturing the video stream.
        cam_opened, img = cam.read()

        img2 = img.copy()
        fgMask = bgSubtractor.apply(img2, learningRate=0)
        img_fg = cv2.bitwise_and(img2, img2, mask = fgMask)

        if cam_opened:
                # if we have two sets of coordinates from the mouse event, draw a rectangle.
                if len(mousePoints) == 2:
                        dlib_rect = dlib.rectangle(mousePoints[0][0], mousePoints[0][1], mousePoints[1][0], mousePoints[1][1])
                        #dlib_rect[mousePoints[0][0]:mousePoints[1][0], mousePoints[1][0]:mousePoints[1][1]] = bg[mousePoints[0][0]:mousePoints[1][0], mousePoints[1][0]:mousePoints[1][1]]


                # tracking in progress, update the correlation tracker and get the object position.
                if tracked == True:
                        tracker.update(img)
                        track_rect = tracker.get_position()
                        x  = int(track_rect.left())
                        y  = int(track_rect.top())
                        x1 = int(track_rect.right())
                        y1 = int(track_rect.bottom())
                        img[y:y1, x:x1] = bg[y:y1, x:x1]

                if blowed == True:
                        img[blow_y:blow_y1, blow_x:blow_x1] = ob
                        blow_y -=10; blow_y1-=10
                        if blow_y <= 10:
                                blowed = False

                if chroma_key == True:
                        #chroma_key=False
                        img = img_fg

                # show the current frame.
                cv2.imshow('Webcam stream', img)


        # press "k" to start chroma_key => remove background image
        if ch == ord("k"):
                chroma_key = True

        # press "l" to end chroma_key => returning background image
        if ch == ord("l"):
                chroma_key = False

        # press "r" to stop tracking and reset the points.
        if ch == ord("r"):
                mousePoints = []
                tracked = False

        # press "s" to blow away tracking the currently selected object/area.
        if ch == ord("s"):
                mousePoints = []
                tracked = False
                blow_x  = int(track_rect.left())
                blow_y  = int(track_rect.top())
                blow_x1 = int(track_rect.right())
                blow_y1 = int(track_rect.bottom())
                cv2.imwrite("static/object.jpg", img[blow_y:blow_y1, blow_x:blow_x1])
                ob = cv2.imread("static/object.jpg")
                blowed = True

        # press "d" to start tracking the currently selected object/area.
        if ch == ord("d"):
            if len(mousePoints) == 2:
                tracker.start_track(img, dlib_rect)
                tracked = True
                blow_x = mousePoints[0][0]
                blow_y = mousePoints[0][1]
                blow_x1 = mousePoints[1][0]
                blow_y1 = mousePoints[1][1]
                cv2.imwrite("static/object.jpg", img[blow_y:blow_y1, blow_x:blow_x1])
                ob = cv2.imread("static/object.jpg")
                blowed = True
                mousePoints = []

        # press "t" to start tracking the currently selected object/area.
        if ch == ord("t"):
            if len(mousePoints) == 2:
                tracker.start_track(img, dlib_rect)
                tracked = True
                mousePoints = []

        # press "q" to quit the program.
        if ch == ord('q'):
                mousePoints = []
                tracked = False

        ret, jpg_frame = imencode('.jpg', img, encode_param)
        frame = jpg_frame.tobytes() # jpg_frame is of type numpy.ndarray

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/message', methods=['POST'])
def message():

    try:

        username = request.form.get('username')
        message = request.form.get('message')

        new_message = Message(username=username, message=message)
        db.session.add(new_message)
        db.session.commit()

        pusher_client.trigger('chat-channel', 'new-message', {'username' : username, 'message': message})

        return jsonify({'result' : 'success'})
    
    except:

        return jsonify({'result' : 'failure'})

@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True)
