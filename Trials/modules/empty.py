import os

def clearall(file):
    if os.path.exists(file):
        os.remove(file)
        