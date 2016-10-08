'''
Formatter libc 2.19 x64 bit
'''

import os
import copy
import sys
from bs4 import BeautifulSoup
import pdb
import math

supported_libc = {"2.19-64": "60-128", "2.23-32": "61-95" , "2.23-64": "89-158"}

flags_div = None
fastbin_divs = [] # list of fastbins div that we will add to the final report
top_chunk_div = None
last_remain_div = []
last_remain_fd_div = None
last_remain_bk_div = None
small_bins_divs = []
large_bins_divs = []

def format(libc_dump_full_path,proc_info,soup):

    f = open(libc_dump_full_path, "r")
    div_libcdump = soup.find(id="libcdump")
    libc_version = proc_info.libc_version
    arch = proc_info.architecture

    lines_range = supported_libc.get(libc_version+"-"+arch,"")
    if lines_range != "": # let's extract only the lines in which there is the malloc_state struct
        start_line = int(lines_range.split("-")[0],10)
        end_line = int(lines_range.split("-")[1],10)
    else:
        print "[ERROR] Libc not supported"
        sys.exit(0)

    cont = 1

    for i in xrange(0,start_line,1):
        line = f.readline().rstrip() # skip unuseful lines

    line = line.split(" ")
    line = line[1:] # remove the memory address

    #space
    div_space = soup.new_tag('div')
    div_space['style'] = "font-size:0;height:20px;"

    # flags qwords
    flags_div = soup.new_tag('div')
    flags_div['style'] = "font-family: monospace;display:inline;"
    flags_div.string = "flags: " + line[1] + line[0]

    line = line[2:] # discard the first processed elements

    div_libcdump.append(flags_div)
    div_libcdump.append(div_space)

    flags_div = soup.new_tag('div')
    flags_div['style'] = "font-family: monospace;display:inline;"
    flags_div.string = "fastbin[0]-> " + line[1] + line[0]

    div_libcdump.append(flags_div)

    '''
    # large bins
    for i in xrange(0,32,1):
        large_bin = []
        next_line = f.readline()
        next_line = next_line.split(" ")
        next_line = next_line[1:]
        large_bin_fd = line[1] + line[0]
        large_bin_bk = next_line[1] + next_line[0]
        large_bin.append(large_bin_fd)
        large_bin.append(large_bin_bk)
        large_bins_divs.append(large_bin)
        line = next_line
        line = line[2:]
        large_bin = []
        large_bin_fd = line[1] + line[0]
        line = line[2:]
        large_bin_bk = next_line[1] + next_line[0]
        large_bin.append(large_bin_fd)
        large_bin.append(large_bin_bk)
        large_bins_divs.append(large_bin)
    '''
