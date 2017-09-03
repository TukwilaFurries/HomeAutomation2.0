#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <errno.h>
#include <string.h>
#include <pthread.h>

#define COM_PORT 15556
#define SERVER_IP_S "10.0.0.99"
#define PI_NAME "XXXXXXX PI"
#define ENTITY_NAME_LEN 64
#define MODULE_NAME_LEN 64
#define MAX_MODULES 1000
#define LOCAL_LISTEN_PORT 15557
#define RECV_BUFF_SIZE 1024
#define ACCEPT_PORT_NUM 15556
#define MAX_ENTITIES 1000 //change to max simultaneous connections **************************************************************************************

struct networkEntity {
	char name[ENTITY_NAME_LEN];
	char ip[15];
	int entityNumber;
	int entitySocket;
};

struct moduleEntry {
	char name[MODULE_NAME_LEN];
	int port;
	int gloabalID;
};

struct moduleEntry** moduleDirectory;

void* connectToServer();
void* runNetCom();
void* registerEntity();

void* acceptConnection();


int main(){

	printf("piController running \n");
	moduleDirectory = calloc(MAX_MODULES, sizeof(struct moduleEntry*));
	if (moduleDirectory == NULL)
	{
        printf("\n[piController]: Calloc for moduleDirectory unsuccessful \n");	
	}
	
	int socket1;
	socket1 = socket(AF_INET, SOCK_STREAM, 0);

	pthread_t acceptConnectionThread;
	pthread_create(&acceptConnectionThread, NULL, acceptConnection, NULL);

	//pthread_t localListenerThread;
	//pthread_create(&localListenerThread, NULL, runLocalListener, NULL);
	runNetCom();
	pthread_join(acceptConnectionThread,NULL);

	return 0;
}

void* runNetCom(){
	printf("running runNetCom\n");
	int comSocket = 0;
	
	connectToServer(&comSocket);
	registerEntity(&comSocket);

}

void* registerEntity(int* comSocketIn){
	int sent = send((*comSocketIn), PI_NAME, 13, 0);
	printf("sent name to server, sent %dbytes\n", sent);
	int entityNumber;
	recv((*comSocketIn), &entityNumber, sizeof(int), 0);
	printf("entityNumber received was: %d\n", entityNumber);
}

void* connectToServer(int* comSocketIn){
	printf("running connectToServer\n");
	char recvBuff[1024];
	memset(recvBuff, '0',sizeof(recvBuff));


    if(((*comSocketIn) = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("\n Error : Could not create socket \n");
        return;
    }

	struct sockaddr_in serverAddress; 
	memset(&serverAddress, '0', sizeof(serverAddress));
	serverAddress.sin_family = AF_INET;
	serverAddress.sin_port = htons(COM_PORT); 

	if(inet_pton(AF_INET, SERVER_IP_S, &serverAddress.sin_addr)<=0)
    {
        printf("\n inet_pton error occured\n");
        return;
    }

	if( connect((*comSocketIn), (struct sockaddr *)&serverAddress, sizeof(serverAddress)) < 0)
    {
       printf("\n Error : Connect Failed \n");
       return ;
    } 
	printf("connection established!\n");
}



void* runLocalTransmitter(){

}

void* acceptConnection(){
	printf("acceptConnection running\n");

	char recBuffer[RECV_BUFF_SIZE];
	memset(recBuffer, '0', sizeof(recBuffer));

	int acceptSocket = 0;
	struct sockaddr_in acceptAddress; 
	memset(&acceptAddress, '0', sizeof(acceptAddress));
	acceptSocket = socket(AF_INET, SOCK_STREAM, 0);
	acceptAddress.sin_family = AF_INET;
	acceptAddress.sin_addr.s_addr = htonl(INADDR_ANY);
	acceptAddress.sin_port = htons(ACCEPT_PORT_NUM);
	int true = 1;

	//flag OS to release port binding quickly after disconnect
	setsockopt(acceptSocket,SOL_SOCKET,SO_REUSEADDR,&true,sizeof(int));

	//bind socket and check sucess
	int toCheck = bind(acceptSocket, (struct sockaddr*)&acceptAddress, sizeof(acceptAddress));

	if(toCheck){
		printf("retrun was %d, errno was %s\n", toCheck, strerror(errno));
		return 0;
	}

	//repeatedly accept new connetions, adding their info to the directory
	while (1){
		int connectionSocket = 0;
		char sendBuff[1024];
		memset(sendBuff, '0', sizeof(sendBuff));
		listen(acceptSocket, MAX_ENTITIES);
		connectionSocket = accept(acceptSocket, (struct sockaddr*)NULL, NULL);
		if(connectionSocket<0){
			printf("error accepting connection\n");
		}


		else{
			printf("connection accepted from server!!! !\n");
			recv(connectionSocket, recBuffer, 8, 0);
			printf("[Local Listener]: message was:  %u %u \n", (*recBuffer), (*(recBuffer+4)));
			if((int)recBuffer[0] == 1){
				printf("First part of first message was 1; it was a status query\n");
				unsigned int toReply = 1;
				send(connectionSocket, &toReply, sizeof(toReply), 0);
			}
		}

	}
}


// to do 
// create thread safe date structure(s) for messageQueue between listeners and transmitters
