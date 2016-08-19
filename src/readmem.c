#include "botutil.h"

#define BLOCK_SIGNALS 1

/*
Returns
	0: success,
	1: general failure,
	2: argument issue,
	3: attach failed, try again
*/
int main(int argc, char **argv)
{
	char start_heap[30];
	char end_heap[30];
	char s_pid[16];
	char heap_dump_filename[40] = {"./HeapDumps/heap_dump_"};
	char dump_index_string[10];
	int dump_index;
	struct stat st = {0};

	if (stat("./HeapDumps", &st) == -1) {
    mkdir("./HeapDumps", 0700);
	}

	FILE *heap_log = fopen("./heap_log","r");
	fscanf(heap_log,"%s",s_pid);
	fscanf(heap_log,"%s", start_heap);
	fscanf(heap_log,"%s", end_heap);
	fclose(heap_log);

	FILE *dump_log = fopen("./dump_log","r"); // take from here info about the name of the next dump
	if(dump_log == NULL){
		dump_index_string[0] = '1';
		dump_index = 1; // first time, dump_log hasn't been created yet
	}else{
		fscanf(dump_log,"%s",dump_index_string); //otherwise read the number from file
		dump_index = strtoul(dump_index_string,NULL,10);
		fclose(dump_log);
	}

	dump_index += 1; // increment the dump counter
	dump_log = fopen("./dump_log","w");
	fprintf(dump_log,"%d\n",dump_index); //update the dump_log
	fclose(dump_log);

	strcat(heap_dump_filename,dump_index_string); // compose the name of the dump

	pid_t const pid = atoi(s_pid);
	size_t heap_start_value = strtoull(start_heap, NULL, 16);
  size_t heap_end_value   = strtoull(end_heap, NULL, 16);
	size_t const size =  heap_end_value - heap_start_value;

	//fprintf(stderr,"Dumping from 0x%zx to 0x%zx, size: 0x%zx, process pid: %zd\n",heap_start_value,heap_end_value,size,pid);

	if (pid <= 0 || heap_start_value == ULONG_MAX || size == ULONG_MAX)
	{
		fprintf(stderr, "Invalid heap start address or size\n");
		return 2;
	}

	/* prepare for memory reads */

	char *mempath = NULL;
	verify(-1 != asprintf(&mempath, "/proc/%d/mem", pid));
	/* attach to target process */

	// block all signals, we can't blow up while waiting for the child to stop
	// or the child will freeze when it's SIGSTOP arrives and we don't clear it
#if defined(BLOCK_SIGNALS)
	sigset_t oldset;
	{
		sigset_t newset;
		verify(0 == sigfillset(&newset));
		// out of interest, we ensure the most likely signal is present
		assert(1 == sigismember(&newset, SIGINT));
		verify(0 == sigprocmask(SIG_BLOCK, &newset, &oldset));
	}
#endif

	// attach or exit with code 3
	if (0 != ptrace(PTRACE_ATTACH, pid, NULL, NULL))
	{
		int errattch = errno;
		// if ptrace() gives EPERM, it might be because another process
		// is already attached, there's no guarantee it's still attached by
		// the time we check so this is a best attempt to determine who is
		if (errattch == EPERM)
		{
			pid_t tracer = get_tracer_pid(pid);
			if (tracer != 0)
			{
				fprintf(stderr, "Process %d is currently attached\n", tracer);
				return 3;
			}
		}
		error(errattch == EPERM ? 3 : 1, errattch, "ptrace(PTRACE_ATTACH)");
	}

	//verify(0 == raise(SIGINT));

	wait_until_tracee_stops(pid);

#if defined(BLOCK_SIGNALS)
	verify(0 == sigprocmask(SIG_SETMASK, &oldset, NULL));
#endif

	int memfd = open(mempath, O_RDONLY);
	assert(memfd != -1);

	// read bytes from the tracee's memory
	char *p_addr;
	unsigned char a_byte_0;
	unsigned char a_byte_1;
	unsigned char a_byte_2;
	unsigned char a_byte_3;

	size_t ret = lseek64(memfd,heap_start_value,SEEK_SET);
	FILE * dump_file = fopen(heap_dump_filename, "a");
	int row_count = 3;
	for(p_addr = heap_start_value; p_addr < heap_end_value; p_addr+=4){
		  if(row_count == 3){
				fprintf(dump_file,"0x%zx ",p_addr);
			}
			read(memfd,&a_byte_0,1);
			read(memfd,&a_byte_1,1);
			read(memfd,&a_byte_2,1);
			read(memfd,&a_byte_3,1);
			fprintf(dump_file,"%02x",a_byte_3);
			fprintf(dump_file,"%02x",a_byte_2);
			fprintf(dump_file,"%02x",a_byte_1);
			fprintf(dump_file,"%02x",a_byte_0);

			if(row_count == 0){
				fprintf(dump_file,"\n");
				row_count = 3;
			}
			else{
				fprintf(dump_file," ");
				row_count--;
			}
	}

	fclose(dump_file);
	free(mempath);
  ptrace(PTRACE_DETACH, pid, NULL, NULL);

	return 0;
}
