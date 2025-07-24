Proof of Concept: Low-Cost Blackbox System for LMVs and Two-Wheelers
This repository represents a working proof of concept for a Blackbox system I am developing for LMV's and 2-Wheelers. It is supposed to replicate some of the key features of Professional Event Data Recorders used in modern automobile such as crash logging, sensor data synchronisation and drowsiness detection but on a smaller budget using microcontrollers. While my long-term goal is to interface it directly to the ECU of a car to get real time data with more parameters, the current setup uses potentiometers to vary parameters for data logging.
The system logs 3 analog inputs at a time (Due to Raspberry pi pico having only 3 ADC inputs) and estimates crash severity and driver alertness using a custom python script on a PC with webcam input. This is currently not deployable hardware in a vehicle (unless the respective sensors are used instead of the potentiometer) but it demonstrates the feasibility of low cost telemetry systems for accident logging, emergency response and analysis.

Purpose:
 - Serves as a hardware software integration project for demonstration.
 - Explore the feasibility of EDR-like systems using cheap and easily available components.
 - Explore their future integrations into legal ventures like insurance data aquisition, accident analysis and emergency response.

Features Demonstrated

-  Analog signal logging via ADC (speed, brake pressure, gyroscope, engine temperature, steering, Impact Intensity)
-  Impact severity estimation (level 0 to 2)
-  Drowsiness detection using Eye Aspect Ratio (EAR) and webcam
-  UART communication between microcontroller and PC
-  Time-synchronized data logging to Excel


---

##  Hardware Used

- Raspberry Pi Pico (MicroPython)
- 6 Potentiometers (simulate vehicle analog signals)
- Diodes for ADC multiplexing
- Pushbutton for selecting pot groups
- Webcam (for facial input)
- PC/laptop for logging and display

---
Tips:

##  Note on Sensor Simulation and ADC Limitations

- Potentiometers are used here to **simulate real analog vehicle sensors** such as speed, brake pressure, and steering input.
- The system is easily adaptable to **real sensors** by changing the wiring and modifying the code accordingly.
- On **Arduino**, you can use **PLX-DAQ** for direct data logging and connect each sensor or potentiometer to a dedicated ADC pin.

###  Why Diodes and Switching Are Used on the Raspberry Pi Pico

- The **Raspberry Pi Pico** has only **3 ADC pins**, but we need to handle **6 inputs**.
- To overcome this:
  - A **switching array** is used, with **GPIO pins controlling VCC** to each potentiometer.
  - **Diodes in reverse bias** isolate each potentiometer, preventing **voltage leakage** or **shared resistance** when not in use.
  - Only one set of 3 potentiometers is active at any time.
  - A **pushbutton** toggles between the two sets (pots 1–3 and pots 4–6).

###  Handling Inactive Potentiometer Values

- When a potentiometer is inactive, it does **not produce valid ADC output**.
- The code handles this by:
  - **Storing the last known value** of each potentiometer.
  - **Logging the stored value** continuously until the pot becomes active again.
- This ensures **seamless data continuity** with no gaps or null values in the Excel log.

### Software Requirements

### On Raspberry Pi Pico
- MicroPython flashed on the board
- `code/pico_script.py`

### On PC (Windows/Linux)
- Python 3.8+
- Serial port access
- Webcam access
- also download this required facial landmark model (NOT included in repo due to size):  https://github.com/davisking/dlib-models

Install dependencies:

```bash
pip install -r requirements.txt




  

