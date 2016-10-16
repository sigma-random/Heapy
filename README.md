## What the heck is Heapy?

Heapy is an heap tracer and visualizer for ptmalloc2 based on LD_PRELOAD, it works both for 32 and 64 bit binaries.

## Why Heapy?

Heapy borns with [villoc](https://github.com/wapiflapi/villoc) in mind. However , nonetheless I found [villoc](https://github.com/wapiflapi/villoc) very useful, I've always felt "blind" while using it. I mean: I am visualizing the heap chunks allocated, but in order to see inside them I have no other choice to use gdb...

Starting from this I thought: "Why not track the heap allocation functions and also dump the heap?". That's basically the core idea behind Heapy: track heap functions, dump the heap and correlate the info about the dump with the state of the heap.

Oh, and Heapy also dumps the malloc_state struct in memory! 

What does it means? 

You can see the free-list bins working live! It is a really good way to learn fastly 
how the free-list mechanism works in ptmalloc2.

## How it works?

While [villoc](https://github.com/wapiflapi/villoc) relies basically on ltrace. Hippy relies on a preloaded library (well, LD_PRELOAD) that replaces our friends malloc,calloc,realloc,free with our custom functions.
It works basically as the malloctracer inside [preeny](https://github.com/zardus/preeny)...but on steroids.

## Note

The current version of Heapy is a dirty and incomplete beta, but it should works well with libc 2.19 and 2.23.

I'm planning to add lots of new functionalities as for example tracking allocation errors ( that could be really useful during heap exploitation ), better correlation between the chunks and the dump etc...

Also the current graphic is in testing, the horizontal view of [villoc](https://github.com/wapiflapi/villoc) sometimes fits better rather than my vertical one. Feedbacks are really appreciated! 


## Screenshots



## Thanks

1) 

## Usage

[TODO]