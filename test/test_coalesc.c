#include <stdlib.h>
#include <stdio.h>

int main(){

	
	unsigned int b = malloc(1000);
	unsigned int c = malloc(4);
	unsigned int a = malloc(1000);
	free(b);
	free(c);
	free(a);
        unsigned int d = malloc(100);


}