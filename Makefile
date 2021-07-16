VERSION=`cat VERSION.txt`

venv:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install --upgrade pip build setuptools wheel && \
	pip install -r requirements.txt

release:
	echo Building version $(VERSION) && \
	docker login && \
	docker buildx create --use && \
	docker buildx build \
	  --push \
	  --platform linux/amd64,linux/arm64,linux/arm64/v8 \
	  --tag ejsuncy/sense_energy_prometheus_exporter:"$(VERSION)" . && \
	gh release create "v$(VERSION)" --notes "Release v$(VERSION)"
