#! /usr/bin/env python
# -*- coding: latin-1 -*-

#  main files  : 
#       filename.py
#
#  specific modules:
#       specific_modules.py
#
#  ==========================================================================
#  Functional description:
#  --------------------------------------------------------------------------
#
#
#  ==========================================================================
#  History:
#  --------------------------------------------------------------------------
#
#
# - ========================================================================== --

#==========================================================================#
# IMPORTS
#==========================================================================#

# Importing Python available modules
import sys, os

# Importing specific modules
import my_simple_gui

#==========================================================================#
# FUNCTIONS/CLASSES DEFINITIONS
#==========================================================================#

# COMMAND LINE HANDLING FUNCTION
def help_cmd_line():
    print( "" )
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] <file ...>" )
    print( "" )
    print( "OPTIONS:" )
    print( "    -o   | --output #" )
    print( "    -v   | --version #" )
    print( "    -r   | --reference #" )

    print( "" )
    print( "    -h   | --help               show this help" )
    exit( -1 )

#==========================================================================#
#==========================================================================#
# MODE EXECUTION HANDLING 
#==========================================================================#
# 1 - The script is the executed as main

if __name__ == "__main__":
    print("\nlaunched as main")
    if len(sys.argv) > 1:
        print("command line mode")
    #======================================================================#
    # a - the script is used with comand line arguments
        fdb       = []
        outfile   = None
        # -----------------------------------------------------------------
        # command line options and arguments handling
        i = 1
        while ( i < len(sys.argv) ):
            if sys.argv[i] == "-o" or sys.argv[i] == "--output":
                i += 1
                outfile = sys.argv[i]
            elif sys.argv[i] == "-v" or sys.argv[i] == "--version":
                i += 1
                version = sys.argv[i]
            elif sys.argv[i] == "-r" or sys.argv[i] == "--reference":
                i += 1
                reference = sys.argv[i]
            elif sys.argv[i] == "-n" or sys.argv[i] == "--name":
                i += 1
                name = sys.argv[i]
            elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
                # help page
                help_cmd_line()
            else:
                fdb.append(sys.argv[i])
            i += 1
        # -----------------------------------------------------------------
        # Computing section example based on the output file passed in arguments
        if outfile == None:
            for f in fdb:
                print( '\n\tComputing: ' + str(f) + ' file' )
        else:
            try:
                fo = open( outfile, 'w' )
                fo.write( """#! /usr/bin/env python# -*- coding: latin-1 -*-""" % os.path.basename(outfile) )
                fo.close()
            except Exception as detail:
                print( detail )
    else:
        #===========================================================================
        # b - the script is used without comand line arguments, the GUI is launched
        print("GUI mode \n")
        app = my_simple_gui.simple_gui(default_color="green")
        my_simple_gui.gui_init(app)
