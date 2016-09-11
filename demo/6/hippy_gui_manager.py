import os
import copy
import sys
from bs4 import BeautifulSoup

import pdb

# configurable parameter libc-version dependente
# these are the lines to take in order to retrieve the malloc_state
# from the libc data segment
supported_libc = {"2.23": "61-95"}

class HippyGuiManager:

    def __init__(self):
        self.html_report_base = "/home/degrigis/Project/Hippy/gui/base2.html" # base html to modify in order to draw the current state
        self.html_report_folder = "./StateHtmlReports" # this folder will contains all the html generated that describe a state
        self.html_report_current_name = "heapstate_X"  # this will be the name of the generated html report
        self.html_report_counter = 1
        self.heap_dump_folder = "./HeapDumps/"
        self.libc_dump_folder = "./LibcDumps/"
        self.current_state_obj = "" # passed later in the run method
        self.current_state_heap_dump = "" # passed later in the run method
        self.current_state_libc_dump = "" # passed later in the run method
        self.soup = []
        self.proc_info = []
        return

    def run(self,prev_state,current_state_obj, next_state, proc_info):

        self.current_state_obj = current_state_obj # the current state to draw on html
        self.proc_info = proc_info
        #self.current_state_heap_dump = current_state_heap_dump # this is the hexdump taken of the heap of the program
        #self.current_state_libc_dump = current_state_libc_dump # this is the hexdump taken of the libc data ( the bins )

        if not os.path.exists(self.html_report_folder):
            os.makedirs(self.html_report_folder)

        self.soup = BeautifulSoup(open(self.html_report_base),"html.parser") # let's open the html_report_base as a soup structure
        html_report_full_path = self.html_report_folder + "/" + self.html_report_current_name.replace("X",str(self.html_report_counter)) # compose finally the name of the html_report_path
        self.html_report_counter = self.html_report_counter + 1 # and increment it :-)

        # now let's start the serious business
        self.write_state_info(prev_state,next_state)
        self.build_heap_state()
        self.paste_heap_dump(self.current_state_obj)
        self.paste_libc_dump(self.current_state_obj)

        # ok, let's save the modified html
        heap_state_html = self.soup.prettify("utf-8")
        with open(html_report_full_path, "wb") as file:
            file.write(heap_state_html)

        self.soup = []


    # this function will write the current api invoked and other information
    # related to the state of the heap
    def write_state_info(self,prev_state,next_state):
        div_info = self.soup.find(id="info") # insert the name of the api now

        if prev_state != []:
            center_tag =  self.soup.new_tag("center")
            div_info_line = self.soup.new_tag('div')
            div_info_line.string = "PREVCALL: " + str(prev_state.api_now)
            div_info_line['style'] = "font-size:10;font-family: monospace;"
            center_tag.append(div_info_line)
            div_info.append(center_tag)

        center_tag =  self.soup.new_tag("center")
        div_info_line = self.soup.new_tag('div')
        center_tag.string = "CURRENTCALL: " + self.current_state_obj.api_now
        div_info_line['style'] = "font-size:20;font-family: monospace;"
        center_tag.append(div_info_line)
        div_info.append(center_tag)

        if next_state != []:
            center_tag =  self.soup.new_tag("center")
            div_info_line = self.soup.new_tag('div')
            div_info_line.string = "NEXTCALL: " + str(next_state.api_now)
            div_info_line['style'] = "font-size:10;font-family: monospace;"
            center_tag.append(div_info_line)
            div_info.append(center_tag)
            div_info.append(center_tag)

    # this function insert inside the heap_state div of the base html
    # the square related to the heap chunks
    def build_heap_state(self):
        for chunk in self.current_state_obj: # now let's append all the block related to chunks
            if chunk.status == "allocated":
                r,g,b = chunk.color[0],chunk.color[1],chunk.color[2]
                div_heap_state = self.soup.find(id="heap_state")
                block_tag = self.soup.new_tag("div")
                block_tag['class'] = "block normal"
                block_layout = "width: 100%; height: 6%; background-color: rgb(RXXX, GXXX, BXXX);;"
                block_layout = block_layout.replace("RXXX",r)
                block_layout = block_layout.replace("GXXX",g)
                block_layout = block_layout.replace("BXXX",b)
                block_tag['style'] = block_layout
                block_tag.string = chunk.addr + "-" + chunk.type
                div_heap_state.append(block_tag)
            if chunk.status == "free":
                div_heap_state = self.soup.find(id="heap_state")
                block_tag = self.soup.new_tag("div")
                block_tag['class'] = "block normal"
                block_layout = "width: 100%; height: 6%; background-color: rgb(255, 255, 255);;"
                block_tag['style'] = block_layout
                block_tag.string = chunk.addr + "-FREE" + "-" + chunk.type
                div_heap_state.append(block_tag)

        div_heap_state = self.soup.find(id="heap_state")
        block_tag = self.soup.new_tag("div")
        block_tag['class'] = "block normal"
        block_layout = "width: 100%; height: 100%; background-color: rgb(0, 255, 0);;"
        block_tag['style'] = block_layout
        block_tag.string = "TOP CHUNK"
        div_heap_state.append(block_tag)


    def paste_heap_dump(self,state):
        heap_dump_full_path = self.heap_dump_folder + state.dump_name
        f = open(heap_dump_full_path, "r")
        div_heapdump = self.soup.find(id="heapdump") # insert the name of the api now
        for line in f.readlines():
            p_tag = self.soup.new_tag('p')
            p_tag.string = str(line)
            p_tag['style'] = "font-family: monospace;"
            div_heapdump.append(p_tag)
            div_space_tag = self.soup.new_tag('div')
            div_space_tag['style'] = "font-size:0;height:1px;"
            div_heapdump.append(div_space_tag)

    def paste_libc_dump(self,state):
        libc_dump_full_path = self.libc_dump_folder + state.libc_dump_name
        f = open(libc_dump_full_path, "r")
        div_heapdump = self.soup.find(id="libcdump")
        libc_version = self.proc_info.libc_version

        lines_range = supported_libc.get(libc_version,"")
        if lines_range != "":
            start_line = int(lines_range.split("-")[0])
            end_line = int(lines_range.split("-")[1])
        else:
            print "[ERROR] Libc not supported"
            sys.exit(0)

        cont = 1

        for line in f.readlines(): # this optimization in order to avoid pase unuseful stuff in the libc view
            if cont < start_line:
                cont+=1
                continue
            if cont > end_line:
                break
            p_tag = self.soup.new_tag('p')
            p_tag.string = str(line)
            p_tag['style'] = "font-family: monospace;"
            div_heapdump.append(p_tag)
            div_space_tag = self.soup.new_tag('div')
            div_space_tag['style'] = "font-size:0;height:1px;"
            div_heapdump.append(div_space_tag)
            cont += 1
