#include <stdlib.h>
#include <stdio.h>

/*
 No coalescing at all
*/
int main(){

unsigned int a = malloc(4);
unsigned int b = malloc(4);
unsigned int c = malloc(4);
unsigned int t = malloc(100);
unsigned int d = malloc(4);
unsigned int e = malloc(4);
unsigned int f = malloc(4);
unsigned int g = malloc(4);
free(a);
free(b);
free(c);
free(d);
free(e);
free(f);
free(t);
unsigned int l = malloc(60);
unsigned int j = malloc(36);
//realloc(j,1000);
unsigned int p = malloc(2000);
unsigned int k = malloc(10);
free(j);
//unsigned int h = realloc(p,4000);
//free(h);
unsigned int ooo = malloc(55);
 malloc(100);
  malloc(100);
   malloc(100);
    malloc(100);
     malloc(100);
      malloc(100);
       malloc(100);
        malloc(100);
         malloc(100);
          malloc(100);
           malloc(100);
            malloc(100);
             malloc(100);
              malloc(100);
               malloc(100);
                malloc(100);
}
