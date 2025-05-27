# autodarts-detection-log-collector

A small tool to collect data for misdetections.

## Requirements
- Linux Autodarts installation with SSH access
- Autodarts headless client
- Windows PC to run the tool

## How To
- Download the autodarts-detection-log-collector.exe from the GitHub Release.
- Just start the autodarts-detection-log-collector.exe
- open the shown ip adress at any device in your network which you have closest to your dartboard. Mostly your smartphone. 
- enter you ip from pc where autodarts is running on
- enter SSH credentials to connect to this PC
- press collect if you want to collect. 
- The tool will create files in the location of your autodarts-detection-log-collector.exe and you can also download a zip directly over the webpage.

The tool grabs images from the Vision/live and Vision/dart tabs of the board manager.
It establishes an SSH connection to your Autodarts PC and retrieves the last 25 lines of autodarts.log.
