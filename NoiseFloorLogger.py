#!/usr/bin/env python3
import telnetlib
import time
import sys
import rrdtool
import os.path
import config as cfg
from airium import Airium

# Read config parameters from config.py
# and store them into variables
host = cfg.host
port = cfg.port
timeout = cfg.timeout
db_file = cfg.db_file
web_path = cfg.web_path

# Create a new database if not already done before
def init_db():
    if not os.path.isfile(db_file):
        print ("creating DB file " + db_file)
        rrdtool.create(
            db_file,
            "--start", "now",
            "--step", "5",
            "RRA:AVERAGE:0.5:12:86400",
            "DS:dbm:GAUGE:15:-80:50")

# Connect to the rig via Telnet to rigctld
def connect_rig():
    try:
        print("Connecting to " + host + ":" + str(port) + "...")
        session = telnetlib.Telnet(host, port, timeout)
        print("Connection successful.")
        return session
    except Exception as e:
        print("Connection failed:")
        print(e)

# Query the rig for signal strength (l STRENGTH)
# and write the output into the database
def query_rig(session):
    global db_file
    # read signal strength from TRX
    session.write(b"l STRENGTH\n")
    # wait a moment 
    time.sleep(0.1)
    # read the answer
    strength = session.read_very_eager().decode("utf-8")
    x = strength.replace("\n", "")
    # write the value returned from rigctld to the DB
    if x:
        rrdtool.update(db_file, 'N:%s' % x)
    else:
        print("yep, that went wrong.")
        rrdtool.update(db_file, 'N:U')
    print(x)

# Generate a PNG file with a graph for a certain time range
def print_graph(filename,title,time_window):
    global db_file
    global web_path

    # Definition of the graph and the output file
    graphv_args = [
        web_path+"/"+filename,
        '--title', title,
        '--start', time_window,
        '--lower-limit=0',
        '--interlaced',
        '--imgformat', 'PNG',
        '--width=800',
        '--vertical-label', 'dbm',
        'DEF:noiselevel='+db_file+':dbm:AVERAGE',
        'LINE1:noiselevel#ff0000:"This is a red line"'
    ]
    # generate the output file
    rrdtool.graphv(*graphv_args)

# Generate an index.html file containing some graphs
def gen_html():
    global web_path
    a = Airium()

    # Generate the HTML code
    a('<!DOCTYPE html>')
    with a.html(lang="en"):
        with a.head():
            a.meta(charset="utf-8")
            a.title(_t="Noise Floor")
        with a.body():
            with a.h3():
                a("Last 1 hour")
            with a.div():
                a.img(src='1.png', alt='alt text')
            with a.h3():
                a("Last 4 hours")
            with a.div():
                a.img(src='2.png', alt='alt text')
            with a.h3():
                a("Last 12 hours")
            with a.div():
                a.img(src='3.png', alt='alt text')
            with a.h3():
                a("Last 24 hours")
            with a.div():
                a.img(src='4.png', alt='alt text')

    html = str(a)
    # write the html code to disk as index.html
    with open(web_path + "/index.html", "w") as html_file:
        print(f"{html}", file=html_file)

# Main functionality
init_db() # If no DB exists, create one
s = connect_rig() # Connect via Telnet to rigctld
while s:
    query_rig(s) # Query the signal strength and write it to the DB
    print_graph("1.png","Noise Floor","-1h")  # create a graph as PNG file
    print_graph("2.png","Noise Floor","-4h")  # ^
    print_graph("3.png","Noise Floor","-12h") # ^
    print_graph("4.png","Noise Floor","-24h") # ^
    gen_html() # create and write a html file
    time.sleep(5) # wait 5 seconds
