# About

A super simple backend that gets the data from the local MQTT server running on the same network and forwards the data in JSON format over HTTP. 

This server is open to the internet at https://plants.hannes.pro, but the MQTT server is NOT. This make sure that the plant data can be accessed anywhere without exposing the whole MQTT server to the internet.

# Setup

Copy the contents of the folder to your computer. Make sure you have **nodejs** and **npm** installed. Run `npm install` within the folder.

# Run

Start the server with the command `node server`.
