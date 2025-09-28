#!/bin/bash
set -e

echo "Building Lyra microservices..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
REGISTRY=${REGISTRY:-"ghcr.io/jvizueta"}
TAG=${TAG:-"latest"}

echo "Registry: $REGISTRY"
echo "Tag: $TAG"

# Build Lyra AI Agent
echo "Building Lyra AI Agent..."
docker build -t "$REGISTRY/lyra:$TAG" "$PROJECT_ROOT/services/lyra"

# Build WAHA Integrator
echo "Building WAHA Integrator..."
docker build -t "$REGISTRY/waha-integrator:$TAG" "$PROJECT_ROOT/services/waha-integrator"

echo "Build completed successfully!"

# Optional: Push to registry if PUSH=true
if [ "$PUSH" = "true" ]; then
    echo "Pushing images to registry..."
    docker push "$REGISTRY/lyra:$TAG"
    docker push "$REGISTRY/waha-integrator:$TAG"
    echo "Images pushed successfully!"
fi

echo ""
echo "Built images:"
echo "  - $REGISTRY/lyra:$TAG"
echo "  - $REGISTRY/waha-integrator:$TAG"
echo ""
echo "Usage examples:"
echo "  # Build only:"
echo "  ./scripts/build.sh"
echo ""
echo "  # Build and push:"
echo "  PUSH=true ./scripts/build.sh"
echo ""
echo "  # Custom registry and tag:"
echo "  REGISTRY=your-registry.com TAG=v1.0.0 ./scripts/build.sh"