import os
import copy
import sys
from bs4 import BeautifulSoup

class HippyGuiManager:

    def __init__(self):
        self.html_report_base = "/home/degrigis/Project/Hippy/gui/base2.html" # base html to modify in order to draw the current state
        self.html_report_folder = "./StateHtmlReports" # this folder will contains all the html generated that describe a state
        self.html_report_current_name = "heapstate_X"  # this will be the name of the generated html report
        self.html_report_counter = 1
        self.current_state_obj = "" # passed later in the run method
        self.current_state_heap_dump = "" # passed later in the run method
        self.current_state_libc_dump = "" # passed later in the run method
        self.soup = []
        return

    def run(self,current_state_obj):

        self.current_state_obj = current_state_obj # the current state to draw on html
        #self.current_state_heap_dump = current_state_heap_dump # this is the hexdump taken of the heap of the program
        #self.current_state_libc_dump = current_state_libc_dump # this is the hexdump taken of the libc data ( the bins )

        if not os.path.exists(self.html_report_folder):
            os.makedirs(self.html_report_folder)

        self.soup = BeautifulSoup(open(self.html_report_base)) # let's open the html_report_base as a soup structure
        html_report_full_path = self.html_report_folder + "/" + self.html_report_current_name.replace("X",str(self.html_report_counter)) # compose finally the name of the html_report_path
        self.html_report_counter = self.html_report_counter + 1 # and increment it :-)

        # now let's start the serious business
        self.write_state_info()
        self.build_heap_state()

        # ok, let's save the modified html
        heap_state_html = self.soup.prettify("utf-8")
        with open(html_report_full_path, "wb") as file:
            file.write(heap_state_html)

        self.soup = []


    # this function will write the curre api invoked and other information
    # related to the state of the heap
    def write_state_info(self):
        div_info = self.soup.find(id="info") # insert the name of the api now
        center_tag =  self.soup.new_tag("center")
        center_tag.string = self.current_state_obj.api_now
        div_info.append(center_tag)

    # this function insert inside the heap_state div of the base html
    # the square related to the heap chunks
    def build_heap_state(self):
        for chunk in self.current_state_obj: # now let's append all the block related to chunks
            r,g,b = chunk.color[0],chunk.color[1],chunk.color[2]
            div_heap_state = self.soup.find(id="heap_state")
            block_tag = self.soup.new_tag("div")
            block_tag['class'] = "block normal"
            block_layout = "width: 100%; height: 6%; background-color: rgb(RXXX, GXXX, BXXX);;"
            block_layout = block_layout.replace("RXXX",r)
            block_layout = block_layout.replace("GXXX",g)
            block_layout = block_layout.replace("BXXX",b)
            block_tag['style'] = block_layout
            block_tag.string = chunk.addr + "<br>" + chunk.type
            div_heap_state.append(block_tag)

        # finally the top chunk
        div_heap_state = self.soup.find(id="heap_state")
        block_tag = self.soup.new_tag("div")
        block_tag['class'] = "block normal"
        block_layout = "width: 100%; height: 100%; background-color: rgb(110, 118, 225);;"
        block_tag['style'] = block_layout
        block_tag.string = "TOP CHUNK"
        div_heap_state.append(block_tag)
