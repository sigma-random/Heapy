#include <stdlib.h>
#include <stdio.h>

/*
 after the last free(c) all the chunk are
 coalesced with the top chunk and c1 is allocated
 where 'a' was.

 Chunks in fastbins keep their inuse bit set, so they cannot
be consolidated with other free chunks. malloc_consolidate
releases all chunks in fastbins and consolidates them with
other free chunks.
*/


/*
   FASTBIN_CONSOLIDATION_THRESHOLD is the size of a chunk in free()
   that triggers automatic consolidation of possibly-surrounding
   fastbin chunks. This is a heuristic, so the exact value should not
   matter too much. It is defined at half the default trim threshold as a
   compromise heuristic to only attempt consolidation if it is likely
   to lead to trimming. However, it is not dynamically tunable, since
   consolidation reduces fragmentation surrounding large chunks even
   if trimming is not used.
 */


 /*
    FASTCHUNKS_BIT held in max_fast indicates that there are probably
    some fastbin chunks. It is set true on entering a chunk into any
    fastbin, and cleared only in malloc_consolidate.
    The truth value is inverted so that have_fastchunks will be true
    upon startup (since statics are zero-filled), simplifying
    initialization checks.
  */

/*
  malloc_consolidate is a specialized version of free() that tears
down chunks held in fastbins.  Free itself cannot be used for this
purpose since, among other things, it might place chunks back onto
fastbins.  So, instead, we need to use a minor variant of the same
code.
*/

int main(){

unsigned int a = malloc(100);
unsigned int b = malloc(4);
unsigned int c = malloc(100);
free(a);
free(b);
unsigned int c1 = malloc(4);
free(c1);
}
