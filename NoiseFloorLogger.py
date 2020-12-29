#!/usr/bin/env python3

import telnetlib
import time
import sys
import rrdtool
import os.path
import config as cfg
from airium import Airium

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
        session = telnetlib.Telnet(host, port, timeout)
        return session
    except Exception as e:
        print("Connecting to " + host + ":" + port + " failed:")
        print(e)

# Query the rig for signal strength (l STRENGTH)
# and write the output into the database
def query_rig(session):
    global db_file
    session.write(b"l STRENGTH\n")
    time.sleep(0.1)
    strength = session.read_very_eager().decode("utf-8")
    x = strength.replace("\n", "")
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
    rrdtool.graphv(*graphv_args)

# Generate an index.html file containing some graphs
def gen_html():
    global web_path
    a = Airium()

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

    html = str(a) # casting to string extracts the value

    with open(web_path + "/index.html", "w") as html_file:
        print(f"{html}", file=html_file)

# Main functionality
init_db()
s = connect_rig()
while s:
    query_rig(s)
    print_graph("1.png","Noise Floor","-1h")
    print_graph("2.png","Noise Floor","-4h")
    print_graph("3.png","Noise Floor","-12h")
    print_graph("4.png","Noise Floor","-24h")
    gen_html()
    time.sleep(5)
