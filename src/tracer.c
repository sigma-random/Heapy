/*
 http://elinux.org/images/b/b5/Elc2013_Kobayashi.pdf
 COMPILE: gcc -shared -fPIC -o tracer.so tracer.c -ldl
 RUN: LD_PRELOAD=./tracer.so /home/degrigis/Desktop/datastore/datastore < /home/degrigis/Desktop/datastore/inputs_test

 DOUBTS: with this technique I can't track all the writes inside heap zones ( I can hook memcpy and friends, but... ).
 Then I have to handle special cases in order to avoid infinite call to the hook: for example if i call the printf
 inside a wrapper, it calls malloc that call printf that calls malloc............
 Also the code inside the wrapper must be heap-allocation-free otherwise
 we are going to dirty the tracing by insertig chunks related to the wrapper itself.

 The pro of this technique is that I can see malloced chunks allocated inside other function as printf, while
 with ltrace I can't see these chunks!

The difference of the behavior of the heap allocation in a 32 and 64 bit programs strongly depend on the
tuning parameter M_MXFAST ( http://man7.org/linux/man-pages/man3/mallopt.3.html ).
Basically if chunks are smaller than 64*sizeof(size_t)/4 they are never freeded but kept inside the fastbin
ready to be allocated.
*/

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h> //needed for strtoul ( otherwise the conversion from a uint64 string to uint64 keep only the lowest part )
#include <dlfcn.h>
#include <string.h>
#include <stdint.h>

int first_allocation = 0;
size_t heap_start_address = NULL;
size_t heap_end_adddress = NULL;
int hook_off = 0;
char *hippy_tag_line = {"HIPPY"};
char *hippy_tag_start = {"HIPPY-START"};
char *hippy_tag_end = {"HIPPY-END"};
int api_counter = 0; //this will be used later for the corrispondence between dumps and logs
char *envp[] = {0};
char *argv[] = {0};

char * tracer_child_binary = {"./tracer_child"};
char * dumper_binary = {"./readmem"};

/*
 Executed during the loading of this library
*/
__attribute__((constructor)) void tracer(){
  //well, nothing for now
}

/*
 Get the address of the original function inside the glibc
 exploiting the dlsym function.
*/
static ssize_t get_original(char *func_name)
{
    size_t real_func;
    real_func = dlsym(RTLD_NEXT, func_name); //dlsym is without heap allocations
    if (NULL == real_func) {
        fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
    }else{
      return real_func;
    }
}


// During the first allocation we have to retreive the
// addresses of the heap just allocated
static void handleFirstAllocation(){

  uint16_t pid2 = fork(); // we are going to create another process in order to avoid to dirty the heap of
                          // the current one that we are tracing with allocations derived from fopen and friends!

  if(pid2 == 0){  // ok son, do the dirty job!
    hook_off = 1;
    int err = execve(tracer_child_binary, argv, envp); // by using execve we have removed the LD_PRELOAD stuff inside the child
    exit(0);
  }else{
    wait();
  }
}

static void dump_heap(){

uint16_t pid = fork(); // fork is heap-allocation-free

if(pid == 0){
  hook_off = 1;
  execve(dumper_binary, argv, envp); // by using execve we have removed the LD_PRELOAD stuff inside the child
  exit(0);
}else{
  wait();
}
}

/*
 Malloc wrapper
*/
void *malloc(size_t size)
{
    api_counter++;
    void* (*real_malloc)(size_t) = NULL;

    if(real_malloc==NULL) {
         real_malloc = get_original("malloc");
    }

    if(hook_off == 1){
      return real_malloc(size);
    }

    void *ret_addr = NULL;
    ret_addr = real_malloc(size);
    size_t usable_size = malloc_usable_size(ret_addr);

    if(first_allocation == 0){
      handleFirstAllocation(); // We need to execute the first malloc in order to retreive the heap range
      first_allocation = 1; // erase the firts allocation flag
    }

    fprintf(stderr, "\n[%s]\n[%s]APIcounter: %zd\n[%s]malloc(%zd) = ", hippy_tag_start,hippy_tag_line,api_counter,hippy_tag_line,size);
    fprintf(stderr, "%p\n", ret_addr);
    fprintf(stderr,"[%s]usable size: (%zd|0x%zx)\n[%s]\n\n", hippy_tag_line,usable_size,usable_size,hippy_tag_end);

    dump_heap();
    return ret_addr;
}

/*
 Free wrapper
*/
void free(void* addr)
{
    api_counter++;
    void (*real_free)(void*) = NULL;

    if(real_free==NULL) {
        real_free = get_original("free");
    }

    if(hook_off == 1){
      real_free(addr);
      return;
    }

    fprintf(stderr, "\n[%s]\n[%s]APIcounter: %zd\n[%s]free(0x%zx)\n[%s]\n\n", hippy_tag_start,hippy_tag_line,api_counter,hippy_tag_line,addr,hippy_tag_end);
    real_free(addr);

    dump_heap();
    return;
}

/*
 Calloc wrapper
*/
void *calloc(size_t nmemb, size_t size)
{
    api_counter++;
    void* (*real_calloc)(size_t,size_t) = NULL;

    if(real_calloc==NULL) {
        real_calloc = get_original("calloc");
    }

    if(hook_off == 1){
      return real_calloc(nmemb,size);
    }

    void *ret_addr = NULL;
    ret_addr = real_calloc(nmemb,size);
    size_t usable_size = malloc_usable_size(ret_addr);

    if(first_allocation == 0){
      handleFirstAllocation();
      first_allocation = 1;
    }

    fprintf(stderr, "\n[%s]\n[%s]APIcounter: %zd\n[%s]calloc(%zd, %zd) = ",hippy_tag_start,hippy_tag_line,api_counter,hippy_tag_line, nmemb,size);
    fprintf(stderr, "%p\n", ret_addr);
    fprintf(stderr,"usable size: (%zd|0x%zx)\n[%s]\n\n", usable_size,usable_size,hippy_tag_end);

    dump_heap();
    return;
}

/*
 Realloc wrapper
*/
void *realloc(void* addr, size_t size)
{
    api_counter++;
    void* (*real_realloc)(void*,size_t) = NULL;

    if(real_realloc==NULL) {
        real_realloc = get_original("realloc");
    }

    if(hook_off == 1){
      return real_realloc(addr,size);
    }

    void *ret_addr = NULL;
    ret_addr = real_realloc(addr,size);
    size_t usable_size = malloc_usable_size(ret_addr);

    if(first_allocation == 0){
      handleFirstAllocation();
      first_allocation = 1;
    }

    fprintf(stderr, "\n[%s]\n[%s]APIcounter: %zd\n[%s]realloc(0x%zx, %zd) = ", hippy_tag_start,hippy_tag_line,api_counter,hippy_tag_line,addr,size);
    fprintf(stderr, "0x%zx\n", ret_addr);
    fprintf(stderr,"[%s]usable size: (%zd|0x%zx)\n", hippy_tag_line,usable_size,usable_size);

    // in this case the chunk has been moved in another position in memory
    // and the documentation says that the old chunk is freed, so we must register a free
    if(ret_addr !=  addr){
      fprintf(stderr, " [%s]free(0x%zx) ",hippy_tag_line,addr);
    }

    fprintf(stderr,"\n[%s]\n\n",hippy_tag_end);

    dump_heap();
    return;
}
