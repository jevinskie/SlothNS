
#include <stdio.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <time.h>
#include "workfct.h"



// functions

int main ()
{
  int sizeT = POW2(24); 	// n, as denoted by Coelho et al.
  int depth = 20; 	// l, as denoted by Coelho et al.
  int seed = 528;
    clock_t cstart, cend;
  double t_gen, t_req, t_res, t_ver;

  int *T = (int *)malloc(sizeof(int)*sizeT);

  int time0 = time(NULL);

  cstart = clock();

  int i, j;
  for(i = 0; i < sizeT; i++)	// initialize permutation table to each index holding the value of the index
  { 
  	T[i] = i;
  	//printf("%d\n", T[i]);
  }
  //printf("\n\n"); */
  
  gen_permTable(T, sizeT, seed);  // generate the permutation table, which can be used by both the server and client
  
  cend = clock();

  t_gen = (cend - cstart)/(double)CLOCKS_PER_SEC;

  // generate the challenge sequence
  int *v;
  int *w;
  myReq server_chal;

  
  int timeT = time(NULL);
  cstart = clock();
  
  server_chal = gen_req(sizeT, depth, T, seed, v, w);
  free(v);
  free(w);

  cend = clock();

  t_req = (cend - cstart)/(double)CLOCKS_PER_SEC;
  
  int time1 = time(NULL);

  cstart = clock();
  
  int resp = solve_req(server_chal, server_chal.init_cond, server_chal.init_cond, 0, T);  
  
  cend = clock();

  t_res = (cend - cstart)/(double)CLOCKS_PER_SEC;

  cstart = clock();

  int verif = verify_req(server_chal, resp, T);
  
  cend = clock();

  int time2 = time(NULL);
  
  t_ver = (cend - cstart)/(double)CLOCKS_PER_SEC;

  
  printf("Verification results is %d\n", verif);
  
  printf("Total time was %lg, with time spent on solving %lg\ngen table: %lg\ngen req: %lg\nver: %lg\n", t_gen+t_req+t_res+t_ver, t_res, t_gen, t_req, t_ver);
  
  for(i = 0; i < sizeT; i++)
  { 
  	//printf("%x\t%x\n", i, T[i]);
  }
  //printf("\n"); 
  
  free(T);


} // main()

