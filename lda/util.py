import sys

# constants
VERBOSE = 1
VERBOSE_FILE = sys.stderr

# utililty variables

vfile = VERBOSE_FILE

# utililty functions
 
def v_print(text):
    vfile.writelines(text)
