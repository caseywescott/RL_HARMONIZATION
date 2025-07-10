# RL Harmonization Project Makefile

.PHONY: help install test train clean lint format docs

# Default target
help:
	@echo "🎵 RL Harmonization Project"
	@echo "=========================="
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  train      - Train harmonization agents"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code with black"
	@echo "  clean      - Clean generated files"
	@echo "  docs       - Generate documentation"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip3 install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run tests
test:
	@echo "🧪 Running tests..."
	python3 test_implementation.py
	@echo "✅ Tests completed"

# Train harmonization agents
train:
	@echo "🎵 Training harmonization agents..."
	python3 train_harmonization.py
	@echo "✅ Training completed"

# Run linting
lint:
	@echo "🔍 Running linting..."
	flake8 src/ --max-line-length=88 --ignore=E203,W503
	mypy src/ --ignore-missing-imports
	@echo "✅ Linting completed"

# Format code
format:
	@echo "🎨 Formatting code..."
	black src/ --line-length=88
	@echo "✅ Code formatted"

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf models/
	rm -rf logs/
	rm -rf outputs/
	rm -rf __pycache__/
	rm -rf src/**/__pycache__/
	@echo "✅ Clean completed"

# Generate documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "Documentation is in markdown format in the project root"
	@echo "✅ Documentation ready"

# Quick setup for new environment
setup: install format lint test
	@echo "🚀 Setup completed! Ready to train."

# Development workflow
dev: format lint test
	@echo "🔄 Development cycle completed" 