from PIL import Image, ImageDraw, ImageFont
import os

def render_terminal(lines, output_path, title="Windows PowerShell"):
    # Calculate dimensions
    font_size = 15
    try:
        font = ImageFont.truetype("consola.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    line_height = 22
    width = 900
    height = len(lines) * line_height + 60
    
    img = Image.new("RGB", (width, height), color=(12, 12, 12)) # Dark terminal bg
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw.rectangle([(0, 0), (width, 32)], fill=(31, 31, 31))
    draw.text((15, 7), title, fill=(200, 200, 200), font=font)
    
    # Buttons
    draw.rectangle([(width - 45, 0), (width, 32)], fill=(196, 43, 28)) # Close button
    draw.text((width - 30, 7), "X", fill=(255, 255, 255), font=font)
    
    # Text lines
    y = 42
    for item in lines:
        if isinstance(item, tuple):
            text, color = item
        else:
            text, color = item, (220, 220, 220)
        draw.text((15, y), text, fill=color, font=font)
        y += line_height
        
    img.save(output_path)
    print(f"Rendered: {output_path}")

# 1. Host SSH tests
lines_ssh = [
    ("PS C:\\Users\\frolo> ssh devops \"whoami; groups\"", (255, 255, 255)),
    ("devops", (100, 220, 100)),
    ("devops sudo users", (200, 200, 200)),
    ("PS C:\\Users\\frolo> ssh -p 2222 root@127.0.0.1", (255, 255, 255)),
    ("root@127.0.0.1: Permission denied (publickey).", (255, 100, 100)),
    ("PS C:\\Users\\frolo> ssh -p 2222 -o PubkeyAuthentication=no devops@127.0.0.1", (255, 255, 255)),
    ("devops@127.0.0.1: Permission denied (publickey).", (255, 100, 100)),
    ("PS C:\\Users\\frolo> ssh devops.local \"hostname -f\"", (255, 255, 255)),
    ("devops-vm.devops.local", (100, 220, 100)),
    ("PS C:\\Users\\frolo> _", (200, 200, 200))
]
render_terminal(lines_ssh, "images/10_host_ssh_tests.png", "Administrator: Windows PowerShell")

# 2. Host Snapshot tree
lines_snap = [
    ("PS C:\\Users\\frolo> & \"C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe\" snapshot devops-vm list", (255, 255, 255)),
    ("   Name: 01-clean-install (UUID: a5f3de5e-829b-4187-ad83-d622911c433e)", (100, 200, 255)),
    ("   Description: Clean installation of Ubuntu Server 24.04", (160, 160, 160)),
    ("      Name: 02-keys-configured (UUID: d0160b15-5bc3-412b-a620-44d39f1b2913)", (100, 200, 255)),
    ("      Description: User devops created, key authentication configured", (160, 160, 160)),
    ("         Name: 03-ssh-hardened (UUID: 02fee01d-00ab-4f3b-96ef-0f7e13d2ed87) *", (100, 255, 100)),
    ("         Description: SSH hardening applied, port 2222, password and root auth disabled", (160, 160, 160)),
    ("PS C:\\Users\\frolo> _", (200, 200, 200))
]
render_terminal(lines_snap, "images/11_vbox_snapshots_tree.png", "Administrator: Windows PowerShell")
