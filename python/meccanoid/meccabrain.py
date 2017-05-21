import RPi.GPIO as GPIO
import time
import numpy as np

usleep = lambda x: time.sleep(x/1000000.0)

class MeccaBrain(object):
    BIT_DELAY_USEC=417
    READ_BIT_DELAY_USEC=2500

    def __init__(self, pin):
        self._pin = pin
        self._output = np.uint8([0xFF,0xFF,0xFF,0xFF]) 
        self._input = np.uint8([0xFF,0xFF,0xFF,0xFF])

        self._module_type = ["_", "_", "_", "_"]
        self._modulenum = 0

        # Set GPIO mode to RPi I/O mapping
        GPIO.setmode(GPIO.BCM)
        # Configure output pin
        GPIO.setup(self._pin, GPIO.OUT)


    def __del__(self):
        print("+++ dtor")
        GPIO.cleanup()

    @property
    def pin(self):
        return self._pin


    def color(self, servo, color):
        self._output[servo] = np.uint8(color)
   

    def communicate(self):
        '''
        communicate()  -  this is the main method that takes care of 
        initializing, sending data to and receiving data from Meccano Smart
        modules

        The datastream consists of 6 output bytes sent to the Smart modules
        and  one return input byte from the Smart modules.  Since there can
        be a maximum of 4 Smart modules in a chain, each module takes turns
        replying along the single data wire.  
        
        Output bytes:   
        0xFF - the first byte is always a header byte of 0xFF
        Data 1 -  the second byte is the data for the Smart module at the 
        1st position in the chain
        Data 2 -  the third byte is the data for the Smart module at the 
        2nd position in the chain
        Data 3 -  the fourth byte is the data for the Smart module at the 
        3rd position in the chain
        Data 4 -  the fifth byte is the data for the Smart module at the 
        4th position in the chain 
        Checksum  -  the sixth byte is part checksum, part module ID.  
        The module ID tells which of the modules in the chain should 
        reply end

        '''
        checksum = np.uint8(self._checksum(
                self._output[0], 
                self._output[1], 
                self._output[2], 
                self._output[3]
                ))

        print("checksum = 0x%02X" % checksum)

        # Sending data 
        self._send(np.uint8(0xFF))     # Send header

        for b in self._output:
            self._send(b)
       
        self._send(checksum)  # Sending checksum
        
        return self._receive()

   
    def _send(self, data):

        GPIO.setup(self._pin, GPIO.OUT)

        # Start bit, 417 usec LOW
        GPIO.output(self._pin, GPIO.LOW)
        usleep(MeccaBrain.BIT_DELAY_USEC)
        
        for b in range(0,8):
            mask = np.uint8(1 << b)

            if data & mask:
                GPIO.output(self._pin, GPIO.HIGH)
            else:
                GPIO.output(self._pin, GPIO.LOW)
            usleep(MeccaBrain.BIT_DELAY_USEC)

        # Stop bit - HIGH 
        GPIO.output(self._pin, GPIO.HIGH)
        usleep(MeccaBrain.BIT_DELAY_USEC)

        # Stop bit - HIGH 
        GPIO.output(self._pin, GPIO.HIGH)
        usleep(MeccaBrain.BIT_DELAY_USEC)

    def _myinput(self, pin):
        s = GPIO.LOW
        pulse = 0
        for t in range(0,100):
            s = GPIO.input(self._pin)
            if s == GPIO.LOW:
                break
            pulse += 100
            usleep(25) 
        return pulse 

    def _receive(self):
        data = np.uint8(0)
        GPIO.setup(self._pin, GPIO.IN)

        # TODO: Why so long time 1.5?
        #usleep(MeccaBrain.READ_BIT_DELAY_USEC)
        usleep(1.5)

        for b in range(0,8):
            mask = np.uint8(1 << b)
            #usleep(MeccaBrain.BIT_DELAY_USEC)
            if self._myinput(self._pin) > 400:
                data |= mask;
        #usleep(MeccaBrain.READ_BIT_DELAY_USEC)

        return data

    def _checksum(self, data1, data2, data3, data4):
        CS = data1 + data2 + data3 + data4 # ignore overflow
        CS = CS + (CS >> 8)                # right shift 8 places
        CS = CS + (CS << 4)                # left shift 4 places
        CS = CS & 0xF0
        CS = CS | self._modulenum
        return np.uint8(CS)



if __name__ == "__main__":
    colors = np.uint8([ 0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70])
    #colors = np.uint8([0xF1, 0xF2, 0xF3, 0xF4, 0xF5])
    mecca = MeccaBrain(21)
    '''
    print("modulenum = %d" % mecca._modulenum)
    mecca.color(0,0xFE)
    mecca.color(1,0xFE)
    mecca.color(2,0xFE)
    mecca.color(3,0xFE)

    r = mecca.communicate()
    print("returned r = 0x%02X" % r)


    mecca._modulenum = 1
    print("modulenum = %d" % mecca._modulenum)
    mecca.color(0,0xFE)
    mecca.color(1,0xFE)
    mecca.color(2,0xFE)
    mecca.color(3,0xFE)

    r = mecca.communicate()
    print("returned r = 0x%02X" % r)


    mecca._modulenum = 2
    print("modulenum = %d" % mecca._modulenum)
    mecca.color(0,0xFE)
    mecca.color(1,0xFE)
    mecca.color(2,0xFE)
    mecca.color(3,0xFE)

    r = mecca.communicate()
    print("returned r = 0x%02X" % r)

    mecca._modulenum = 3
    print("modulenum = %d" % mecca._modulenum)
    mecca.color(0,0xFE)
    mecca.color(1,0xFE)
    mecca.color(2,0xFE)
    mecca.color(3,0xFE)

    r = mecca.communicate()
    print("returned r = 0x%02X" % r)
    '''

    r = mecca.communicate()
    print("init return = 0x%02X" % r)
    for c in colors:
        print("changing color to 0x%02X" % c)
        mecca.color(0,c)
        r = mecca.communicate()
        print("id = %d, return = 0x%02X" % (0,r))
        
        mecca.color(1,c)
        r = mecca.communicate()
        print("id = %d, return = 0x%02X" % (1,r))

        mecca.color(2,c)
        r = mecca.communicate()
        print("id = %d, return = 0x%02X" % (2,r))

        mecca.color(3,c)
        r = mecca.communicate()
        print("id = %d, return = 0x%02X" % (3,r))

        time.sleep(1)

