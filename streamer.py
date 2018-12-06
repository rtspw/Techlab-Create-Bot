import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

PAGE="""\
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Techlab Create Robot Interface</title>
  <style>
    /* Fonts from Google Fonts - more at https://fonts.google.com */
    @import url('https://fonts.googleapis.com/css?family=Raleway:400,700');

    * {
      box-sizing: border-box;
      padding: 0;
      margin: 0;
    }

    body {
      font-family: 'Raleway', sans-serif;
      font-size: 18px;
      background: #eee;
      user-select: none;
    }

    h1 {
      font-weight: 400;
      letter-spacing: 2px;
      padding: 30px 0;
      text-align: center;
      color: #374243;
    }

    /* - - - Button Styles - - -*/
    .btn {
      background: none;
      border: 1px solid #a5a3a3;
      font-family: inherit;
      border-radius: 5px;
      outline: none;
      transition: background .2s, color .2s;
    }

    .btn:hover {
      background: #838383;
      color: white;
      cursor: pointer;
      transition: background .2s, color .2s;
    }

    .btn-streaminfo {
      padding: 7px 15px;
    }

    .btn-switch {
      padding: 10px 20px;
    }

    /* - - - General Modifiers - - - */
    .upside-down {
      transform: scaleY(-1);
      transition: transform .15s;
    }

    .hidden {
      display: none !important;
    }

    .shadow--dark {
      box-shadow: 0px 2px 15px 0px rgba(0,0,0,0.22);
    }

    .shadow {
      box-shadow: 0px 2px 15px 0px rgba(171, 183, 183, 0.9);
    }
    /* - - - Block Styles - - - */
    .header {
     background: white;
    }

    .main {
      margin: 45px 0;
      padding: 45px 0;
      display: flex;
      justify-content: center;
      background: white;
      z-index: -1;
    }

    .stream {
      padding: 10px;
      position: relative;
      background: #ffffff;
    }

    .stream__img {
      background-image: url('https://images.pexels.com/photos/34950/pexels-photo.jpg?cs=srgb&dl=abandoned-forest-hd-wallpaper-34950.jpg&fm=jpg');
      height: 480px;
      width: 640px;
      border-radius: 10px;
      transition: transform .15s;
    }

    .stream__info {
      border-radius: 2px;
      padding: 10px;
      margin-top: 10px;
      display: flex;
      justify-content: space-around;
      align-items: center;
    }
     
    .control {
      justify-content: space-between;
      flex-direction: column;
      padding: 0 20px;
      margin-left: 20px;
      display: flex;
    }

    .control__joystick {
      padding: 10px;
      margin: 0 30px;
      background: rgb(214, 214, 214);
      border-radius: 10px;
    }

    #joystick {
      background: white;
    }

    .control__info {
      display: flex;
      flex-direction: column;
      justify-content: center;
      margin: 0 20px;
      padding: 0 20px;
    }

    .control__info__field {
      padding: 10px;
      display: flex;
      justify-content: space-around;
      text-align: center;
      border-bottom: 1px solid grey;
    }

    .control__info__field:first-child {
      border-top: 1px solid grey;
    }

    .x-coord {
      flex: 1;
    }

    .y-coord {
      flex: 1;
    }

    .left-power {
      flex: 1;
    }

    .right-power {
      flex: 1;
    }

    .control__switch {
      margin: 0 20px 10px 20px;
      padding: 0 20px;
      display: flex;
      justify-content: space-around;
    }

    .control__switch__figure {
      height: 40px;
      width: 40px;
      border-radius: 50%;
      border: 10px solid rgba(0, 119, 134, 0.34);
      background: #eff;  
      transition: border 1s, border-left-color 1s, border-right-color 1s;
      animation: donut-spin 5.5s linear infinite;

    }

    .control__switch__figure--on {
      border: 10px solid rgb(255, 168, 3);
      border-left-color: #ffcba5;
      border-right-color: #ffcba5;
      transition: border 1s, border-left-color 1s, border-right-color 1s;
    }

    .control__tank {
      display: flex;
      justify-content: center;
    }

    #tank {
      box-sizing: padding-box;
      border: 5px solid rgb(214, 214, 214);
      border-radius: 4px;
      box-shadow: 0px 2px 15px 0px rgba(171, 183, 183, 0.9);
    }

    @keyframes donut-spin {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }

    @media (max-width: 1154px) {
      * {
        color: blue;
      }
      
      .main {
        flex-direction: column;
      }
      
      .stream {
        display: flex;
        flex-direction: column;
      }
      
      .stream__img {
        margin: auto;
        width: 80%;
        height: 50%;
      }
      
      .control {
        margin: 0;
      }
      
      .control > * {
        margin: 10px 0;
      }
      
      .control__joystick {
        margin: 25px auto;
      }
      
      .control__switch {
        margin: 25px auto;
      }
      
      .control__switch__figure {
        margin-left: 30px;
      }
    }
  </style>

  </head>
    <body>
    <header class="header shadow--dark">
      <h1>Techlab Create Robot Interface</h1>
    </header>

    <div class="main shadow--dark"> 
      <div class="stream shadow">
        <img class="stream__img" src="stream.mjpg"/>
        <div class="stream__info">
          <div>Latency : 
            <span class="stream__info__latency">100</span>
            ms
          </div>
          <div>Distance : 
            <span class="stream__info__distance">100</span>
            cm
          </div>
          <button class="btn btn-streaminfo" id="btn-flip">Flip</button>
          <button class="btn btn-streaminfo" id="btn-showcontrols">
          Hide Controls</button>
        </div>
      </div>

      <div class="control">
        <div class="control__joystick shadow">
          <canvas id="joystick" width="200" height="200"> </canvas>
        </div>
        <div class="control__info">
          <div class="control__info__field">
            <p class="x-coord">X : 0</p>
            <p class="y-coord">Y : 0</p>
          </div>
          <div class="control__info__field">
            <p class="left-power">L : 0</p>
            <p class="right-power">R : 0</p>
          </div>
        </div>
        <div class="control__switch">
          <button class="btn btn-switch">Toggle Light</button>
          <div class="control__switch__figure"></div>
        </div>
        <div class="control__tank">
          <canvas id="tank" height="75" width="200"></canvas>
        </div>
      </div>
      
    </div>
    
    <script>
      var canvas = document.getElementById('joystick');
      var ctx = canvas.getContext('2d');
      var xDisplay = document.querySelector('.x-coord');
      var yDisplay = document.querySelector('.y-coord');
      var lDisplay = document.querySelector('.left-power');
      var rDisplay = document.querySelector('.right-power');

      var mousePos;
      var JOYSTICK_CURSOR_SIZE = 20;
      var LINE_COLOR = 'rgba(220, 220, 220, 0.5)';
      var CURSOR_COLOR = 'rgba(200, 200, 200, 0.4)';

      var global_left;
      var global_right;

      // Gets relative position of mouse on canvas element
      function getMousePos(canvas, event) {
        var rect = canvas.getBoundingClientRect();
        var x = Math.floor(event.clientX - rect.left - 100);
        var y = Math.floor(event.clientY - rect.top - 100);
        return { x, y };
      }

      // Update mouse location when cursor is held down over canvas
      canvas.addEventListener('mousedown', mouseDownEvent);
      canvas.addEventListener('touchstart', mouseDownEvent);

      function mouseDownEvent(event) {
        mousePos = getMousePos(canvas, event);
        setCoordDisplay(mousePos.x, mousePos.y * -1);

        var deadzone = getDeadZone(mousePos.x, mousePos.y);
        var tank = convertToTank(deadzone.x, deadzone.y * -1);
        setTankDisplay(tank.l, tank.r);
        global_left = tank.l;
        global_right = tank.r;

        dSendPost(tank.l, tank.r);

        clearCanvas();

        draw();
        ctx.beginPath();
        ctx.fillStyle = CURSOR_COLOR;
        ctx.arc(mousePos.x + 100, mousePos.y + 100, JOYSTICK_CURSOR_SIZE, 0, Math.PI * 2, false);
        ctx.fill();

        canvas.onmousemove = mouseMoveEvent;
        canvas.addEventListener('touchmove', mouseMoveEvent);
      }

      function mouseMoveEvent(event) {
        mousePos = getMousePos(canvas, event);
        setCoordDisplay(mousePos.x, mousePos.y * -1);

        var deadzone = getDeadZone(mousePos.x, mousePos.y);
        var tank = convertToTank(deadzone.x, deadzone.y * -1);
        setTankDisplay(tank.l, tank.r);
        global_left = tank.l;
        global_right = tank.r;

        dSendPost(tank.l, tank.r);

        clearCanvas();

        draw();

        drawCursor(mousePos.x + 100, mousePos.y + 100);
      }

      // Clears events when the mouse is released over joystick
      // and resets position to center
      canvas.addEventListener('mouseup', mouseUpEvent);
      canvas.addEventListener('touchend', mouseUpEvent);

      function mouseUpEvent(event) {
        canvas.onmousemove = null;
        canvas.ontouchend = null;
        mousePos = {x: 100, y: 100};
        setCoordDisplay(0, 0);
        setTankDisplay(0, 0);
        global_left = 0;
        global_right = 0;

        dSendPost(0, 0);

        clearCanvas();
        draw();
        drawCursor();
      }

      // Draws base canvas with the crosshair
      function draw() {
        ctx.strokeStyle = LINE_COLOR;
        
        // Vertical
        ctx.beginPath();
        ctx.moveTo(80, 0);
        ctx.lineTo(80, 200);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(120, 0);
        ctx.lineTo(120, 200);
        ctx.stroke();  
        
        // Horizontal
        ctx.beginPath();
        ctx.moveTo(0, 80);
        ctx.lineTo(200, 80);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(0, 120);
        ctx.lineTo(200, 120);
        ctx.stroke();
        
        // Forward Diagonal
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(80, 80);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(120, 120);
        ctx.lineTo(200, 200);
        ctx.stroke();
        
        // Backward Diagonal
        ctx.beginPath();
        ctx.moveTo(0, 200);
        ctx.lineTo(80, 120);
        ctx.stroke();
        

        ctx.beginPath();
        ctx.moveTo(120, 80);
        ctx.lineTo(200, 0);
        ctx.stroke();
      }

      // Draws joystick cursor at location
      function drawCursor(x = 100, y = 100) {
        ctx.beginPath();
        ctx.fillStyle = CURSOR_COLOR;
        ctx.arc(x, y, JOYSTICK_CURSOR_SIZE, 0, Math.PI * 2, false);
        ctx.fill();
        
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(100, 100);
        ctx.stroke();
      }

      // Resets canvas to base
      function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }

      // Most inelegent solution I've ever written
      function getDeadZone(x, y) {
        if (Math.abs(x) <= 20) {
          x = 20;
        }
        if (Math.abs(y) <= 20) {
          y = 20;
        }
        if (x >= 0) {
          x -= 20; 
        }
        else { 
          x += 20; 
        }
        if (y >= 0) {
          y -= 20;
        }
        else {
          y += 20;
        }
        return {x, y};
      }

      function setCoordDisplay(x, y) {
        xDisplay.textContent = 'X : ' + x;
        yDisplay.textContent = 'Y : ' + y;
      }

      function setTankDisplay(l, r) {
        lDisplay.textContent = 'L : ' + l;
        rDisplay.textContent = 'R : ' + r;
      }

      function convertToTank(x, y) {
        var v = (100 - Math.abs(x)) * (y / 100) + y;
        var w = (100 - Math.abs(y)) * (x / 10000) + x;
        var r = (v + w) / 2;
        var l = (v - w) / 2;
        l = Math.round(l / 100 * 300);
        r = Math.round(r / 100 * 300);
        return {l, r};
      }

      function sendPost(l, r) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/move', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www.form-urlencoded');
        xhr.onreadystatechange = function() {
          if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            console.log('Request complete.');
          }
        }
        xhr.send(l + ', ' + r);
      }

      var dSendPost = debounce(sendPost, 10);


      // Lodash implementation of debounce
      function debounce(func, wait, immediate) {
        var timeout;
        return function() {
          var context = this, args = arguments;
          var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
          };
          var callNow = immediate && !timeout;
          clearTimeout(timeout);
          timeout = setTimeout(later, wait);
          if (callNow) func.apply(context, args);
        };
      };

      function init() {
        draw();
        drawCursor();
        setCoordDisplay(0, 0);
        setTankDisplay(0, 0);
        
        global_left = 0;
        global_right = 0;
      }

      init();


    </script>
    
    <script>
      (function() {
      var canvas = document.getElementById('tank');
      var activationArea = document.getElementById('joystick');
      var ctx = canvas.getContext('2d');

      function draw() {
        
        clearCanvas();
        drawCenter();

        
        grd1 = ctx.createLinearGradient(0, 0, 200, 0);
        grd1.addColorStop(0.000, 'rgba(219, 28, 50, 1.000)');
        grd1.addColorStop(1.000, 'rgba(255, 112, 157, 1.000)');
        ctx.fillStyle = grd1;
        
        var temp_left = global_left/255 * 95 / -2;
        ctx.fillRect(0, 75/2, 100, temp_left);
        
        grd2 = ctx.createLinearGradient(0, 0, 200, 0);
        grd2.addColorStop(0.000, 'rgba(65, 216, 199, 1.000)');
        grd2.addColorStop(1.000, 'rgba(147, 255, 215, 1.000)');
        ctx.fillStyle = grd2;
        
        var temp_right = global_right/255 * 95 / -2;
        ctx.fillRect(100, 75/2, 200, temp_right);
        
        setTimeout(() => {
          requestAnimationFrame(draw);
        }, 10);
      }

      activationArea.addEventListener('mouseover', (event) => {
        continueLoop = true;
        draw();
      });
        
      function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
        
      function drawCenter() {
        ctx.strokeStyle = 'rgba(200, 200, 200, 1)';
        ctx.beginPath();
        ctx.moveTo(100, 0);
        ctx.lineTo(100, 75);
        ctx.stroke();
        
        ctx.strokeStyle = 'rgb(232, 232, 232)';
        ctx.beginPath();
        ctx.moveTo(0, 75/2);
        ctx.lineTo(200, 75/2);
        ctx.stroke();
      }

      drawCenter();
        
      })();
    </script>
    
    <script>
      var lightButton = document.querySelector('.btn-switch');
      var lightState = document.querySelector('.control__switch__figure');

      lightButton.addEventListener('click', () => {

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/toggleLight', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www.form-urlencoded');
        xhr.onreadystatechange = function() {
          if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            toggleSwitch();
          }
        }
        xhr.send();
      });


      function toggleSwitch() {
        lightState.classList.toggle('control__switch__figure--on');
      }

      var flipButton = document.getElementById('btn-flip');
      var streamBox = document.querySelector('.stream__img');

      flipButton.addEventListener('click', () => {
        streamBox.classList.toggle('upside-down');
      });


      var showControlButton = document.getElementById('btn-showcontrols');
      var controls = document.querySelector('.control');
      var hiddenState = false;

      showControlButton.addEventListener('click', () => {
        if (hiddenState) {
          showControlButton.textContent = 'Hide Controls';
        } else {
          showControlButton.textContent = 'Show Controls';
        }
        hiddenState = !hiddenState;

        controls.classList.toggle('hidden');
      });
    </script>
    
    <script>
      var latencyText = document.querySelector('.stream__info__latency');

      latencyText.textContent = 'NA';

      setInterval(() => {
        sendLatencyRequest();
      }, 1000);

      function sendLatencyRequest() {
        var now = new Date();
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/ping', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www.form-urlencoded');
        xhr.onreadystatechange = function() {
          if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            var end = new Date();
            var ms = end - now;
            latencyText.textContent = ms;
          }
        }
        xhr.send();
      }
    </script>
  </body>
</html>
"""

import smbus

bus = smbus.SMBus(1)
i2c_address = 0x08

def write_motor_speed(rDirection, lDirection, rSpeed, lSpeed):
    payload = [rDirection, lDirection, rSpeed, lSpeed]
    bus.write_i2c_block_data(i2c_address, 0x02, payload)

def toggle_lights():
    print('Toggling lights')
    bus.write_i2c_block_data(i2c_address, 0x03, [])

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()
    def do_POST(self):
        if self.path == '/move':
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8')
            post_params = post_body.split(',')
            lSpeed = int(post_params[0])
            rSpeed = int(post_params[1])
            lDir = 1 if lSpeed >= 0 else 0
            rDir = 1 if rSpeed >= 0 else 0
            lSpeed = abs(lSpeed)
            rSpeed = abs(rSpeed)
            write_motor_speed(rDir, lDir, rSpeed, lSpeed)
            self.send_response(200)
            self.end_headers()
        elif self.path == '/toggleLight':
            toggle_lights()
            self.send_response(200)
            self.end_headers()
        elif self.path == '/ping':
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        print('Starting server')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Ending server')
        pass
    finally:
        camera.stop_recording()
