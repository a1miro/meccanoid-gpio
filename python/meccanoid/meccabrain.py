import RPi.GPIO as GPIO
import time

usleep = lambda x: time.sleep(x/1000000.0)

class MeccaBrain(object):
    BIT_DELAY_USEC=417
    READ_BIT_DELAY_USEC=2500

    def __init__(self, pin):
        self._pin = pin
        self._modulenum = 0
        self._output = bytearray(4)
        self._input = bytearray(4)
        
        # Set GPIO mode to RPi I/O mapping
        GPIO.setmode(GPIO.BOARD)
        # Configure output pin
        GPIO.setup(self._pin, GPIO.OUT)

    @property
    def pin(self):
        return self._pin


    def color(self, servo, color):
        self._output[servo] = color
    

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
        self._send(0xFF)     # Send header

        for b in self._output:
            self._send(b)

        checksum = self._checksum(
                self._output[0], 
                self._output[1], 
                self._output[2], 
                self._output[3]
                )

        self._send(checksum)  # Sending checksum
        return self._receive()



    def _send(self, data):

        GPIO.setup(self._pin, GPIO.OUT)

        # Start bit, 417 usec LOW
        GPIO.output(self._pin, GPIO.LOW)
        usleep(MeccaBrain.BIT_DELAY_USEC)

        for b in range(0,8):
            mask = 1 << b;
            if (data & mask):
                GPIO.output(self._pin, GPIO.HIGH)
            else:
                GPIO.output(self._pin, GPIO.LOW)
            usleep(MeccaBrain.BIT_DELAY_USEC)

        # Stop bit - HIGH 
        GPIO.output(self._pin, GPIO.LOW)
        usleep(MeccaBrain.BIT_DELAY_USEC)

        # Stop bit - HIGH 
        GPIO.output(self._pin, GPIO.LOW)
        usleep(MeccaBrain.BIT_DELAY_USEC)

    def _receive(self):
        data = 0
        GPIO.setup(self._pin, GPIO.IN)

        # TODO: Why so long time 1.5?
        time.sleep(0.5)

        for b in range(0,8):
            mask = 1 << b;

            if GPIO.input(self._pin) == GPIO.HIGH:
                pass
                data |= 1 << b;

            usleep(MeccaBrain.READ_BIT_DELAY_USEC)

        return data

    def _checksum(self, data1, data2, data3, data4):
        CS = data1 + data2 + data3 + data4 # ignore overflow
        CS = CS + (CS >> 8)                # right shift 8 places
        CS = CS + (CS << 4)                # left shift 4 places
        CS = CS & 0xF0
        CS = CS | self._modulenum
        return CS



if __name__ == "__main__":
    mecca = MeccaBrain(21)
    colors = [ 0xF7, 0xF6, 0xF5, 0xF4, 0xF3, 0xF2, 0xF1, 0xF0]
    for c in colors:
        mecca.color(1,c)
        r = mecca.communicate()
        print("return = %d" % r)
        time.sleep(1)

