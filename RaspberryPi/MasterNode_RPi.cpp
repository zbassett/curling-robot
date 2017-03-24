
  
#include "RF24Mesh/RF24Mesh.h"  
#include <RF24/RF24.h>
#include <RF24Network/RF24Network.h>
#include <sys/time.h>
#include <sys/timeb.h>


#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <string>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <iostream>
#include <chrono>


//RF24 radio(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ);  
RF24 radio(17,0);
RF24Network network(radio);
RF24Mesh mesh(radio,network);

uint32_t displayTimer = 0;

//Used to synch time between nodes.  They'll each send their millis() value to master every second.
uint32_t slaveNodeTime[7];
uint32_t masterNodeTime[7];
uint32_t masterTeeTime = 0;

uint32_t voltage[7];

//Node 0: Master
//Node 1: Hack 1
//Node 2: Tee 1 (includes temp & humidity)
//Node 3: Hog 1
//Node 4: Hog 2
//Node 5: Tee 2
//Node 6: Hack 2

unsigned long tripInfo[9];
    // 1: teeTripMasterTime
    // 2: teeTripDuration
    // 3: hogTripMasterTime
    // 4: hogTripDuration
    // 5: tempC
    // 6: humidity
    // 7: distance1
    // 8: distance2
	
unsigned long secondaryPing;

bool teeTripped;
bool hogTripped;
int nodeID;

//variables to store temp and humidity.
int temp = 0;
int hum = 0;

//Function to return current time in milliseconds.  This allows us to sync with the Arduino times received.
//unsigned long long current_timestamp() {
//  	using namespace std::chrono;
//  	system_clock::time_point tp = system_clock::now();
//  	system_clock::duration dtn = tp.time_since_epoch();
//  	std::uint64_t timeVar = dtn.count();

//    return time(0);
//}

unsigned  long millis1(){
  struct timespec tt;
  clock_gettime(CLOCK_MONOTONIC, &tt);
  return  tt.tv_nsec/1000000+ tt.tv_sec * 1000;
  }

// int getMilliCount(){
	// timeb tb;
	// ftime(tb);
	// int nCount = tb.millitm + (tb.time & 0xfffff) * 1000;
	// return nCount;
//}

//Function to send commands to the slave nodes.
void SlaveCommand(int SlaveNode, int TargetMode) {
  int NodeAddr=0;
  //Get Node address from ID.
    for (int i = 0; i < mesh.addrListTop; i++) {
      if (mesh.addrList[i].nodeID == SlaveNode) {
        NodeAddr = mesh.addrList[i].address;
      }
    }
  RF24NetworkHeader header(NodeAddr); //Constructing a header   mesh.addrList[SlaveNode].address
  if((network.write(header, &TargetMode, sizeof(TargetMode))) == 1) {
	  printf("Send OK\n");
  }
  else {
	  printf("Send Fail\n"); 
  }
}

//Celsius to Fahrenheit conversion
double Fahrenheit(double celsius) {
 return 1.8 * celsius + 32;
}

//Speed of Sound calculation (m/s)
double SoS(double temperature, double humidity){
 return 331.4 + (0.606 * temperature) + (0.0124 * humidity);
}

//error handler for SendDataToServer
void error(const char *msg)
{
    perror(msg);
    exit(0);
}

//Transmit collected data to python server
int SendDataToServer(const char HostName[], int PortNum, char* MsgTxt){
	//printf("%s\n",MsgTxt);
	
    int sockfd, n;
    struct sockaddr_in serv_addr;
    struct hostent *server;

    char buffer[256];
    /* if (argc < 3) {
       fprintf(stderr,"usage %s hostname port\n", argv[0]);
       exit(0);
    } */
    //portno = atoi(argv[2]);
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");
    server = gethostbyname(HostName);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host\n");
        exit(0);
    }
    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
         (char *)&serv_addr.sin_addr.s_addr,
         server->h_length);
    serv_addr.sin_port = htons(PortNum);
    if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
        error("ERROR connecting");
    //printf("Please enter the message: ");
    
	
	bzero(buffer,256);
	//buffer = MsgTxt;
	//buffer = MsgTxt;
    //fgets(buffer,255,MsgTxt[255]);
	/* printf("%d",strlen(MsgTxt));
	printf("\n"); */
	
	;

    n = write(sockfd,MsgTxt,strlen(MsgTxt));
    if (n < 0) 
         error("ERROR writing to socket");
    bzero(buffer,256);
    n = read(sockfd,buffer,255);
    if (n < 0) 
         error("ERROR reading from socket");
    printf("%s\n",buffer);
    close(sockfd);
    return 0;
}

