#include <stdio.h>
#include <stdlib.h>

int main(){

	unsigned int a = malloc(2312);
	unsigned int v = realloc(a,4000);

	malloc(2332);
}
