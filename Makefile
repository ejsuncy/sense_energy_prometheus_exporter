VERSION=`cat VERSION.txt | tr -d '\n'`
CURRENT_BRANCH=`git rev-parse --abbrev-ref HEAD | tr -d '\n'`

venv:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install --upgrade pip build setuptools wheel && \
	pip install -r requirements.txt

build:
	echo Building version $(VERSION) && \
	docker buildx create --use && \
	docker buildx build . \
	  --platform linux/amd64,linux/arm64/v8 \
	  --tag ghcr.io/ejsuncy/sense_energy_prometheus_exporter:"$(VERSION)"

release-dockerhub:
	echo Building version $(VERSION) && \
	docker login && \
	docker buildx create --use && \
	docker buildx build . \
	  --push \
	  --platform linux/amd64,linux/arm64/v8 \
	  --tag ejsuncy/sense_energy_prometheus_exporter:"$(VERSION)"

release-ghcr:
	echo Building version $(VERSION) && \
	echo $GITHUB_CR_PAT| docker login ghcr.io -u ejsuncy --password-stdin && \
	docker buildx create --use && \
	docker buildx build . \
	  --push \
	  --platform linux/amd64,linux/arm64/v8 \
	  --tag ghcr.io/ejsuncy/sense_energy_prometheus_exporter:"$(VERSION)"

release-github:
	gh release create --draft --generate-notes --target main --title "Release v$(VERSION)" "v$(VERSION)"

release-patch-github:
	gh release create --draft --generate-notes --target $(CURRENT_BRANCH) --title "Patch v$(VERSION)" "v$(VERSION)"
