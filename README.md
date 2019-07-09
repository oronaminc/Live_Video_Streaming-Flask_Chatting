


# Live_Video_Streaming
Live Video Streaming & Chatting (in vision programming class)

## Function

1. Starting Flask Web server (Showing Live Web Cam in Localhost)
2. Showing Starting Date & Time, IP Adress
3. Selecting Specific Area ( Rectangle Area )
4. Tracking Specific Area ( Rectangle Area )
5. Delecting Specific Area ( Chromakey Effect )
6. Chatting (boardcasting message + designating name) 
  => https://youtu.be/h4kIkPxhXPs

## Result Live Cam

<div>
  <img width="400" src="https://user-images.githubusercontent.com/37185394/60858090-eaf7d900-a247-11e9-8653-11c4c7295ae1.gif"/>
  <img width="400" src="https://user-images.githubusercontent.com/37185394/60858089-ea5f4280-a247-11e9-8c80-c2b295a97575.gif"/>
</div>
<div>
  <img width="800" src="https://user-images.githubusercontent.com/37185394/60860487-b8eb7480-a251-11e9-8304-d4d75a810495.gif"/>
</div>

## Using Manual

1. Starting Server and let program learn background 
(no object at cam, existing just background) => Just Waiting outside (It takes just 3 seconds)
2. Selecting Area which you want to remove at "cv2.imshow"
3. Object Removing (start) : "t or "d"
4. Object Removing (end) : "r" or "s"
5. Chrmoakey (start) : "k"
6. Chromakey (end) : "l"
 
## pip install

```python
pip3 install flask
pip3 install dlib
pip3 install cv2
pip3 install datetime
pip3 install pusher
``` 

## Dependencies
- Python 3+
- dlib
- OpenCV
- datetime
- flask
- pusher
