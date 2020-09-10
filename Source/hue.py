import argparse
import requests
import pickle
import ast
import qhue
import os
import traceback
import pathlib
import getpass
import shutil

#class used for storing info about a bridge/profile
class Profile:
    def __init__(self,name,lights,ip,username):
        self.name = name
        self.username = username
        self.ip = ip
        self.lights = lights

#create a folder for storing info about hue bridges
if not os.path.isdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI"):
    os.mkdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI")

profilesFileLocation = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\HueCLI\\profiles.hue"

#Get the current Ip to reference in commands and get other profiles/ bridges that the user can switch to

try:
    currentIp,profiles = pickle.load(open(profilesFileLocation,"rb"))
except:
    currentIp,profiles,= None,{}

#displays 2D arrays neatly in columns
def DisplayTable(table,columnCount = -1):
    #this assumes the table is correctly formatted. It will error if it is not
    if columnCount == -1:
        columnCount = len(table[0])
    #must calculate column sizes first so that the table nicely fits together
    try:
        maxColumnSizes = [0] * columnCount
        for row in table:
            for i in range(len(row)):
                col = str(row[i])
                #finds the largest size each column is
                if len(col) > maxColumnSizes[i]:
                    maxColumnSizes[i] = len(col)
        display = ""
        for row in table:
            for i in range(len(row)):
                item = str(row[i])
                #This will just keep the items in their respective columns
                whiteSpace = " " * (maxColumnSizes[i] - len(item)+2)#the plus 2 is just for additional padding to space out the columns
                display += item + whiteSpace
            display += "\n"
        #get rid of the final new line if its not wanted/needed
        display = display[0:-1]
        print(display)
    except IndexError:
        raise IndexError("Malformed table")

