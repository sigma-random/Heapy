#include <stdlib.h>
#include <stdio.h>

/*
Coalescing of c with top chunk
*/
int main(){

unsigned int a = malloc(4);
unsigned int b = malloc(1000);
unsigned int c = malloc(1000);

free(c);
}
