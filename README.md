# Backdoor-Trojan
A Backdoor written in Python 3 that enables the attacker to execute commands on the remote machine being undetectable.

Step 1: Set Client Host Address to Attacker Machine (being you)

Step 2: Compile Python Code into an executable file (if using pyinstaller, use command: pyinstaller --onefile --noconsole client.py)

[!] Make Sure you set --noconsole so no DOS Prompt pops up on victim machine.
[!] Works better on Windows 10 (compatible with: Windows 10, Linux)

---[ All Commands ]---

_______________________________________
(Connection Commands)                  |
                                       |
[-tc] Terminate Connection             |
[-ac] Append Connection to Background  |
_______________________________________|
(User Interface Commands)              |
                                       |
[-sm] Send Message (VBS-Box)           |
[-ow] Open Webpage                     |
[-ss] Capture Screenshot               |
[-cw] Capture Webcam                   |
_______________________________________|
(System Commands)                      |
                                       |
[-si] View System Information          |
[-sp] Start Process on Remote Machine  |
[-pi] Remote Python Interpreter        |
[-rs] Remote CMD Shell                 |
[-su] Register to Startup              |
[-ru] Remove from Startup              |
[-sc] Shutdown Computer                |
[-rc] Restart Computer                 |
[-lc] Lock Computer                    |
_______________________________________|
(File Commands)                        |
                                       |
[-cd] Get Current Directory            |
[-vf] View Files                       |
[-sf] Send File                        |
[-rf] Receive File                     |
[-dl] Delete File/Directory            |
_______________________________________|

