run:
	docker network create verdaccio
	docker run -d --rm -it --name verdaccio -v $(PWD)/config.yaml:/verdaccio/conf/config.yaml -p 127.0.0.1:4873:4873 --network verdaccio verdaccio/verdaccio:5

	# here we add tinyproxy to verdaccio, configure it, and start it up. This will allow other docker containers
	# in the same network to set HTTP_PROXY to this instance (env HTTP_PROXY=http://verdaccio:4873). This will, in turn,
	# allow yarn to still connect to localhost (as localhost, to the proxy, will be verdaccio). And thus use
	# the same config, as when running locally in dev mode.
	docker exec -tiu0 verdaccio ash -c 'apk update && apk add tinyproxy && echo "Allow 172.0.0.0/8" >> /etc/tinyproxy/tinyproxy.conf && tinyproxy'

stop:
	docker stop verdaccio
	docker network rm verdaccio
