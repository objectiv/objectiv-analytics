clean:
	# clean up caches
	find core plugins queues trackers transports -type d -name dist -o -name coverage -o -name .npmrc -not -path '*node_modules*'  | xargs rm -rf

build: clean
	yarn install && yarn build

publish: build
	cd verdaccio && make  run
	yarn publish:verdaccio
