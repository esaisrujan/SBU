#include<fcntl.h>
#include <resolv.h>  
 #include <string.h>  
 #include <pthread.h>  
 #include<unistd.h>  
#include <arpa/inet.h>
#include<stdlib.h>
#include <openssl/aes.h>
#include <openssl/rand.h> 
#include <openssl/hmac.h>
#include <openssl/buffer.h>
#include<netinet/in.h>
#include<netdb.h>
 

int sd=0,len,i=-1;
char *keyp=NULL;
unsigned char iv[AES_BLOCK_SIZE];  
struct ctr_state 
{ 
    unsigned char ivec[AES_BLOCK_SIZE];  
    unsigned int num; 
    unsigned char ecount[AES_BLOCK_SIZE]; 
};       
void init_ctr(struct ctr_state *state, const unsigned char iv[16])
{        
    state->num = 0;
    memset(state->ecount, 0, 16);
    memcpy(state->ivec, iv, 16);
}

void crypt_message(char* src, char* dst, unsigned int src_len, const AES_KEY* key, const char* iv)
{   
   struct ctr_state state;
   init_ctr(&state, iv);
    AES_ctr128_encrypt(src, dst, src_len, key, state.ivec, state.ecount, &state.num);
}
void *runSocket_server(void *vargp)
{	int client_fd =(int)(intptr_t)vargp;
          int bytes=0,len=0,rbytes;
	  char buffer[65000],cipher[65000];

		//bzero(iv,sizeof(iv));
					 while(1)
					{
						bytes=read(client_fd,iv,sizeof(iv));
						if(bytes>0)
							break;
					}
		      
			while(1)
			{ 		bzero(buffer,sizeof(buffer));
                			bzero(cipher,sizeof(cipher));
					
					
				rbytes=0;
				while((bytes=read(client_fd,cipher,sizeof(cipher)))>0)
				{   
					AES_KEY key;
                 			AES_set_encrypt_key(keyp, 128, &key);
                			len= bytes;
               				crypt_message(( char*)cipher, (char*)buffer, len, &key, iv);
                		
					//write(1,buffer,bytes);
					if(write(sd,buffer,bytes)>0);
					write(1,"\nwritten to server",18);
				
				}

			
				 bzero(buffer,sizeof(buffer));
                 		bzero(cipher,sizeof(cipher));
				
				while((bytes=read(sd,buffer,sizeof(buffer)))>0)
				{      
				      

										AES_KEY key;
                                        AES_set_encrypt_key(keyp, 128, &key);
                                        len=bytes;
                                        crypt_message(( char*)buffer, (char*)cipher, len, &key, iv);
                                        
										//write(1,buffer,bytes);
										if(write(client_fd,cipher,bytes)>0)
											write(1,"\nwritten to client",18);
				}
				
			}

}
void *runSocket_client(void *vargp)
 {
   int servd =(int)(intptr_t)vargp;
   int bytes=0,l=0,rbytes=0;
   char buffer[65000],cipher[65000];
  
         while(1)
{

		 memset(&buffer,'\0',sizeof(buffer));
                  memset(&cipher,'\0',sizeof(cipher));
			
	         bytes=0;
                 while((bytes=read(servd,cipher,sizeof(cipher)))>0)
                                {
                                      
                                       AES_KEY key;
                                        AES_set_encrypt_key(keyp, 128, &key);
                                        len= bytes;
                                        crypt_message(( char*)cipher, (char*)buffer, len, &key, iv);
	                		write(1,buffer,bytes);
   	                        }   
				  
 }    
}
 
 int main(int argc,char **argv)  
 {  
	 int client_fd,opt,bytes=0,wbytes=0,rbytes=0,w=0;//len;  
      char buffer[65000],cipher[65000];
      char *keyf=NULL;
	char *servaddr=NULL;
      int lport,servport;  
      int fd = 0,f=0 ;  
      int server=0;
     
     pthread_t ctid,stid[500];
     
      while ((opt = getopt (argc, argv, "k:l:")) != -1)
  {
    switch (opt)
    {
      case 'k':
                keyf = optarg;
                break;
      case 'l':
                server=1;
                lport = atoi(optarg);
                struct sockaddr_in server_sd;         
                fd = socket(AF_INET, SOCK_STREAM, 0);
		fcntl(fd, F_SETFL, O_NONBLOCK);
		
                 memset(&server_sd, 0, sizeof(server_sd));
                // set socket variables
                server_sd.sin_family = AF_INET;
                server_sd.sin_port = htons(lport);
                server_sd.sin_addr.s_addr = INADDR_ANY;
                // bind socket to the port
                if( bind(fd, (struct sockaddr*)&server_sd,sizeof(server_sd))<0)
		{
			fprintf(stderr,"proxy bind failed\n");
		}
		
                 // start listening at the given port for new connection requests
                 listen(fd, SOMAXCONN);
                 

    }
  }

FILE *fp;
char fbuff[65000];
char *ip=NULL;
fp= fopen(keyf,"r");
if(fp==NULL){fprintf(stderr,"key file open error\n");}

fgets(fbuff,sizeof(fbuff),(FILE*)fp);
fbuff[strlen(fbuff)-1]='\0';

keyp = fbuff;

if(argv[optind]!=NULL)
	{   servaddr = argv[optind];
	
	}
if(argv[optind+1]!=NULL)
	{ servport = atoi(argv[optind+1]);
	
	}
 
      struct sockaddr_in serv_sd;
      // create a socket  
     sd = socket(AF_INET, SOCK_STREAM, 0);
    
      memset(&serv_sd, 0, sizeof(serv_sd));
	struct hostent *ht=gethostbyname(servaddr);  
	
      // set socket variables  
      serv_sd.sin_family = AF_INET;  
      serv_sd.sin_port = htons(servport); 
	memcpy(&serv_sd.sin_addr.s_addr, ht->h_addr, ht->h_length); 
	
      //serv_sd.sin_addr.s_addr = inet_addr(servaddr);  //Uncomment this when servaddr is ip
      
      if((connect(sd, (struct sockaddr *)&serv_sd, sizeof(serv_sd))<0))
           {
                fprintf(stderr,"connect failed");
           }
		fcntl(sd, F_SETFL, O_NONBLOCK);
      if(server ==0 )
	{ 
      if(!RAND_bytes(iv, AES_BLOCK_SIZE))
           {
                fprintf(stderr, "Could not create random bytes.");
                exit(1);
            }
        if(write(sd,iv,sizeof(iv))>0)
		//write(1,"written iv",10);

if( pthread_create(&ctid, NULL, runSocket_client, (void *)(intptr_t)sd))
                        fprintf(stderr,"failed to create thread");

               // else printf("created\n");
	}

      while(1)  
      {  
           // accept any incoming connection 
           if(server == 1)
	{
           client_fd = accept(fd, (struct sockaddr*)NULL ,NULL);
	   fcntl(client_fd, F_SETFL, O_NONBLOCK);	
           if(client_fd > 0)

              {       
			if(i>-1)
	                {	close(sd);
				sd = socket(AF_INET, SOCK_STREAM, 0);
    
				      memset(&serv_sd, 0, sizeof(serv_sd));
					struct hostent *ht=gethostbyname(servaddr);  
	
				      // set socket variables  
				      serv_sd.sin_family = AF_INET;  
				      serv_sd.sin_port = htons(servport); 
					memcpy(&serv_sd.sin_addr.s_addr, ht->h_addr, ht->h_length); 
	
				      //serv_sd.sin_addr.s_addr = inet_addr(servaddr);  //Uncomment this when servaddr is ip
				      
				      if((connect(sd, (struct sockaddr *)&serv_sd, sizeof(serv_sd))<0))
					   {
						fprintf(stderr,"connect failed");
					   }
						fcntl(sd, F_SETFL, O_NONBLOCK);
				
				pthread_cancel(stid[i]);
				bzero(iv,sizeof(iv));
			}
		i++;
		if( pthread_create(&stid[i], NULL, runSocket_server, (void *)(intptr_t)client_fd)<0)
		
		fprintf(stderr,"pthread creation failed");
			//else
			//write(1,"success",10);     
			
		  
		             
						   
           }  
  }
           else if( server == 0)
           {
		
                bzero(buffer,sizeof(buffer));
		bzero(cipher,sizeof(cipher));
		
                while((rbytes=read(0,buffer,sizeof(buffer)))>0)
		{
 		AES_KEY key;
		 AES_set_encrypt_key(keyp, 128, &key);
		len= rbytes;
		crypt_message((char*)buffer, (char*)cipher, len, &key, iv);
		
                write(sd,cipher,rbytes);
		}          
          
      }
}  
       
      return 0;  
 } 
