FROM nodered/node-red:latest

USER root

RUN apk update && \
	apk add bind-tools && \
	npm install node-red-contrib-python-function node-red-contrib-influxdb node-red-contrib-bigtimer && \
	npm install node-red-contrib-tasmota && \
	npm install node-red-contrib-pushover && \
	npm audit fix

	

