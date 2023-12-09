import os

def basename ( filename ):
    return ".".join( os.path.basename(filename).split(".")[0:-1] )

def extname ( filename ):
    return os.path.basename(filename).split(".")[-1]

