# autodarts-detection-log-collector

A small tool to collect data for misdetections.

## Requirements
- Linux Autodarts installation with SSH access
- Autodarts headless client
- Windows PC to run the tool

## How To
- Download the autodarts-detection-grabber.exe from the GitHub Release.
- Create a shortcut on your desktop or wherever you want.
- Right-click on the shortcut and select Properties.
- Change the target to, for example:  
  `C:\PATH_TO_YOUR\autodarts-detection-log-collector.exe --host AUTODARTS_PC_IP_WITHOUT_PORT --username SSHUSERNAME --password SSHPASSWORD`
- Save
- Run the shortcut.
- The tool will create files in the location of your autodarts-detection-log-collector.exe.

The tool grabs images from the Vision/live and Vision/dart tabs of the board manager.
It establishes an SSH connection to your Autodarts PC and retrieves the last 25 lines of autodarts.log.
