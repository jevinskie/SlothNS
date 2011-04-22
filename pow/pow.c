#include "pow.h"

void _gen_perm_table(pow_t *p)
{
    uint32_t i;
    uint32_t tmp;
    uint32_t rand_index;

    assert(p != NULL);

    p->perm_table = malloc(sizeof(uint32_t) * p->size);
    assert(p->perm_table != NULL);

    for (i = 0; i < p->size; i++)
    {
        p->perm_table[i] = i;
    }

    for (i = 0; i < p->size; i++)
    {
        rand_index = jrand48(p->rand);
        tmp = p->perm_table[i];
        p->perm_table[i] = p->perm_table[rand_index % p->size];
        p->perm_table[rand_index % p->size] = tmp;
    }

    return;
}

pow_req_t *pow_create_req(pow_t *p)
{
    pow_req_t *r;
    uint32_t x0, xi;
    uint32_t i;
    uint32_t check;

    assert(p != NULL);

    r = malloc(sizeof(pow_req_t));
    assert(r != NULL);

    r->n = p->n;
    r->l = p->l;
    memcpy(r->seed, p->seed, sizeof(r->seed));

    r->v = malloc(sizeof(uint32_t) * p->l);
    assert(r->v != NULL);

    r->w = malloc(sizeof(uint32_t) * p->l);
    assert(r->v != NULL);

    x0 = jrand48(p->rand) % p->size;
    r->x0 = x0;

    for (i = 0; i < p->l; i++)
    {
        r->v[i] = jrand48(p->rand);
        r->w[i] = jrand48(p->rand);
    }

    xi = x0;
    check = x0;

    for (i = 0; i < p->l; i++)
    {
        if (jrand48(p->rand) & 1)
        {
            xi = p->perm_table[(xi ^ r->v[i]) % p->size];
        }
        else
        {
            xi = p->perm_table[(xi ^ r->w[i]) % p->size];
        }
        check ^= xi << i;
    }

    r->check = check;

    return r;
}

<<<<<<< HEAD
void pow_destroy_req(pow_req_t *r)
{
=======
int pow_verify_res(pow_t *p, pow_req_t *req, pow_res_t *res)
{
    uint32_t x0, xi;
    uint32_t i;
    uint32_t check;
    uint32_t path;

    assert(p != NULL);
    assert(req != NULL);
    assert(res != NULL);

    check = x0;
    xi = x0;

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

int64_t _solve_req(pow_t *p, pow_req_t *req, uint32_t x, uint32_t check, int level)
{
    uint32_t xv, xw;
    int64_t v_child, w_child;

    assert(p != NULL);
    assert(req != NULL);

    if (level < req->l)
    {
        xv = p->perm_table[(x ^ req->v[level]) % p->size];
        v_child = _solve_req(p, req, xv, check ^ (xv << level), level + 1);
        if (v_child >= 0)
        {
            v_child <<= 1;
            v_child |= 1;
            return v_child;
        }
        xw = p->perm_table[(x ^ req->w[level]) % p->size];
        w_child = _solve_req(p, req, xw, check ^ (xw << level), level + 1);
        if (w_child >= 0)
        {
            w_child <<= 1;
            return w_child;
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

    res = malloc(sizeof(pow_res_t));
    assert(res != NULL);

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

pow_t *pow_create(size_t n, size_t l, uint64_t seed)
{
    pow_t *p;

    p = malloc(sizeof(pow_t));
    assert(p != NULL);

    memcpy(p->rand, &seed, sizeof(p->rand));
    memcpy(p->seed, &seed, sizeof(p->seed));
    p->n = n;
    p->size = 1<<n;
    p->l = l;

    _gen_perm_table(p);

    return p;
}

void pow_destroy(pow_t *p)
{
    assert(p != NULL);
    free(p->perm_table);
    free(p);
}

