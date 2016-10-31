## What the heck is Heapy?

Heapy is an heap tracer and visualizer for the glibc’s malloc implementation based on LD_PRELOAD, it works both for 32 and 64 bit binaries.

## Why Heapy?

Heapy borns with [villoc](https://github.com/wapiflapi/villoc) in mind. However , nonetheless I found [villoc](https://github.com/wapiflapi/villoc) very useful, I've always felt "blind" while using it. I mean: I am visualizing the heap chunks allocated, but in order to see inside them I have no other choice to use gdb...

Starting from this I thought: "Why not track the heap allocation functions and also dump the heap?". That's basically the core idea behind Heapy: track heap functions, dump the heap and correlate the info about the dump with the state of the heap.

Oh, and Heapy also dumps the malloc_state struct in memory! 

What does it means? 

You can see the free-list bins working live! It is a really good way to learn fastly 
how the free-list mechanism works in ptmalloc2.

## How it works?

While [villoc](https://github.com/wapiflapi/villoc) relies basically on ltrace, Heapy exploits LD_PRELOAD to preload a library that replaces our friends malloc,calloc,realloc,free with our custom functions.
It works basically as the malloctracer inside [preeny](https://github.com/zardus/preeny)...but on steroids.

## Requirements

1)sudo pip install bs4

2)sudo apt-get install libc6-dev-i386

3)Also remember to enable ptrace: ( do this in a vm or remember to disable it after the analysis ) 
   - sudo su root
   - echo 0 > /proc/sys/kernel/yama/ptrace_scope
   - su -your user-

## Usage

1) git clone https://github.com/degrigis/Heapy.git

2) Install requirements if needed.

3) Move cloned folder in your preferred location.

4) cd /Heapy/src & ./BUILD.sh

4) Change the variable HEAPY_PATH inside the file GoHeapy.py with the folder where you have copied the cloned repo.
   - example: HEAPY_PATH = "/home/degrigis/Project/Heapy"

5) Now copy GoHeapy.py in the same folder of the program you want to trace and launch:
   - python GoHeapy.py ./program-traced 

   OR 

   - python GoHeapy.py ./program-traced ./input.txt ( this if you have an input file )

6) If all ok you should see a folder called HeapReport that will contains some html.

7) Open the first html file. Now you can navigate between the report using the arrow keys. :-)

## Screenshots

![alt tag](http://i.imgur.com/E7o2psg.png)

## Note

The current version of Heapy is a dirty and incomplete beta, but it should works well with libc 2.19 and 2.23.

I'm planning to add lots of new functionalities as for example tracking allocation errors ( that could be really useful during heap exploitation ), better correlation between the chunks and the dump etc...

Also the current graphic is in testing, the horizontal view of [villoc](https://github.com/wapiflapi/villoc) sometimes fits better rather than my vertical one. Feedbacks are really appreciated! 

## Thanks

1) [readmem](https://github.com/anacrolix/various/blob/e41b93b1b3e2accd540ebdf5d126e7d0fbf7af77/tibia/butox/cutil/readmem.c)

2) [villoc](https://github.com/wapiflapi/villoc)

3) [preeny](https://github.com/zardus/preeny)

