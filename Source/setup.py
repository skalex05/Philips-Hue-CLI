import os
import getpass
import shutil

if not os.path.isdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI"):
    os.mkdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")

shutil.copyfile("hue.exe",f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI\\hue.exe" )

print(f"You'll have to manually add the following directory to your PATH environment variable:\n\nC:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")
