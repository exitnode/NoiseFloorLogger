# NoiseFloorLogger

The aim of this application is to log and monitor the signal strength of the noise floor at your QTH. This could be useful to locate sources of interference by correlating the collected data with other information, e.g. when sun collectors are active, your washing machine runs, your neighbours mowing their lawns etc.

The application connects itself via Telnet to a computer which is connected via serial/USB to the CAT interface of your transceiver and is running an instance of rigctld. This deamon must be configured to be network-wide reachable.

## Requirements

This tool needs the following libraries/packages:

* Airium
* rrdtool headers

You can install all required packages with the following commands (Ubuntu/Debian):

'''
# sudo apt install rrdtool librrd-dev
# sudo pip3 install rrdtool
# sudo pip3 install airium 
'''

You furthermore need to have your transceiver connected to a computer with rigctld (hamlib) running. This tool connects via Telnet to this computer and gets its data from there.

## Configuration

Adapt the file _config.py_ to your needs.
Don't forget to create the directory where you want to store the database as well as the html and png files.

## Execution

Start the tool without any parameters like this:

'''
# python3 NoiseFloorLogger.py
'''
