from subprocess import Popen, PIPE, STDOUT
import json
import copy
import sys
import random
import os
from HeapyGuiManager import HeapyGuiManager
from shutil import copyfile

# insert here the path of hippy
HEAPY_PATH = "/home/degrigis/Tool/Heapy/"

def Usage():
    print "Usage: python ./GoHeapy.py ./trace_me_32 [input.out]\n"
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
     Usage()
    elif len(sys.argv) == 2:
        program_to_trace = sys.argv[1]
        input_for_program = " "
    elif len(sys.argv) == 3:
        program_to_trace = sys.argv[1]
        input_for_program = sys.argv[2]

    # which tracer we have to pick? 32 or 64?
    cmd = "file " + program_to_trace
    pinfo = Popen(cmd, shell=True, stdout=PIPE, close_fds=True)
    output = pinfo.stdout.read()

    if "ELF 64-bit" in output:
        path_arch = "amd64"
    elif "ELF 32-bit" in output:
        path_arch = "i386"

    #working directory in which we will put all our stuff
    working_directory = HEAPY_PATH +"WorkingDirectory/"
    os.makedirs(working_directory)

    # preparing the working directory
    p = Popen(['cp','-p','--preserve',HIPPY_PATH + "/bin/" + path_arch + "/tracer.so",working_directory + "/tracer.so"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HIPPY_PATH + "/bin/" + path_arch + "/tracer_child",working_directory + "/tracer_child"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HIPPY_PATH + "/bin/" + path_arch + "/readmem",working_directory + "/readmem"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HIPPY_PATH + "/HeapyGuiManager.py",working_directory + "/HeapyGuiManager.py"])
    p.wait()
    p = Popen(['cp','-p','--preserve',HIPPY_PATH + "/Heapy.py",working_directory + "/Heapy.py"])
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
    p = Popen(['cp','-r',working_directory+"StateHtmlReports",curr_dir])
    p.wait()


    # copy the heap report in the original folder
    p = Popen(['rm','-r',working_directory])
    p.wait()
