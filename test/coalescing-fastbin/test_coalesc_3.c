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
}
