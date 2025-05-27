# autodarts-detection-grabber

a little tool to collect data for missdetections

## Requirements
- Linux Autodarts installation with ssh access
- autodarts headles client
- Windows pc to execute the tool. 

## How To
- download the autodarts-detection-grabber.exe from Github Release
- create a shortcut to you Desktop or wherever you want. 
- right click on shortcut and press properties
- change the target to for example:  
` C:\LOCATION OF YOUR \autodarts-detection-grabber.exe --host AUTODARTS_PC_IP_WITHOUT_PORT --username SSHUSERNAME --password SSHPASSWORD `
- save
- execute the shortcut
- the Tool will creates files in the location of your autodarts-detection-grabber.exe

The tool grabs the picture from Vision/live and Vision/dart tab from boardmanager.
It creates an ssh acces to your autodarts pc and grabs the last 25 rows of autodarts.log.  
