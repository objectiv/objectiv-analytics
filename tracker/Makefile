clean:
	# clean up caches
	find core plugins trackers -type d -name dist -o -name coverage -o -name .npmrc -not -path '*node_modules*'  | xargs rm -rf

build: clean
	yarn install && yarn build

publish: build
	cd verdaccio && make  run
	yarn publish:verdaccio

merge-coverage:
	rm -rf .nyc_output
	mkdir .nyc_output
	cp `find core plugins trackers -type f -name coverage-final.json -not -path '*node_modules*'` --backup=numbered .nyc_output
	nyc merge .nyc_output
	nyc report --reporter=lcov
	rm coverage.json
	rm -rf .nyc_output
