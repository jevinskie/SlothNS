#include "pow.h"

uint32_t _rot(uint32_t x, int n)
{
    return (x<<n)|(x>>(32-n));
}

uint32_t _rand(uint32_t state[4])
{
  uint32_t e = state[0] - _rot(state[1], 27);
  state[0] = state[1] ^ _rot(state[2], 17);
  state[1] = state[2] + state[3];
  state[2] = state[3] + e;
  state[3] = e + state[0];
  return state[3];
}

void _rand_init(uint32_t state[4], uint32_t seed)
{
  int i;

  state[0] = 0xf1ea5eed;
  state[1] = state[2] = state[3] = seed;

  for (i = 0; i < 20; i++)
  {
    (void)_rand(state);
  }
}

// create the permutated table in D (0 -> 2^n-1)
void _gen_perm_table(pow_t *p)
{
    uint32_t i;
    uint32_t tmp;
    uint32_t rand_index;

    assert(p != NULL);

    // allocate the table
    p->perm_table = malloc(sizeof(uint32_t) * p->size);
    assert(p->perm_table != NULL);

    // fill the table with the elements of D
    for (i = 0; i < p->size; i++)
    {
        p->perm_table[i] = i;
    }

    // fischer yates shuffle
    for (i = p->size - 1; i >= 1; i--)
    {
        rand_index = _rand(p->rand) % (i + 1);
        tmp = p->perm_table[i];
        p->perm_table[i] = p->perm_table[rand_index];
        p->perm_table[rand_index] = tmp;
    }

    return;
}

// creates a PoW request to be sent to a client
pow_req_t *pow_create_req(pow_t *p, uint32_t l)
{
    pow_req_t *r;
    uint32_t xi;
    uint32_t check;
    uint32_t i;

    assert(p != NULL);

    assert(l > 0 && l <= 32);

    // allocate the request
    r = malloc(sizeof(pow_req_t));
    assert(r != NULL);

    // copy the parameters
    r->n = p->n;
    r->l = l;
    r->seed = p->seed;

    // allocate the v and w tables
    r->v = malloc(sizeof(uint32_t) * l);
    assert(r->v != NULL);

    r->w = malloc(sizeof(uint32_t) * l);
    assert(r->v != NULL);

    // fill v and w with random numbers within D
    for (i = 0; i < l; i++)
    {
        r->v[i] = _rand(p->rand) % p->size;
        r->w[i] = _rand(p->rand) % p->size;
    }
    
    // choose a random starting point in D
    r->x0 = _rand(p->rand) % p->size;

    xi = r->x0;
    check = r->x0;

    // walk a random path through D
    for (i = 0; i < l; i++)
    {
        if (_rand(p->rand) & 1)
        {
            xi = p->perm_table[(xi ^ r->v[i]) % p->size];
        }
        else
        {
            xi = p->perm_table[(xi ^ r->w[i]) % p->size];
        }

        // calculate the simple checksum
        check ^= xi << i;
    }

    r->check = check;

    return r;
}

// verifies the response to a given request
int pow_verify_res(pow_t *p, pow_req_t *req, pow_res_t *res)
{
    uint32_t xi;
    uint32_t check;
    uint32_t path;
    uint32_t i;

    assert(p != NULL);
    assert(req != NULL);
    assert(res != NULL);

    xi = req->x0;
    check = req->x0;

    path = res->path;

    for (i = 0; i < req->l; i++)
    {
        if (path & 1)
        {
            xi = p->perm_table[(xi ^ req->v[i]) % p->size];
        }
        else
        {
            xi = p->perm_table[(xi ^ req->w[i]) % p->size];
        }
        check ^= xi << i;
        path >>= 1;
    }

    if (check == req->check)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}

int64_t _solve_req(pow_t *p, pow_req_t *req, uint32_t x, uint32_t check, uint32_t level)
{
    uint32_t xv, xw;
    int64_t path;

    assert(p != NULL);
    assert(req != NULL);

    if (level < req->l)
    {
        xv = p->perm_table[(x ^ req->v[level]) % p->size];
        path = _solve_req(p, req, xv, check ^ (xv << level), level + 1);
        
        if (path >= 0)
        {
            path <<= 1;
            path |= 1;
            return path;
        }

        xw = p->perm_table[(x ^ req->w[level]) % p->size];
        path = _solve_req(p, req, xw, check ^ (xw << level), level + 1);
        
        if (path >= 0)
        {
            path <<= 1;
            return path;
        }
        
        return -1;
    }
    else if (req->check == check)
    {
        return 0;
    }
    else
    {
        return -1;
    }
}

pow_res_t *pow_create_res(pow_t *p, pow_req_t *req)
{
    pow_res_t *res;

    assert(p != NULL);
    assert(req != NULL);

    // allocate the response
    res = malloc(sizeof(pow_res_t));
    assert(res != NULL);

    // find the path that satisfies the request
    res->path = _solve_req(p, req, req->x0, req->x0, 0);

    return res;
}

void pow_destroy_res(pow_res_t *r)
{
    assert(r != NULL);
    free(r);
}


void pow_destroy_req(pow_req_t *r)
{
    assert(r != NULL);
    free(r->v);
    free(r->w);
    free(r);
}

pow_t *pow_create(uint32_t n, uint32_t seed)
{
    pow_t *p;

    p = malloc(sizeof(pow_t));
    assert(p != NULL);

    assert(n > 0 && n <= 32);

    p->seed = seed;
    _rand_init(p->rand, seed);
    p->n = n;
    p->size = 1<<n;

    _gen_perm_table(p);

    return p;
}

void pow_destroy(pow_t *p)
{
    assert(p != NULL);
    free(p->perm_table);
    free(p);
}

