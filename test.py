# In a Python REPL or a scratch script (do not commit)
from data.loader import load_vendors
vendors = load_vendors()
print(len(vendors))  # Expect 17
