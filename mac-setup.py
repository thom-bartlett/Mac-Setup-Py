#!/Library/ManagedFrameworks/Python/Python3.framework/Versions/Current/bin/python3

from asyncore import write
from datetime import datetime
import json
import os
import time
import subprocess
import os.path
import requests
import plistlib
import tempfile
from Foundation import NSLog
from license import license

## TODO

## Requirements
# requires Splashtop install script as part of package
# requires crowdstrike package cached

apps = {
    "steps": [
        {
            "Name": "Google Chrome",
            "Trigger": "googlechromepkg",
            "progresstext": "Google Chrome is a browser that combines a minimal design with sophisticated technology to make the Web faster.",
            "Icon": "12d3d198f40ab2ac237cff3b5cb05b09f7f26966d6dffba780e4d4e5325cc701",
            "Path": "/Applications/Google Chrome.app"
        },
        {
            "Name": "Slack",
            "Trigger": "slack",
            "progresstext": "Slack is a new way to communicate with your team. It's faster, better organized, and more secure than email.",
            "Icon": "395aed4c1bf684b6abd0e5587deb60aa6774dc2a525fed2d9df2b95293b72b2c",
            "Path": "/Applications/Slack.app"
        },
        {
            "Name": "Evernote",
            "Trigger": "evernote",
            "progresstext": "Evernote is a powerful tool that can help executives, entrepreneurs and creative people capture and arrange their ideas.",
            "Icon": "e562a5b3628966e8d9280b0ccce719f020d4954cfc6afb1379f0172b0c620c44",
            "Path": "/Applications/Evernote.app"
        },
        {
            "Name": "Google Drive",
            "Trigger": "googledrive",
            "progresstext": "Google Drive is a file storage and synchronization service developed by Google",
            "Icon": "06daf9a94b41e43bc9e9d3339018769f1862bf8b0646c2795996fa01d25db7ba",
            "Path": "/Applications/Google Drive.app"
        },
        {
            "Name": "Mozilla Firefox",
            "Trigger": "firefoxpkg",
            "progresstext": "Firefox is a free web browser backed by Mozilla, a non-profit dedicated to internet health and privacy.",
            "Icon": "d1754d8839b1a61332b413cb9d0ff00c4d2109aee792552a67cbed5703863186",
            "Path": "/Applications/Firefox.app"
        },
        {
            "Name": "Splashtop",
            "Trigger": "splashtop",
            "progresstext": "Splashtop delivers next-generation remote access and remote support software and services.",
            "Icon": "e16b822560486cd123bd1a0e3cc3614ae42f3a30c40cad07eaf4d2cd5aa51cc0",
            "Path": "/Applications/Splashtop Streamer.app"
        },
        {
            "Name": "Microsoft Word",
            "Trigger": "microsoftword",
            "progresstext": "The trusted Word app lets you create, edit, view, and share your files with others quickly and easily.",
            "Icon": "02d85f833abb84627237d2109ca240ca9ee4dc8d9db299996d45363e3034166d",
            "Path": "/Applications/Microsoft Word.app"
        },
        {
            "Name": "Microsoft Excel",
            "Trigger": "microsoftexcel",
            "progresstext": "Microsoft Excel is the industry leading spreadsheet software program, a powerful data visualization and analysis tool.",
            "Icon": "47b16c524f57020290de1a510a7abeb3aa992b15a583c2db74c4e28f3caf7e77",
            "Path": "/Applications/Microsoft Excel.app"
        },
        {
            "Name": "Microsoft PowerPoint",
            "Trigger": "microsoftpowerpoint",
            "progresstext": "Microsoft PowerPoint empowers you to create clean slideshow presentations and intricate pitch decks",
            "Icon": "66ce76d1d8590b2cca9ac65b097c98d7f1e3e06d9848335624892fcc6aece2d4",
            "Path": "/Applications/Microsoft PowerPoint.app"
        },
        {
            "Name": "Crowdstrike Falcon",
            "Trigger": "crowdstrike",
            "progresstext": "Leading Cloud-Delivered Endpoint Protection Platform.",
            "Icon": "db5cac16aa2af32c497c2b25257e7c0eef54a707061093d77fa3d26725c879e2",
            "Path": "/Applications/Falcon.app"
        }
    ]
}

