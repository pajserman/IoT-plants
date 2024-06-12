// A super simple backend that gets the data from the local MQTT server
// running on the same network and forwards the data in json format over
// HTTP.  This server is open to the internet at https://plant.hannes.pro
// but the MQTT server is NOT. This make sure that the plant data can be
// accessed anywhere without exposing the whole MQTT server to the internet.
const mqtt = require('mqtt')
const http = require('http')
const protocol = 'mqtt'
const host = '192.168.1.226'
const port = '1883'

const connectURL = `${protocol}://${host}:${port}`

const client = mqtt.connect(connectURL, {
	clean: true,
	connectTimeout: 4000,
	reconnectPeriod: 1000
})

const topic = 'Pico/sensor'

client.on('connect', () => {
	console.log('Connected')
	client.subscribe([topic], () => {
	console.log(`Subscribed to ${topic}`)
	})
})

client.on('message', (topic, payload) => {
	parsedString = payload.toString()
	parsedJSON= JSON.parse(payload.toString())
	parsedJSON.time = new Date().toLocaleString()
	parsedJSON.sunshine = parsedJSON.sunshine === 1 ? true : false
	parsedString = JSON.stringify(parsedJSON)
})


http.createServer( (req, res) => {
	res.setHeader("Access-Control-Allow-Origin", "*")
	if(typeof parsedString === 'undefined') {
		res.writeHead(503, {'Content-Type': 'application/json'})
		res.write('{error: "No data"}')
        } else {
		res.writeHead(200, {'Content-Type': 'application/json'})
		res.write(parsedString)
	}
	res.end()
}).listen(8080)

