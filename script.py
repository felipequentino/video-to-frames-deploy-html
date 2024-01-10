import cv2
import pygetwindow as gw
import numpy as np
from flask import Flask, Response, render_template

app = Flask(__name__)

def generate_frames():
    while True:
        try:
            window = gw.getWindowsWithTitle('video.mp4')[0]  # Substitua pelo título da sua janela
            left, top, right, bottom = window.left, window.top, window.right, window.bottom
            width, height = right - left, bottom - top
            hwnd = window._hWnd

            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            save_bit_map = win32ui.CreateBitmap()
            save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)

            save_dc.SelectObject(save_bit_map)
            result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0)

            bmpinfo = save_bit_map.GetInfo()
            bmpstr = save_bit_map.GetBitmapBits(True)
            im = np.frombuffer(bmpstr, dtype='uint8')
            im.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            im = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
            
            ret, buffer = cv2.imencode('.jpg', im)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except IndexError:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
