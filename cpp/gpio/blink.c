// blink.c
//
// Example program for bcm2835 library
// Blinks a pin on an off every 0.5 secs
//
// After installing bcm2835, you can build this 
// with something like:
// gcc -o blink blink.c -l bcm2835
// sudo ./blink
//
// Or you can test it before installing with:
// gcc -o blink -I ../../src ../../src/bcm2835.c blink.c
// sudo ./blink
//
// Author: Mike McCauley
// Copyright (C) 2011 Mike McCauley
// $Id: RF22.h,v 1.21 2012/05/30 01:51:25 mikem Exp $

#include <bcm2835.h>
#include <stdio.h>

// Blinks on RPi Plug P1 pin 11 (which is GPIO pin 17)
// #define PIN RPI_GPIO_P1_11
#define PIN RPI_V2_GPIO_P1_19

int main(int argc, char **argv)
{
    // If you call this, it will not actually access the GPIO
    // Use for testing
    // bcm2835_set_debug(1);
    TP();

    if (!bcm2835_init())
    {
        printf("bcm2835 initialisation has failed");
        return 1;
    }
    TP();
    
    // Set the pin to be an output
    bcm2835_gpio_fsel(PIN, BCM2835_GPIO_FSEL_OUTP);
    printf("set the pin to be an output");

    TP();

    // Blink
    while (1)
    {
	printf("Turn it on \n");
	bcm2835_gpio_write(PIN, HIGH);
	
	printf("wait a bit \n");
	bcm2835_delay(500);
	
	printf("turn it off \n");
	bcm2835_gpio_write(PIN, LOW);
	
	printf("wait a bit \n");
	bcm2835_delay(500);
    }
    bcm2835_close();
    return 0;
}

