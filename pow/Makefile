CFLAGS = -ggdb3 -Os -std=c99 -Wall -Wextra
CC = gcc

all: pow_test libpow.la

clean:
	rm -rf pow_test *.o *.lo *.a *.la .libs

.PHONY = all clean

%.lo: %.c
	libtool --mode=compile $(CC) $(CPPFLAGS) $(CFLAGS) -c $^

lib%.la: %.lo
	libtool --mode=link $(CC) -rpath $(PWD) $(LDFLAGS) $(LOADLIBES) $(LDLIBS) -o $@ $^

pow_test: pow_test.lo libpow.la
	libtool --mode=link $(CC) $(LDFLAGS) $(LOADLIBES) $(LDLIBS) -o $@ $^

libpow.la: pow.lo

