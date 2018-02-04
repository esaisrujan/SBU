
pbproxy : pbproxy.o
	gcc -o pbproxy pbproxy.o -lcrypto -lpthread
pbproxy.o : pbproxy.c
	gcc -c pbproxy.c
clean : 
	rm pbproxy pbproxy.o
