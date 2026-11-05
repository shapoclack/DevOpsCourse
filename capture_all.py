import subprocess, time, base64, os

cmds = [
    ("clear; ip -brief address", "01_ip_brief.png", 1.5),
    ("clear; stat -c '%a %n' /home/devops/.ssh /home/devops/.ssh/authorized_keys", "02_stat_devops_keys.png", 1.5),
    ("clear; sudo sshd -T | grep -Ei '^(port|permitrootlogin|passwordauthentication|maxauthtries|allowusers)'", "03_sshd_hardening.png", 1.5),
    ("clear; sudo ss -tlnp | grep sshd", "04_ss_listening_port.png", 1.5),
    ("clear; sudo ufw status verbose", "05_ufw_status_verbose.png", 1.5),
    ("clear; sudo grep 'UFW BLOCK' /var/log/ufw.log | tail -3", "06_ufw_block.png", 1.5),
    ("clear; hostname -f", "07_hostname_fqdn.png", 1.5),
    ("clear; /home/devops/audit.sh", "08_audit_script.png", 2.0),
]

vbox = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
os.makedirs("images", exist_ok=True)

for cmd, filename, wait_time in cmds:
    b64 = base64.b64encode(cmd.encode()).decode()
    remote_code = f"python3 -c 'import fcntl, termios, base64; cmd = base64.b64decode(\"{b64}\").decode() + \"\\n\"; fd = open(\"/dev/tty1\", \"w\"); [fcntl.ioctl(fd, termios.TIOCSTI, bytes([c])) for c in cmd.encode()]'"
    subprocess.run(["ssh", "devops", f"sudo {remote_code}"], capture_output=True)
    time.sleep(wait_time)
    out_path = os.path.join("images", filename)
    subprocess.run([vbox, "controlvm", "devops-vm", "screenshotpng", out_path], capture_output=True)
    print(f"Captured: {filename}")
print("ALL SCREENSHOTS CAPTURED SUCCESSFULLY!")
