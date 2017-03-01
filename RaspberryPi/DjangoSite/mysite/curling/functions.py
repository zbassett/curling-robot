from django.core import serializers

def DistanceCalc(PingTime,Temp,Humidity):
	#Speed of sound (m/s)
	SoS = 331.4 + (0.606 * float(Temp)) + (0.0124 * float(Humidity))
	
	one_way_time = float(PingTime) / 1000000 / 2 #convert nanoseconds to seconds.  divide by two since sound has to travel to and from the rock

	distance = SoS * one_way_time

	return distance





