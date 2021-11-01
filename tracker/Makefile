clean:
	# clean up caches
	find core plugins trackers -type d -name dist -o -name coverage -not -path '*node_modules*'  | xargs rm -rf

build: clean
	yarn install && yarn build

publish: build
	cd verdaccio && make  run
	yarn publish
