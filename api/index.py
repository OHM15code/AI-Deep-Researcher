import sys
import os

# Add src to sys.path to allow importing from the researcher package
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from researcher.app import app
from mangum import Mangum

# Create a handler for AWS Lambda / Vercel
handler = Mangum(app)
