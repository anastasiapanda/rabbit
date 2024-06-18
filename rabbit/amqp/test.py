import os
from dotenv import load_dotenv

load_dotenv()
print(os.environ.get('CLOUDAMQP_URL','empty'))