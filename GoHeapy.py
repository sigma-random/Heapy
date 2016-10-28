from subprocess import Popen, PIPE, STDOUT
import json
import copy
import sys
import random
import os
from shutil import copyfile

# insert here the path of hippy
HEAPY_PATH = "/home/degrigis/Project/Heapy"

def Usage():
    print "Usage: python ./GoHeapy.py ./trace_me_32 <OutputFolderName> [input.out]\n"
    sys.exit(0)

if __name__ == '__main__':

    input_for_program = " "

    if len(sys.argv) < 2:
     Usage()

    program_to_trace = sys.argv[1] # first argument is the name of the program to trace

    if len(sys.argv) == 3:
        input_for_program = sys.argv[2] # file containing input for the program

    # which tracer we have to pick? 32 or 64?
    cmd = "file " + program_to_trace
    pinfo = Popen(cmd, shell=True, stdout=PIPE, close_fds=True)
    output = pinfo.stdout.read()

    if "ELF 64-bit" in output:
        path_arch = "amd64"
    elif "ELF 32-bit" in output:
        path_arch = "i386"

    #working directory in which we will put all our stuff
    working_directory = HEAPY_PATH +"/WorkingDirectory/"
    os.makedirs(working_directory)

    # preparing the working directory with all the stuff we need 
    p = Popen(['cp','-p','--preserve',HEAPY_PATH + "/bin/" + path_arch + "/tracer.so",working_directory + "tracer.so"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HEAPY_PATH + "/bin/" + path_arch + "/tracer_child",working_directory + "tracer_child"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HEAPY_PATH + "/bin/" + path_arch + "/readmem",working_directory + "readmem"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HEAPY_PATH + "/HeapyGuiManager.py",working_directory + "HeapyGuiManager.py"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HEAPY_PATH + "/Heapy.py",working_directory + "Heapy.py"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HEAPY_PATH + "/HeapyLibcFormatter.py",working_directory + "HeapyLibcFormatter.py"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HEAPY_PATH + "/gui/report_base.html",working_directory + "report_base.html"])
    p.wait()
    p = Popen(['cp','-p','--preserve',program_to_trace,working_directory + program_to_trace.split("/")[-1]])
    p.wait()

    if input_for_program != " ":
        p = Popen(['cp','-p','--preserve',input_for_program,working_directory + input_for_program.split("/")[-1]])
        p.wait()

    cmd = "python " + "./Heapy.py" + " " + program_to_trace
    if input_for_program != " ":
        cmd += " " + input_for_program

    curr_dir = os.getcwd()
    os.chdir(working_directory)

    pheapy = Popen(cmd, shell=True, close_fds=True)
    pheapy.wait()

    # copy the heap report in the original folder
    p = Popen(['cp','-r',working_directory+"HeapReport",curr_dir])
    p.wait()


    # copy the heap report in the original folder
    p = Popen(['rm','-r',working_directory])
    p.wait()
