#!/bin/bash
set -e

REGISTRY="us-central1-docker.pkg.dev/project-2f3c2d48-8095-4bfd-991/tennis-court-registry"
IMAGE="$REGISTRY/book-a-tennis-court"

gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

docker build --platform linux/amd64 -t "$IMAGE" .
docker push "$IMAGE"