//main loop
int main(int argc, char** argv) {
  
  // Set the nodeID to 0 for the master node
  mesh.setNodeID(0);
  // Connect to the mesh
  printf("start\n");
  mesh.begin();
  radio.printDetails();
  radio.setPALevel(RF24_PA_MAX);  //options: RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH and RF24_PA_MAX



while(1)
{
  
  // Call network.update as usual to keep the network updated
  mesh.update();

  // In addition, keep the 'DHCP service' running on the master node so addresses will
  // be assigned to the sensor nodes
  mesh.DHCP();
  
  
  // Check for incoming data from the sensors
  while(network.available()){
//    printf("rcv\n");
    RF24NetworkHeader header;
    network.peek(header);
	
	//Get Node ID from address.
    for (int i = 0; i < mesh.addrListTop; i++) {
      if (mesh.addrList[i].address == header.from_node) {
        nodeID = mesh.addrList[i].nodeID;
        //printf("%d", nodeID);
		//printf(" - ");
      }
    }
    
    uint32_t dat=0;
	char txt[16];
    unsigned char uid[4];
    unsigned long trip[6];

	
    switch(header.type){
      // Display the incoming millis() values from the sensor nodes
    case 'M': //Calibration transmission from each node.
		masterNodeTime[nodeID] = millis1();  //determine local time.
                delay(1);



		network.read(header,&dat,sizeof(dat));
		
		slaveNodeTime[nodeID] = dat;  //determine slave time.
		
		//printf("Rcv %u from 0%o\n",dat,header.from_node);
		printf("Node: ");
		printf("%d", nodeID);
		printf("  MasterTime: ");
		printf("%u",masterNodeTime[nodeID]);
		printf("  SlaveTime: ");
		printf("%u",slaveNodeTime[nodeID]);
		printf("  Adjustment: ");
		printf("%lu\n",((long)masterNodeTime[nodeID] - (long)slaveNodeTime[nodeID]));
		 break;
	case 'V': //Voltage transmission from each node.
		//masterNodeTime[nodeID] = millis();  //determine local time.
		network.read(header,&dat,sizeof(dat));
		
		voltage[nodeID] = dat;  //determine slave time.
		
		//printf("Rcv %u from 0%o\n",dat,header.from_node);
		printf("Node: ");
		printf("%d", nodeID);
		printf("  Voltage: ");
		printf("%u\n",voltage[nodeID]);
		 break;
	case 'P': //Secondary ping time for direction information
		network.read(header,&dat,sizeof(dat));
		
		secondaryPing = dat;
		
		printf("Node: ");
		printf("%d", nodeID);
		printf("  SecondaryPing: ");
		printf("%lu\n",secondaryPing);
		
		char TripInfoString[30];
		char trip2Info[100];
		strcpy(trip2Info,"shot2:");
		sprintf(TripInfoString,"%lu",secondaryPing);
		strcat(trip2Info,TripInfoString);
		
		SendDataToServer("localhost",10000,trip2Info);
		
		
		break;
	case 'S': //String
        network.read(header,&txt,17); 
        printf("Node: ");
		printf("%d", nodeID);
		printf(" Length: ");
		printf("%d",strlen(txt));
		printf(" StringMsg: ");
		printf("%s \n",txt); 
        break;
	case 'R': //RFID tag
        network.read(header,&uid,4); 
		
		//uidString = (char *)uid;
		
		//BYTE array[100];
		char hexstr[9];
		int i;
		for (i=0; i<4; i++) {
			sprintf(hexstr+i*2, "%02x", uid[i]);
		}
		hexstr[i*2] = 0;

		// std::string dec_num;
          // dec_num =  String(uid[0],DEC);
          // dec_num += " ";
          // dec_num += String(uid[1],DEC);
          // dec_num += " ";
          // dec_num += String(uid[2],DEC);
          // dec_num += " ";
          // dec_num += String(uid[3],DEC);
		//char* decString = string2char(dec_num);
		
		
        printf("Node: ");
		printf("%d", nodeID);
		printf(" RFID UID: ");
		printf(hexstr);
        // for (int i = 0; i < 4; i++) {
          // printf("%d", uid[i]);
          //printf(" ");
        // }
        printf("\n");
        
        if(nodeID == 1){ //if rec'd RFID from side 1
          SlaveCommand(2,2); //set the side 1 tee line node to "live" mode
          SlaveCommand(3,2); //set the side 1 hog line node to "live" mode
        }
        else if(nodeID == 6){ //if rec'd RFID from side 2
          SlaveCommand(5,2); //set the side 2 tee line node to "live" mode
          SlaveCommand(4,2); //set the side 2 hog line node to "live" mode
        }
        
        teeTripped = false;
        hogTripped = false;
		
		temp = 0;  //reset temp and humidity 
		hum = 0;
		
		char nodeString[1];
		sprintf(nodeString,"%d",nodeID);
		/* printf(nodeString);
		printf("\n"); */
		
        char RFIDinfo[20];
		strcpy(RFIDinfo,"uid:");
		strcat(RFIDinfo,hexstr);
		strcat(RFIDinfo,",");
		strcat(RFIDinfo,nodeString);
		
		/* printf("uidBeingSent:");
		printf(RFIDinfo);
		printf("\n");*/
		
		SendDataToServer("localhost",10000,RFIDinfo);
		
        break;
	case 'T': //Trip detected
        network.read(header,&trip,sizeof(trip)); 
        printf("Node: ");
		printf("%d", nodeID);
		printf(" TRIP!  local start: ");
		printf("%lu", trip[1]);
		printf(" Duration: ");
		printf("%lu", trip[2]);
		printf(" TempC: ");
		printf("%lu", trip[3]);
		printf(" Hum: ");
		printf("%lu", trip[4]);
		printf(" MinPingTime: ");
		printf("%lu", trip[5]);
		printf("\n");
          
          //tripInfo[x]
          // 0: teeTripMasterTime
          // 1: teeTripDuration
          // 2: teeHogSplit
          // 3: hogTripDuration
          // 4: tempC
          // 5: humidity
          // 6: distance1
          // 7: distance2
		  

		  
		if(nodeID == 2){
			temp = trip[3];
			hum = trip[4];
		}
        if((teeTripped == false) && (hogTripped == false)) {  //if no lasers have been tripped yet
          if((nodeID == 2) or (nodeID == 5)) { //if the tee is tripped
			unsigned long long int millisSinceTrip = (unsigned long long int)millis1() - ((unsigned long long int)trip[1] + ((unsigned long long int)masterNodeTime[nodeID] - (unsigned long long int)slaveNodeTime[nodeID]));
			//printf("%lu\n", millis1()); 
			//printf("%ull\n",((unsigned)trip[1] + ((unsigned)masterNodeTime[nodeID] - (unsigned)slaveNodeTime[nodeID])));
			//printf("%llu\n", millisSinceTrip); 
			
			
            tripInfo[0] = (unsigned long long int)time(0) - (millisSinceTrip / 1000);  //UNIX time since epoch in seconds
									//trip[1] + ((long)masterNodeTime[nodeID] - (long)slaveNodeTime[nodeID]);
			masterTeeTime = trip[1] + ((long)masterNodeTime[nodeID] - (long)slaveNodeTime[nodeID]);
            tripInfo[1] = trip[2];
            tripInfo[4] = trip[3];
            tripInfo[5] = trip[4];
            tripInfo[6] = trip[5];
            teeTripped = true;
          }
          else if((nodeID == 3) or (nodeID == 4)) {
            SlaveCommand(nodeID,2); //set the hog line back to "live" mode
          }
        }
        else if((teeTripped == true) && (hogTripped == false)) { //tee has already been tripped, hog has not.
          if((nodeID == 3) or (nodeID == 4)) { //if a hog is tripped
            tripInfo[2] = trip[1] + (masterNodeTime[nodeID] - slaveNodeTime[nodeID]) - masterTeeTime;
									//trip[1] + ((long)masterNodeTime[nodeID] - (long)slaveNodeTime[nodeID]);
            tripInfo[3] = trip[2];
            tripInfo[7] = trip[5];
            hogTripped = true;
          }
        }
        if((teeTripped == true) && (hogTripped == true)) {  //Check to see if a trip is complete.
          printf("----Shot Summary----\n");
		  printf("Split time (seconds): ");
		  printf("%.2f", ((float)tripInfo[2])/1000);
		  printf("  Avg.FPS: ");
		  printf("%.2f", 21/(((float)tripInfo[2])/1000)); //tee-hog distance is 21 feet.
		  printf("\n");
		  
		  printf("Tee FPS: ");
		  printf("%.2f\n",(0.958 / ((float)tripInfo[1]/1000)));  //using 11.5 as rock diameter.  fix later.
		  printf("Hog FPS: ");
		  printf("%.2f\n",(0.958 / ((float)tripInfo[3]/1000)));
		  printf("---------------------\n");
          teeTripped = false;
          hogTripped = false;
		  
		  
		char TripInfoString[30];
		sprintf(nodeString,"%d",nodeID);
		  
		char trip1Info[100];
		strcpy(trip1Info,"shot1:");
		sprintf(TripInfoString,"%lu",tripInfo[0]);
		strcat(trip1Info,TripInfoString);
		strcat(trip1Info,",");
		sprintf(TripInfoString,"%lu",tripInfo[1]);
		strcat(trip1Info,TripInfoString);
		strcat(trip1Info,",");
		sprintf(TripInfoString,"%lu",tripInfo[2]);
		strcat(trip1Info,TripInfoString);
		strcat(trip1Info,",");
		sprintf(TripInfoString,"%lu",tripInfo[3]);
		strcat(trip1Info,TripInfoString);
		strcat(trip1Info,",");
		sprintf(TripInfoString,"%lu",tripInfo[4]);
		strcat(trip1Info,TripInfoString);
		strcat(trip1Info,",");
		sprintf(TripInfoString,"%lu",tripInfo[5]);
		strcat(trip1Info,TripInfoString);
		strcat(trip1Info,",");
		sprintf(TripInfoString,"%lu",tripInfo[6]);
		strcat(trip1Info,TripInfoString);
		strcat(trip1Info,",");
		sprintf(TripInfoString,"%lu",tripInfo[7]);
		strcat(trip1Info,TripInfoString);
		
		SendDataToServer("localhost",10000,trip1Info);
        }
        break;
    default:  network.read(header,0,0); 
		printf("Rcv bad type %d from 0%o\n",header.type,header.from_node); 
		break;
    }
  }
//delay(2);
  //display all connected nodes every 5 seconds.
  if(millis() - displayTimer > 5000){
    displayTimer = millis();
    printf(" \n");
    printf("********Assigned Addresses********\n");
     for(int i=0; i<mesh.addrListTop; i++){
       printf("NodeID: ");
	   printf("%d",mesh.addrList[i].nodeID);
	   printf(" RF24Network Address: ");
	   printf("%d",mesh.addrList[i].address);
	   printf("\n");
     }
    printf("**********************************\n");
  }
  
  // if(millis() - displayTimer > 1000){
		// printf("%d\n",millis());
		// displayTimer = millis();
  // }
  
  
  
  
  }
return 0;
}

      