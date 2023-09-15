import serial

ser = serial.Serial(
   port='Enter Port',
   baudrate=19200,
   parity=serial.PARITY_ODD,
   stopbits=serial.STOPBITS_TWO,
   bytesize=serial.EIGHTBITS
)

ser.close()

