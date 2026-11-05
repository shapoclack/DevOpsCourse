import subprocess, time, base64, os

vbox = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

# Make audit.sh executable and readable
subprocess.run(["ssh", "devops", "sudo cp /home/devops/audit.sh /usr/local/bin/audit.sh && sudo chmod 755 /usr/local/bin/audit.sh"])

cmd = "clear; sudo /usr/local/bin/audit.sh"
b64 = base64.b64encode(cmd.encode()).decode()
remote_code = f"python3 -c 'import fcntl, termios, base64; cmd = base64.b64decode(\"{b64}\").decode() + \"\\n\"; fd = open(\"/dev/tty1\", \"w\"); [fcntl.ioctl(fd, termios.TIOCSTI, bytes([c])) for c in cmd.encode()]'"
subprocess.run(["ssh", "devops", f"sudo {remote_code}"])
time.sleep(2.5)

subprocess.run([vbox, "controlvm", "devops-vm", "screenshotpng", "images/08_audit_script.png"])
print("Audit script screenshot updated!")
