/*
 http://elinux.org/images/b/b5/Elc2013_Kobayashi.pdf
 COMPILE: gcc -m32 -shared -fPIC -o simple_tracer_32.so simpletracer.c -ldl
 RUN: LD_PRELOAD=./simple_tracer_32.so ./trace_me_32
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
char *hippy_tag = {"HIPPY"};
int api_counter = 0; //this will be used later for the corrispondence between dumps and logs
char *envp[] = {0};
char *argv[] = {0};

char * tracer_child_binary = {"./tracer_child_32"};
char * dumper_binary = {"./readmem_32"};

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

/*
 Malloc wrapper
*/
void *malloc(size_t size)
{
    void* (*real_malloc)(size_t) = NULL;

    if(real_malloc==NULL) {
         real_malloc = get_original("malloc");
    }

    void *ret_addr = NULL;
    fprintf(stderr, "\n[%s]\nAPIcounter: %zd\nmalloc(%zd) = ", hippy_tag,api_counter,size);
    ret_addr = real_malloc(size);
    fprintf(stderr, "%p\n", ret_addr);
    size_t usable_size = malloc_usable_size(ret_addr);
    fprintf(stderr,"usable size: (%zd|0x%zx)\n[%s]\n\n", usable_size,usable_size,hippy_tag);

    if(first_allocation == 0){
      handleFirstAllocation();
      first_allocation = 1;
    }

    api_counter++;

    return ret_addr;
}

/*
 Free wrapper
*/
void free(void* addr)
{
    void (*real_free)(void*) = NULL;

    if(real_free==NULL) {
        real_free = get_original("free");
    }

    api_counter++;
    return;
}

/*
 Calloc wrapper
*/
void *calloc(size_t nmemb, size_t size)
{
    void* (*real_calloc)(size_t,size_t) = NULL;

    if(real_calloc==NULL) {
        real_calloc = get_original("calloc");
    }

    void *ret_addr = NULL;
    fprintf(stderr, "\n[%s]\nAPIcounter: %zd\ncalloc(%zd, %zd) = ",hippy_tag,api_counter, nmemb,size);
    ret_addr = real_calloc(nmemb,size);
    fprintf(stderr, "%p\n", ret_addr);
    size_t usable_size = malloc_usable_size(ret_addr);
    fprintf(stderr,"usable size: (%zd|0x%zx)\n[%s]\n\n", usable_size,usable_size,hippy_tag);

    if(first_allocation == 0){
      handleFirstAllocation();
      first_allocation = 1;
    }

    api_counter++;
    return;
}

/*
 Realloc wrapper
*/
void *realloc(void* addr, size_t size)
{
    void* (*real_realloc)(void*,size_t) = NULL;

    if(real_realloc==NULL) {
        real_realloc = get_original("realloc");
    }

    void *ret_addr = NULL;
    fprintf(stderr, "\n[%s]\nAPIcounter: %zd\nrealloc(0x%zx, %zd) = ", hippy_tag,api_counter,addr,size);
    ret_addr = real_realloc(addr,size);
    fprintf(stderr, "%p\n", ret_addr);
    size_t usable_size = malloc_usable_size(ret_addr);
    fprintf(stderr,"usable size: (%zd|0x%zx)\n[%s]\n\n", usable_size,usable_size,hippy_tag);

    if(first_allocation == 0){
      handleFirstAllocation();
      first_allocation = 1;
    }

    api_counter++;
    return;
}
