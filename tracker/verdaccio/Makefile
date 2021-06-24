run:
	docker run -d --rm -it --name verdaccio -v $(PWD)/config.yaml:/verdaccio/conf/config.yaml -p 4873:4873 --network verdaccio verdaccio/verdaccio:5

stop:
	docker stop verdaccio
