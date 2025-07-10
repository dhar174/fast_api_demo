"""
Simple test to verify the FastAPI application setup
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all required modules can be imported"""
    try:
        import fastapi

        print(f"✓ FastAPI version: {fastapi.__version__}")

        import torch

        print(f"✓ PyTorch version: {torch.__version__}")

        import torchvision

        print(f"✓ Torchvision version: {torchvision.__version__}")

        import PIL

        print(f"✓ Pillow version: {PIL.__version__}")

        import uvicorn

        print(f"✓ Uvicorn installed")

        print("\n✅ All dependencies are properly installed!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_server_creation():
    """Test that the server can be created without errors"""
    try:
        from server import app

        print("✓ FastAPI app created successfully")

        # Check if the app has the expected routes
        routes = [route.path for route in app.routes]
        print(f"✓ Available routes: {routes}")

        return True

    except Exception as e:
        print(f"❌ Server creation error: {e}")
        return False


if __name__ == "__main__":
    print("FastAPI Image Classifier - Setup Test")
    print("=" * 40)

    # Test imports
    if test_imports():
        print("\n" + "=" * 40)
        # Test server creation
        if test_server_creation():
            print("\n🎉 Setup completed successfully!")
            print("\nTo start the server, run:")
            print("  python server.py")
            print("\nThen visit: http://localhost:8000/docs")
        else:
            print("\n❌ Server setup failed")
    else:
        print("\n❌ Dependencies not properly installed")
