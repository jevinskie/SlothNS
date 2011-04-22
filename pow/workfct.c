#include "workfct.h"

void gen_permTable(int *T, int size, int seed)
{
  if(T == NULL)
  {
  	printf("ERROR, T not allocated");
  	return;
  }
  
  int i;
  int random_no;
  int aux;
  
  srand(seed);
  
  for(i = 0; i < size; i++)
  {
  	random_no = rand() % size;
  	
  	// swap T[i] and T[random_no]
  	aux = T[i];
  	T[i] = T[random_no];
  	T[random_no] = aux;
  	
   } 

}


myReq gen_req(int size, int depth, int *T, int seed, int *v, int *w)
{
  v = malloc(sizeof(int) * depth);
  w = malloc(sizeof(int) * depth);
  
  int i,j;
  myReq serv_req;
  
  serv_req.size = size;
  serv_req.depth = depth;
  serv_req.seed = seed;

  srand( time(NULL) );

  int x0 = rand() % size;	// generate x0;
  serv_req.init_cond = x0;

  // first, generate auxiliary arrays v and w, with "depth" distinct elements in each
  int *seen = calloc(1, sizeof(int) * size);
  
  for(i = 0; i < depth; i++)	// depth of tree is same as number of applications of mangling fct
  {
  	// generate two random v, w values, make sure they are unique
  	int r;
  	
  	do {
      		r = rand() % size;
    	} while (seen[r]);
    
    	seen[r] = 1;
    	v[i] = r;

  	do {
      		r = rand() % size;
    	} while (seen[r]);
    
    	seen[r] = 1;
    	w[i] = r;
  }
   
  for(i = 0; i < depth; i++)	
  {
	//printf("%x\t%x\n", v[i], w[i]);
  }
  
  //printf("\n"); 
  free(seen);
  
  serv_req.v = v;
  serv_req.w = w;
  
  int chksum = x0;	// first term of checksum is rot(x0, 0) = x0
  int x_current = x0;
  int b_current;
  
  //printf("%x\t%x\n", x0, chksum);
    
  for(i = 0; i < depth; i++)
  {
  	b_current = rand() % 2;
  	//printf("%x\t",b_current);
  	if(b_current)
  	{
  		x_current = T[(x_current)^(v[i])];
  	}
  	else
  	{
  		x_current = T[(x_current)^(w[i])];
  	}
  	
  	//printf("%x\t",x_current);
  	
  	int shft = i % ( sizeof(int) * 8 );
  	chksum = (chksum)^( ( x_current>>(shft+1) )|( x_current<<(sizeof(int)*8-shft-1) ) );
  	
  	//printf("%x\n",chksum);
  }
  
  //printf("\n");
  serv_req.c = chksum;
  
  return serv_req;

}



int solve_req(myReq r, int chk_sum, int x, int level, int *T)
{
  //printf("Reached level %d of recurssion; ", level); 

  if(level < r.depth)  // intermediate nodes, call right and left node recursively
  {
        int x_v = T[( x )^( r.v[level] )];
        int i = level % ( sizeof(int) * 8 );	// shift index for checksum
  	int v_child = solve_req(r, (chk_sum)^( ( x_v>>(i+1) )|( x_v<<(sizeof(int)*8-i-1) ) ), x_v, level+1, T);
  	
  	if(v_child >= 0)	// if a path was found along the v_child, add 1 to binary path and return value
  	{
  		v_child = (v_child << 1) | 1;
  		//printf("Added 1 to path, returning\n");
  		return v_child;
  	}
  	// implicitly, no valid path was found by v_child, call w_child
  	
  	int x_w = T[( x )^( r.w[level] )];
  	int w_child = solve_req(r, (chk_sum)^( ( x_w>>(i+1) )|( x_w<<(sizeof(int)*8-i-1) ) ), x_w, level+1, T);
  		
  	if(w_child >= 0)	// if a path was found along w_child, add 0 to binary path and return value
  	{
  		w_child = w_child << 1;
  		//printf("Added 0 to path, returning\n");
  		return w_child;
  	}	
  	
  	// if function reaches this point, neither children returned valid binery path, return -1
  	//printf("Found no path, returning\n");
  	return -1;
  }
  
  // if function reaches past this point, it means it's at level "depth"
  if( r.c == chk_sum)
  {
  	//printf("Valid leaf node, returning 0\n");
  	return 0;
  }
  
  //printf("Invalid leaf node, retuning -1\n");
  return -1;	
}


int verify_req(myReq r, int path, int *T)
{


  int *v = r.v;
  int *w = r.w;
  
  int i;
 
  int size = r.size;
  int depth = r.depth;
  int seed = r.seed;

  int x0 = r.init_cond;

  int chksum = x0;	// first term of checksum is rot(x0, 0) = x0
  int x_current = x0;
  int b_current;
  
  for(i = 0; i < depth; i++)
  {
  	b_current = path % 2;
  	path = path / 2;
  	//printf("%x\t",b_current);
  	if(b_current)
  	{
  		x_current = T[(x_current)^(v[i])];
  	}
  	else
  	{
  		x_current = T[(x_current)^(w[i])];
  	}
  	
  	//printf("%x\t",x_current);
  	
  	chksum = (chksum)^( ( x_current>>(i+1) )|( x_current<<(sizeof(int)*8-i-1) ) );
  	
  	//printf("%x\n",chksum);
  }
  
  if (r.c == chksum)
  {
  	printf("Challenge passed!\n");
  	return 1;
  }
  
  return 0;

}

