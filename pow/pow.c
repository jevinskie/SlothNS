#include "pow.h"

void gen_perm_table(pow_t *p)
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
        if (jrand48(p->rand) % 2)
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

void pow_destroy_req(pow_req_t *r)
{
    free(r->v);
    free(r->w);
    free(r);
}

pow_t *pow_create(size_t n, size_t l, uint64_t seed)
{
    pow_t *p = malloc(sizeof(pow_t));
    assert(p != NULL);

    memcpy(p->rand, &seed, sizeof(p->rand));
    memcpy(p->seed, &seed, sizeof(p->seed));
    p->n = n;
    p->size = 1<<n;
    p->l = l;

    gen_perm_table(p);

    return p;
}

void pow_destroy(pow_t *p)
{
    free(p->perm_table);
    free(p);
}