def main():
    global currentIp
    parser = argparse.ArgumentParser(description = "A little CLI program to control my lights more easily")

    #Command Options
    parser.add_argument("--setup",action = "store_true",help = "Automatically setup a hue bridge")
    parser.add_argument("--change",action = "store_true",help = "Used to change the brightness/state of a given light")
    parser.add_argument("--rename",action = "store_true",help = "Rename a light to make it more easily accessible")
    parser.add_argument("--list",action = "store_true",help = "List all available lights connected to a hue bridge")
    parser.add_argument("--switch",action = "store_true",help = "Switch between different profiles for different hue bridge IPs")
    parser.add_argument("--ips",action = "store_true",help = "List all bridge IPs on your network")

    #Parameters
    parser.add_argument("-name",type = str,default = "")
    parser.add_argument("-id",type = str,default = "")
    parser.add_argument("-ip",type = str,default = "")
    parser.add_argument("-bri",type = int,default = None)
    parser.add_argument("-on",action = "store_true")
    parser.add_argument("-off",action = "store_true")
    
    args = parser.parse_args()

    args.name = args.name.strip()
    args.id = args.id.strip()
    args.ip = args.ip.strip()    

    try:
        #setup a bridge profile so it can be referrenced in other commands
        if args.setup:
            #required arguments
            if args.name == "":
                print("-name is a required parameter of the --setup command")
                return

            print("Retrieving Hue Bridge ip:\n")
            #get a list of bridge ips on the users network
            response = requests.get("https://discovery.meethue.com/")
            response.raise_for_status()
            if args.ip:
                ip = args.ip
                #if the user explicitly chooses a bridge ip to connect to, it must be validated to make sure it exists on the network
                if not ip in [bridge["internalipaddress"] for bridge in ast.literal_eval(response.text)]: 
                    print("The provided ip could not be found on your network")
                    return
            else:
                try:
                    #if one wasn't explicitly specified, it should just choose to setup with the first one it finds (most people will only have one bridge anyway)
                    ip = ast.literal_eval(response.text)[0]["internalipaddress"] 
                except:
                    #if no bridge ips could be found
                    print("Couldn't find a hue bridge on your network :(")
                    return
            print("IP:",ip,"\n")
            print("Press the pair button on the hue bridge to complete the connection process\n")
            #pair the bridge with the program
            try:
                username = qhue.create_new_username(ip,None,60,120)
            except qhue.QhueException:
                print("2 minute time limit exceeded")
                raise KeyboardInterrupt()
            print("Username:",username,"\n")
            
            lights = {}
            
            bridge = qhue.Bridge(ip,username)

            #turn on all the lights so they can be dimmed one by one and the user can work out which light is which
            for light in bridge.lights():
                light = bridge.lights[light]
                try:
                    light.state(on = True)
                    light.state(bri = 255)
                except:pass
            
            input("Turn on all of your lights so they can be identified and then press enter\n")
            
            for light in bridge.lights():
                light = bridge.lights[light]
                if light()["state"]["on"]:
                    try:light.state(bri = 122)
                    except:light.state(on = False)
                    #names are assaigned to each light to make it easier for the user to change them later on
                    name = input("Enter a name for the light I just turned off:\n").strip()
                    while name in lights.values() or name == "":
                        name = input("That is not a valid name for the light:\n").strip()
                    lights[str(light()["uniqueid"])] = name
                else:
                    #tell the user that one of the lights couldn't be setup as it was turned off and can't be identified
                    print(f"Light {light()['uniqueid']} was off and thus cannot be identified. You can specify a name for it manually with hue -rn -id <Light Id> -name <Light Name>")

            #store the bridge profile
            profiles[str(ip)] = Profile(args.name,lights, ip,username)
            pickle.dump([ip,profiles],open(profilesFileLocation,"wb"))
            
            print(f"Profile sucessfully set for this IP and the current IP was switched to {ip}")
            return 

        #list all lights connected to a bridge
        elif args.list:
            profile = profiles[str(currentIp)]

            ip,username = profile.ip,profile.username
            
            bridge = qhue.Bridge(ip,username)

            print(f"\n{profile.name}\t-\t{profile.ip}\n")

            table = []
            #get the ids and names of all lights connected to the bridge
            for light in bridge.lights():
                light = bridge.lights[light]
                id = light()["uniqueid"]
                try:
                    name = profile.lights[id]
                except KeyError:
                    name = "N/A"#specify this if the light hasn't been assaigned a name on this profile. this could be because it was added to the bridge after the initial setup of the profile
                table.append(["\t"+name,id])
            #display table function used to make the infomation more presentable and easy to read
            DisplayTable(table)

        #list all bridge ips the user can connect to
        elif args.ips:
            response = requests.get("https://discovery.meethue.com/")
            response.raise_for_status()
            ips = []
            #get ips and names of bridges on the network
            for ip in [bridge["internalipaddress"] for bridge in ast.literal_eval(response.text)]:
                if ip in profiles:
                    ips.append(["\t"+profiles[ip].name,ip])#if the user has already setup this bridge, it will have a name
                else:
                    ips.append(["\tN/A",ip])#otherwise it will not and N/A will be put there instead
            print("Bridge IPs:\n")
            #display table function used to make the infomation more presentable and easy to read
            DisplayTable(ips)
            
        #renames a light on a bridge profile
        elif args.rename:
            profile = profiles[str(currentIp)]

            ip,username = profile.ip,profile.username
            
            bridge = qhue.Bridge(ip,username)

            #required parameters for this function 
            if args.name == "":
                print("-name is a required parameter of the --rename command")
                return
            if args.id == "":
                print("-id is a required parameter of the --rename command")
                return
            #make sure the specified light id is valid
            if args.id in [bridge.lights[light]()["uniqueid"] for light in bridge.lights()]:
                profile = profiles[str(currentIp)]
                try:
                    oldName = profile.lights[args.id]
                except KeyError:
                    oldName = "N/A"
                #make sure there won't be multiple lights with the same name on the bridge profile
                if args.name not in profile.lights.values():
                    profile.lights[args.id] = args.name
                else:
                    print(f"A light with the name {args.name} already exists in this profile")
                    return
                #save the changes to the profiles file
                pickle.dump([ip,profiles],open(profilesFileLocation,"wb"))
                
                print(f"Changed light {args.id} name from {oldName} to {args.name} ")
            else:
                print("Invalid id, use --list to get a list of lights and their ids")

        #command used for turning lights on and off and changing brightness 
        elif args.change:
            profile = profiles[str(currentIp)]

            ip,username = profile.ip,profile.username
            
            bridge = qhue.Bridge(ip,username)

            #get the light from a specified name
            if args.name != "":
                name = args.name
                light = list(filter(lambda l: profile.lights[l] == args.name,profile.lights))
                #find a light id with that name
                if light == []:#no matches
                    print(f"Couldn't find a light with the name {args.name} in this profile")
                    return
                else:
                    #once the id has been retrieved it can be extracted the same way as below
                    id = light[0]
                    light = list(filter(lambda l: bridge.lights()[l]["uniqueid"] == id,bridge.lights()))
                    if light != []:
                        #if a match was found with the specified id
                        light = bridge.lights[light[0]]
                    else:
                        #this will probably only happen if a bridge was removed from a network (was setup) and the program is still trying to access it
                        print(f"Couldn't find a light with the id, {id} associated with {args.name}")
                        return
            #get the light from a specified id
            elif args.id != "":
                id = args.id
                #try and get the name of the light if it is in the bridge profile, otherwise just leave it as "N/A"
                try:
                    name = profile.lights[id]
                except:
                    name = "N/A"
                light = list(filter(lambda l: bridge.lights()[l]["uniqueid"] == args.id,bridge.lights()))
                #find a light with
                if light != []:
                    light = bridge.lights[light[0]]
                else:
                    print(f"Couldn't find a light with the id, {args.id}")
                    return
            else:
                #if the name nor id were specified, throw an error to say that one of the two are required
                print("Either the parameter -name or -id are required for the --change command")
                return

            #if the brightness value was specified but it contained a number outside of the range of 0-255 an error should be thrown
            if args.bri != None:
                if args.bri < 0 or args.bri > 255:
                    print("-bri parameter only accepts values between 0-255")
                    return 

            #if the user wanted to change the brightness of their light
            if args.bri and args.bri != 0:
                if not light()["state"]["on"]:
                    #turn the light on if it was off beforehand
                    light.state(on = True)    
                light.state(bri = args.bri)
                print(f"Set {name}\t-\t{id} brightness to {args.bri}")
            #turn the light off if the -off keyword was used or the user set -bri to 0
            if args.off or args.bri == 0:
                light.state(on = False)
                print(f"Turned Off {name}\t-\t{id}")
            #just turn the light on
            if args.on:
                light.state(on = True)
                print(f"Turned On {name}\t-\t{id}")

            #they are three seperate if statements so that they can be used together and have been arranged in a hierarchical order

        #switch between different hue bridges
        elif args.switch:
            #if the user is switching to a specified bridge ip
            if args.ip != "":
                #the bridge ip must already have a profile associated with it
                if args.ip in profiles:
                    #change the current ip and save it to the profiles file
                    currentIp = args.ip
                    pickle.dump([currentIp,profiles],open(profilesFileLocation,"wb"))
                    print(f"Switched profile to {profiles[currentIp].name} - {currentIp}")
                else:
                    #if the ip hasn't got a profile for it, reccomend the user sets it up
                    print(f"Couldn't find a profile/bridge with the ip, {args.ip}. Use 'hue --setup -ip {args.ip} -name <profile name>' to get started")
            #if the user is switching to a given bridge name
            elif args.name != "":
                #search for a profile with the specified name
                profile = list(filter(lambda profile : profiles[profile].name == args.name,profiles))
                if profile == []:
                    print(f"Couldn't find a profile with the name, {args.name}")
                else:
                    #change the current ip and save it to the profiles file
                    currentIp = profiles[profile[0]].ip
                    pickle.dump([currentIp,profiles],open(profilesFileLocation,"wb"))
                    print(f"Switched profile to {args.name} - {currentIp}")
            else:
                print("Either -name or -ip is a required parameter of the --switch command")
    #handle exceptions
    except KeyboardInterrupt: #if the user presses ctrl+c
        print("Cancelled")
    except requests.exceptions.ConnectTimeout: #if the program fails to connect to the bridge
        print("Failed to connect to {ip}")
    except KeyError as e: #an error that will occur when some commands are used before the user has setup a bridge to connect to
        if not str(currentIp) in profiles:
            print("There is no Ip or profile set to retrieve from. Run 'hue --setup -name <profile name>' to get started")
            return
        else:
            print(traceback.format_exc())#if another key error occurs then this should show an error
             
    
if __name__ == "__main__":
    main()
