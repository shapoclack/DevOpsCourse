import subprocess, time, base64

vbox = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

# Break config
subprocess.run(["ssh", "devops", "sudo sed -i 's/MaxAuthTries 3/MaxAuthTries 10/' /etc/ssh/sshd_config.d/99-hardening.conf"])

cmd = "clear; sudo /usr/local/bin/audit.sh"
b64 = base64.b64encode(cmd.encode()).decode()
remote_code = f"python3 -c 'import fcntl, termios, base64; cmd = base64.b64decode(\"{b64}\").decode() + \"\\n\"; fd = open(\"/dev/tty1\", \"w\"); [fcntl.ioctl(fd, termios.TIOCSTI, bytes([c])) for c in cmd.encode()]'"
subprocess.run(["ssh", "devops", f"sudo {remote_code}"])
time.sleep(2.5)

subprocess.run([vbox, "controlvm", "devops-vm", "screenshotpng", "images/09_audit_script_broken.png"])

# Revert config back to 3
subprocess.run(["ssh", "devops", "sudo sed -i 's/MaxAuthTries 10/MaxAuthTries 3/' /etc/ssh/sshd_config.d/99-hardening.conf"])
print("Broken audit captured and config restored!")
