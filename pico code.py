from machine import ADC, Pin, UART
import time

# Initialize UART communication (assuming default baud rate 9600)
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))  # Adjust pins as necessary

# ADC pins for potentiometers (Pico has 3 ADC channels)
adc1 = ADC(26)  # ADC0 pin for pots 1 and 2 (speed and brake pressure)
adc2 = ADC(27)  # ADC1 pin for pots 3 and 4 (gyroscope and engine temp)
adc3 = ADC(28)  # ADC2 pin for pots 5 and 6 (steering and impact intensity)

# GPIO pins controlling VCC of potentiometers (sets of 2 pots each)
vcc_pins = [Pin(2, Pin.OUT), Pin(8, Pin.OUT), Pin(9, Pin.OUT), 
            Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(13, Pin.OUT)]

# Pushbutton pin (connected to 3.3V and GPIO6)
button_pin = Pin(6, Pin.IN, Pin.PULL_DOWN)

# Onboard LED pin (GPIO 25)
led = Pin(25, Pin.OUT)

# Hold current selected pots (0: first pot in set, 1: second pot in set)
pot_selection = 0  # Track which set of pots is currently selected

# Debounce time for button press
debounce_time = 0.2
last_button_press = time.ticks_ms()

# Voltage range for scaling
adc_max_value = 65535  # 16-bit ADC resolution

# Last known values for all six potentiometers
last_known_values = [0] * 6

def scale_to_range(adc_value, output_min, output_max):
    """Scale the ADC reading to the specified range."""
    scaled_value = int(((adc_value / adc_max_value) * (output_max - output_min)) + output_min)
    return scaled_value

def calculate_severity(impact_intensity):
    """Determine the severity based on the Impact Intensity."""
    if impact_intensity < 10:
        return 0
    elif impact_intensity < 30:
        return 1
    else:  # impact_intensity between 30 and 50
        return 2

def read_adc():
    """Read from the active pots based on selection and send data over UART."""
    global last_known_values
    
    if pot_selection == 0:  # Pots 1-3
        last_known_values[0] = scale_to_range(adc1.read_u16(), 0, 220)    # Speed (0 - 220 km/h)
        last_known_values[1] = scale_to_range(adc2.read_u16(), 800, 2000) # Brake Pressure (800 - 2000 psi)
        last_known_values[2] = scale_to_range(adc3.read_u16(), 0, 180)    # Gyroscope (0 - 180 degrees)
    elif pot_selection == 1:  # Pots 4-6
        last_known_values[3] = scale_to_range(adc1.read_u16(), 0, 200)    # Engine Temp (0 - 200 °C)
        last_known_values[4] = scale_to_range(adc2.read_u16(), 0, 360)    # Steering (0 - 360 degrees)
        last_known_values[5] = scale_to_range(adc3.read_u16(), 0, 50)     # Impact Intensity (0 - 50)

    # Calculate Severity based on Impact Intensity (last_known_values[5])
    severity = calculate_severity(last_known_values[5])

    # Add severity to the output values
    output_data = last_known_values + [severity]  # Append severity to the last known values

    # Prepare output data as a comma-separated string
    output_data_str = ",".join(map(str, output_data))
    
    # Send data over UART
    uart.write(output_data_str + '\n')  # Send data followed by newline for better parsing
    print(f"Sending data: {output_data_str}")  # Print data to console

def update_pot_selection():
    """Cycle through the pot sets when the button is pressed."""
    global last_button_press
    global pot_selection

    current_time = time.ticks_ms()
    if button_pin.value() == 1 and time.ticks_diff(current_time, last_button_press) > debounce_time * 1000:
        last_button_press = current_time
        pot_selection = (pot_selection + 1) % 2  # Toggle between 0 and 1 for pot sets
        update_vcc()

def update_vcc():
    """Set the VCC for the selected pot in each set."""
    for i in range(3):
        if pot_selection == 0:  # First set of pots (1-3)
            vcc_pins[i * 2].value(1)   # Turn on the first pot in the set
            vcc_pins[i * 2 + 1].value(0)  # Ground the second pot in the set
        else:  # Second set of pots (4-6)
            vcc_pins[i * 2].value(0)   # Ground the first pot in the set
            vcc_pins[i * 2 + 1].value(1)  # Turn on the second pot in the set

# Initial setup
update_vcc()

# Main loop
while True:
    update_pot_selection()
    read_adc()

    # Blink onboard LED to confirm code is running
    led.toggle()
    time.sleep(1)