def install_Tools(url, name, signature):
    new = requests.get(url, stream=True)
    with tempfile.TemporaryDirectory() as tmpdirname:
        with open(f"{tmpdirname}/{name}", 'wb') as f:
            f.write(new.content)
            # check signature
            command = ["/usr/sbin/spctl", "-a", "-vv", "-t", "install", f"{tmpdirname}/{name}"]
            result = subprocess.run(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # if valid install
            if (str(result).find(signature) != "-1"):
                print("Verified signature and will now install")
                try:
                    command = ["/usr/sbin/installer", "-pkg", f"{tmpdirname}/{name}", "-target", "/"]
                    install = subprocess.run(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"Install results: {install}")
                except Exception as e:
                    write_log(f"failed to install package with error: {e}")
            else:
                write_log("Signature validation failed - will not install")
                exit

def check_Tools():
    tools = {
        "list": [
            {
                "name": "Installomator",
                "url": "https://api.github.com/repos/Installomator/Installomator/releases/latest",
                "path": "/usr/local/Installomator/Installomator.sh",
                "signature": "JME5BW3F3R"
            },
            {
                "name": "SwiftDialog",
                "url": "https://api.github.com/repos/bartreardon/swiftDialog/releases/latest",
                "path": "/usr/local/bin/dialog",
                "signature": "PWA5E9TQ59"
            }]}
    for i in tools["list"]:
        response = requests.get(i["url"])
        url = (response.json()["assets"][0]["browser_download_url"])
        name = (response.json()["assets"][0]["name"])
        latest_Version = response.json()["tag_name"][1:]
        write_log(f"Latest version is: {latest_Version}")
        if os.path.exists(i["path"]):
            if i["name"] == "Installomator":
                raw_Version = run_cmd([i["path"], "version"])
                version = raw_Version[0].strip()
            elif i["name"] == "SwiftDialog":
                raw_Version = run_cmd([i["path"], "-v"])
                version = raw_Version[0].strip()[:6]
                write_log(f"current version is: {version}")
            if version != latest_Version:
                print("Not on latest version")
                install_Tools(url, name, i["signature"])
            else:
                print("On latest version")
        else:
            print("Not installed.")
            install_Tools(url, name, i["signature"])

def splashtop_Install(app):
    # download Install to temp directory
    write_log("Downloading Splashtop")
    url = "https://my.splashtop.com/csrs/mac"
    name = "streamer.dmg"
    new = requests.get(url, stream=True)
    f = open(name, "wb")
    f.write(new.content)
    write_log("check signature Splashtop")
    os.system(f"hdiutil attach {name} -nobrowse -readonly")
    command = ["/usr/sbin/spctl", "-a", "-vv", "/Volumes/SplashtopStreamer/Install Splashtop Streamer.app"]
    result = subprocess.run(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # if valid install
    if (str(result).find("CPQQ3AW49Y") != "-1"):
        write_log("Verified signature and will now install")
        try:
            command = ["/usr/local/Installomator/deploy_splashtop_streamer.sh", "-i", "streamer.dmg", "-d", "ZH2P522JLST3", "-w", "0", "-s", "0", "-v", "0"]
            install = subprocess.run(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            write_log(f"Install results: {install}")
            if os.path.exists("/Applications/Splashtop Streamer.app"):
                appCheck(app)
            else:
                appCheck(app)
        except Exception as e:
            write_log(f"failed with error: {e}")
            appCheck(app)
    else:
        write_log("Signature validation failed - will not install")
        appCheck(app)

def falcon_Install(app):
    # not validating signature because this is a static package - not downloaded from internet
    # check if config profiles in place
    command = ["sudo", "profiles", "show"]
    result = run_cmd(command)
    index = 0
    while "CrowdStrike" not in result[0]:
        write_log("No config profile detected")
        time.sleep(3)
        index += 3
        result = run_cmd(command)
        if index >= 1200:
            write_log("Install Timed out...")
            appCheck(app)
            return
    else:
        write_log("Installing Falcon")
        os.system("installer -verboseR -package /usr/local/Installomator/FalconSensorMacOS.pkg -target /")
        write_log("Licensing Falcon")
        os.system(f"/Applications/Falcon.app/Contents/Resources/falconctl license {license}")
        appCheck(app)

def dialog_Update(text):
    f = open("/var/tmp/dialog.log", "a")
    f.write(text)
    f.close()

def caffeinate():
    PID = run_cmd(["pgrep", "Dialog"])
    caf_cmd = ["caffeinate", "-dimsu", "-w", PID[0]]
    subprocess.Popen(caf_cmd)

def write_log(text):
    """logger for depnotify"""
    NSLog("[mac-setup] " + str(text))

def run_dialog():
    """Runs the SwiftDialog app and returns the exit code"""
    # build list of items for json
    listitems = []
    for app in apps["steps"]:
        listitems.append({"title" : app['Name'], "icon" : f"https://ics.services.jamfcloud.com/icon/hash_{app['Icon']}", "status" : "pending", "statustext" : "Pending"})

    initial_Dialog = {
        "title": "Installing Applications",
        "alignment": "center",
        "button1text": "Please Wait",
        "button2": 0,
        "button1disabled": 1,
        "message": "Please wait while the following apps are downloaded and installed.",
        "messagefont": "size=14",
        "moveable": 1,
        "listitem": listitems,
    }
    jsonString = json.dumps(initial_Dialog)
    progess_Total = str(len(apps["steps"]))
    result = subprocess.Popen(["/usr/local/bin/dialog", "--jsonstring", jsonString, "--progress", progess_Total])
    return result

def appCheck(app):
    if os.path.exists(f"{app['Path']}"):
        write_log("App Installation verified, continuining...")
        dialog_Update(f"listitem: {app['Name']}: success\n")
        dialog_Update("progress: increment\n")
        return True
    else:
        write_log("App install failed...")
        dialog_Update(f"listitem: title: {app['Name']}, status: fail, statustext: Failed\n")
        dialog_Update("progress: increment\n")
        return False
    
def run_cmd(cmd):
    """Run the cmd"""
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, err = run.communicate()
    if err:
        print(err)
    return output, err

def finalize():
    # final dialog appearance changes
    dialog_Update("icon: SF=checkmark.circle.fill,weight=bold,colour1=#00ff44,colour2=#075c1e\n")
    dialog_Update("progresstext: Computer configuration complete!\n")
    dialog_Update("icon: SF=checkmark.seal.fill,weight=bold,colour1=#00ff44,colour2=#075c1e\n")
    dialog_Update("progresstext: Complete!\n")
    dialog_Update("progress: complete\n")
    dialog_Update("button1text: Done\n")
    dialog_Update("button1: enable\n")
    # cleanup
    if os.path.exists("/var/tmp/dialog.log"):
        #os.remove(dialog_command_file)
        print("command file removed")

def main ():
    # check if swiftdialog is installed
    check_Tools()
    # make sure we are at desktop
    process = run_cmd(["pgrep", "-l", "Setup Assistant"])
    while process[0] != "":
        print(f"{datetime}: Setup Assistant Still Running")
        time.sleep(1)
        process = run_cmd(["pgrep", "-l", "Setup Assistant"])
    process = run_cmd(["pgrep", "-l", "Finder"])
    while process[0] == "":
        print(f"{datetime}: Finder process not found. Assuming device at login screen")
        time.sleep(1)
        process = run_cmd(["pgrep", "-l", "Finder"])

    # initial run with pause to initialize
    result = run_dialog()
    # caffeinate 
    time.sleep(.5)
    caffeinate()
    # set initial progress
    dialog_Update("progress: 0\n")

    # main install logic 
    for app in apps["steps"]:
        dialog_Update(f"icon: https://ics.services.jamfcloud.com/icon/hash_{app['Icon']}\n")
        dialog_Update(f"listitem: title: {app['Name']}, status: wait, statustext: Installing\n")
        dialog_Update(f"progresstext: {app['progresstext']}\n")
        if os.path.exists(app["Path"]):
            appCheck(app)
        elif app["Trigger"] == "none":
            appCheck(app)
        else:
            if app["Trigger"] == "crowdstrike":
                falcon_Install(app)
            elif app["Trigger"] == "splashtop":
                splashtop_Install(app)
            else:
                os.system(f"/usr/local/Installomator/Installomator.sh '{app['Trigger']}' NOTIFY=silent BLOCKING_PROCESS_ACTION=ignore")
                appCheck(app)
    finalize()
    # needs to stay running until Dialog is quit so we can get the exit code
    process = run_cmd(["pgrep", "Dialog"])
    while process[0]:
        time.sleep(5)
        process = run_cmd(["pgrep", "Dialog"])
    # this updates the result object to get the latest exit code
    result.communicate()
    exit_Code = (result.returncode)
    write_log(exit_Code)

main()
