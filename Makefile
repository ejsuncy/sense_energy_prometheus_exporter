VERSION=`cat VERSION.txt`

venv:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install --upgrade pip build setuptools wheel && \
	pip install -r requirements.txt


build:
	echo Building version $(VERSION) && \
	docker buildx create --use && \
	docker buildx build \
	  --platform linux/amd64,linux/arm64 \
	  --tag ejsuncy/sense_energy_prometheus_exporter:"$(VERSION)" .

release-dockerhub:
	echo Building version $(VERSION) && \
	docker login && \
	docker buildx create --use && \
	docker buildx build \
	  --push \
	  --platform linux/amd64,linux/arm64 \
	  --tag ejsuncy/sense_energy_prometheus_exporter:"$(VERSION)" \
	  --tag ejsuncy/sense_energy_prometheus_exporter:latest .

release-github:
	export GITHUB_TOKEN="" && \
	gh auth login && \
	gh release create "v$(VERSION)" -F Changelog.md
