#!/bin/bash

# Docker build and push script for Zion Discord Bot
# Usage: ./build.sh <version>

set -e # Exit on any error

# Check if version argument is provided
if [ $# -eq 0 ]; then
    echo "Error: Version argument is required"
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.1"
    exit 1
fi

VERSION=$1
USERNAME="ibfleming"
APP="zion-discord-bot"

echo "Building Docker image for $APP version $VERSION..."

# Build the Docker image
echo "Step 1: Building Docker image..."
docker build -t $APP .

# Tag the image with version and latest
echo "Step 2: Tagging Docker image..."
docker tag $APP $USERNAME/$APP:$VERSION
docker tag $APP $USERNAME/$APP:latest

# We would login in here but our dev container is using local
# Docker config which should have a personal access token and
# therefore we are already authenticated

# Push the versioned image
echo "Step 4: Pushing versioned image ($VERSION)..."
docker push $USERNAME/$APP:$VERSION

echo "✅ Successfully built and pushed $APP:$VERSION"
echo "Images pushed to:"
echo "  - $USERNAME/$APP:$VERSION"
