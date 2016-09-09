#include <stdlib.h>
#include <stdio.h>

/*
No coalescing
*/
int main(){


unsigned int b = malloc(4);
unsigned int d = malloc(4);
free(b);
free(d);

}
