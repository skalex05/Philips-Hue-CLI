# Philips-Hue-CLI

A CLI to make changing hue lights super simple from the console! 
I recommend you read through this documentation to know how to correclty setup and use this program. 

However, not all credit can go to me thanks to quentinsf's for his amazing philips hue wrapper.
__https://pypi.org/project/qhue/__

__Command Setup:__

  Run setup.exe to create the files needed to store neccessary infomation.
  Go to your environment variables and add the said directory to your PATH. The directory you need to add should look something like this:

  __C:\Users\<Your username>\AppData\Roaming\HueCLI__

  Adding it to the path will allow you to reference the second executable, hue.exe from anywhere in your terminal.

  To test that everything is setup, open up your terminal and type *'hue --ips'*. If everything is setup, you should see a list of bridge ips you can connect to. If you see an error that says 'hue' is not a recognised command, make sure you added the directory above correctly to the PATH environment variable.

  __Bridge Setup:__

  If you try running other commands such as *'hue --change'* or *'hue --list'* you may have seen the error: *'There is no Ip or profile set to retrieve from'*
  This means that you need to setup a hue bridge in order to control your lights and can be done with the command *'hue --setup -name <a name to give your bridge>'*
  
  This command will automatically setup the first bridge IP is found (this is fine for most people as you will probably only have one) however you can optionally define a specific IP to setup. To get a list of ips you can use the aforementioned command *'hue --ips'* to get a list of bridges you can connect to.

  Next, you will be asked to pair to your hue bridge. This is done by simply pressing the big button on the side of the bridge. This will timeout after 2 minutes and will cancel the setup. If at any other point setting up the bot you decide to cancel the setup, simply press ctrl+c to cancel.

  Finally, you'll be asked to turn on all of your hue lights. This is so that they can be turned off one by one and you can identify which is which. Once you've gone through all of your lights, you'll have successfully set up a bridge!

__Commands:__
  __Syntax for understanding the commands:__
  Below are the lists of commands. These will contain how to specify the command (starts with two hyphens) and a list of options for the command:
  
  <>    These will contain an option.
  
  \[]   These indicate that at least one of the options within it are required. If an option is not surrounded by brackets, assume that it is required.
  
  ""    These show you if a value needs to follow the command. It will in most cases with exceptions such as *'-on'* and *'-off'*  which don't require a value after it.
  
  __--change \[<-bri "brightness of light"> <-on> <-off>] \[<-name "name of light" > <-id "id of light">]__
  
  This is the main command which allows you to turn your lights on and off and control the brightness of them.
  *'-bri'* is used to specify the brightness you want your light to be. This is on a scale from 0-255. 0 being Off and 255 being turned on all the way. If a light is off when you set the brightness, this will turn the light on. If you don't want this to happen, you can additionally specify *'-off'* with your command and your light will stay off
  
  *'-on'* and *-off* are fairly self explanatory and will simply turn off a light. Turning off a light will also maintain the lights brightness when you turn it back on
  
  ___--switch \[<-ip "IP of another bridge"> <-name "Name of a bridge">]__
  
  A useful command if you need to connect to multiple bridges. Please note that you can only switch to bridges that have been setup. If you need to setup multiple bridges, use *'hue --setup -name <name of another bridge> -ip <specific ip to setup>'*
  
  __--rename <-id "id of the light to rename"> <-name "New name of the light">__
  
  Renaming can be used if a light was misidentified and given the wrong name. It can also be used to give a name to a light that was added to the bridge after it was setup. You'll notice this if a light's name is specified as *'N/A'*
  
  __--list__
  
  *'--List'* will display the current bridge's name and ip aswell as all the light ids and their respective names. A light's name may be displayed as *'N/A'* which means that it doesn't have a name associated with it. It can be renamed with *'hue --rename -id <id of the light you want to rename> -name <name you want to give this light>'*
  
  __--ips__
  
  *'--ips'* not to be confused with *'-ip'* is used to get all bridge ips on your network. If a bridge has been setup, the name of it will be displayed next to it. Otherwise, it will be left as *'N/A'* and can be setup with *'hue --setup -ip <bridge ip you want to setup> -name <name of the bridge you want to setup>'*
