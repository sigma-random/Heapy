'''
Formatter libc 2.19 x64 bit
'''

import os
import copy
import sys
from bs4 import BeautifulSoup
import pdb
import math

# configurable parameter libc-version dependent
# these are the lines to take in order to retrieve the malloc_state
# from the libc data segment
# f.i. 2.23-32 is the libc 2.23 on 32 bit, 61-96 means that from line 61 to 95 of the hexdump we have the info about bins
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
    div_space['style'] = "font-size:0;height:5px;"

    # flags qwords
    flags_div = soup.new_tag('div')
    flags_div['style'] = "font-family: monospace;display:inline;"
    flags_div.string = "flags: " + line[1] + line[0]

    line = line[2:] # discard the first processed elements

    # fastbins
    for i in xrange(0,10,1):
        if line == []:
            line = f.readline().rstrip().split(" ")
            line = line[1:]

        fastbin_div = soup.new_tag('div')
        fastbin_div['style'] = "font-family: monospace;display:inline;"
        fastbin_div.string = "fastbin["+str(i)+"]-> 0x" + line[1] + line[0]
        div_libcdump.append(fastbin_div)
        div_space = soup.new_tag('div')
        div_space['style'] = "font-size:0;height:5px;"
        div_libcdump.append(div_space)
        line = line[2:]

    #top chunk
    top_chunk_div = soup.new_tag('div')
    top_chunk_div['style'] = "font-family: monospace;display:inline;"
    top_chunk_div.string = "topchunk: 0x" + line[1] + line[0]
    div_libcdump.append(top_chunk_div)
    div_space = soup.new_tag('div')
    div_space['style'] = "font-size:0;height:5px;"
    div_libcdump.append(div_space)

    line = f.readline().rstrip().split(" ")
    line = line[1:]

    #last remains
    last_remain_div = soup.new_tag('div')
    last_remain_div['style'] = "font-family: monospace;display:inline;"
    last_remain_div.string = "last remainder: 0x" + line[1] + line[0]
    div_libcdump.append(last_remain_div)
    div_space = soup.new_tag('div')
    div_space['style'] = "font-size:0;height:5px;"
    div_libcdump.append(div_space)

    line = line[2:]

    #unsorted bin
    unsorted_bin_fd = soup.new_tag('div')
    unsorted_bin_fd['style'] = "font-family: monospace;display:inline;"
    unsorted_bin_fd.string = "unsorted bin{fd} -> 0x" + line[1] + line[0]
    div_libcdump.append(unsorted_bin_fd)

    div_space = soup.new_tag('div')
    div_space['style'] = "font-size:0;height:5px;"
    div_libcdump.append(div_space)

    line = line[2:]

    unsorted_bin_fd = soup.new_tag('div')
    unsorted_bin_fd['style'] = "font-family: monospace;display:inline;"
    unsorted_bin_fd.string = "unsorted bin{bk} -> 0x" + line[1] + line[0]
    div_libcdump.append(unsorted_bin_fd)

    line = line[2:]

    div_space = soup.new_tag('div')
    div_space['style'] = "font-size:0;height:5px;"
    div_libcdump.append(div_space)

    #small bins
    for i in xrange(0,62,1):
        if len(line) == 2:
            nextline = f.readline().rstrip().split(" ")
            nextline = nextline[1:]
            small_bin_fd = soup.new_tag('div')
            small_bin_fd['style'] = "font-family: monospace;display:inline;"
            small_bin_fd.string = "smallbin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
            div_libcdump.append(small_bin_fd)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            small_bin_bk = soup.new_tag('div')
            small_bin_bk['style'] = "font-family: monospace;display:inline;"
            small_bin_bk.string = "smallbin["+str(i)+"]{bk}-> 0x" + nextline[1] + nextline[0]
            div_libcdump.append(small_bin_bk)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            line = nextline
            line = line[2:]
        else:
            small_bin_fd = soup.new_tag('div')
            small_bin_fd['style'] = "font-family: monospace;display:inline;"
            small_bin_fd.string = "smallbin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
            div_libcdump.append(small_bin_fd)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            line = line[2:]
            small_bin_bk = soup.new_tag('div')
            small_bin_bk['style'] = "font-family: monospace;display:inline;"
            small_bin_bk.string = "smallbin["+str(i)+"]{bk}-> 0x" + line[1] + line[0]
            div_libcdump.append(small_bin_bk)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            line = line[2:]


    #large bins
    for i in xrange(0,63,1):
        if len(line) == 2:
            nextline = f.readline().rstrip().split(" ")
            nextline = nextline[1:]
            large_bin_fd = soup.new_tag('div')
            large_bin_fd['style'] = "font-family: monospace;display:inline;"
            large_bin_fd.string = "largebin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
            div_libcdump.append(large_bin_fd)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            large_bin_bk = soup.new_tag('div')
            large_bin_bk['style'] = "font-family: monospace;display:inline;"
            large_bin_bk.string = "largebin["+str(i)+"]{bk}-> 0x" + nextline[1] + nextline[0]
            div_libcdump.append(large_bin_bk)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            line = nextline
            line = line[2:]
        else:
            large_bin_fd = soup.new_tag('div')
            large_bin_fd['style'] = "font-family: monospace;display:inline;"
            large_bin_fd.string = "largebin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
            div_libcdump.append(large_bin_fd)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            line = line[2:]
            large_bin_bk = soup.new_tag('div')
            large_bin_bk['style'] = "font-family: monospace;display:inline;"
            large_bin_bk.string = "largebin["+str(i)+"]{bk}-> 0x" + line[1] + line[0]
            div_libcdump.append(large_bin_bk)
            div_space = soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            line = line[2:]

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
