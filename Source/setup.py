import os
import getpass
import shutil
import webbrowser
import time

print("Setting up...")
time.sleep(2)

print(f"Creating C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")
if not os.path.isdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI"):
    os.mkdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")

print(f"Transferring hue.exe to C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")
shutil.copyfile("hue.exe",f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI\\hue.exe" )

print(f"\nYou'll have to manually add the following directory to your PATH environment variable:\n\nC:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")

if "y" in input("Not sure how to set environment variables? (y/n)").lower():
    url = "https://www.addictivetips.com/windows-tips/set-path-environment-variables-in-windows-10/"
    try:
        webbrowser.open(url)
    except:
        print("\n"+url+"\n")
        
input(f"Press enter once you have added the following directory to your PATH environment variable and complete the setup process:\n\nC:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")
