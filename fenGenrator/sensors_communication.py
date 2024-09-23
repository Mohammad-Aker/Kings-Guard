import serial

arduino = serial.Serial('/dev/tty.usbmodem2101', 9600, timeout=1)  # change port when error is thrown

def read_ultrasonic_data():
    # Read data from the serial port
    if arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        return data
    return None

def process_ultrasonic_data(data):
    # Split the received data and extract avg1 and avg2
    try:
        parts = data.split(',')
        avg1 = float(parts[0].split(':')[1])
        avg2 = float(parts[1].split(':')[1])
        return avg1, avg2
    except (IndexError, ValueError) as e:
        print(f"Error processing data: {e}")
        return None, None

def finalize_ultrasonic():
    data = read_ultrasonic_data()
    if data:
        avg1, avg2 = process_ultrasonic_data(data)
        if avg1 is not None and avg2 is not None:
            print(f"Average Distance 1: {avg1} cm")
            print(f"Average Distance 2: {avg2} cm")
            return avg1, avg2
    return None, None

if __name__ == "__main__":
    avg1, avg2 = finalize_ultrasonic()
    if avg1 is not None and avg2 is not None:
        print(f"Final Average Distance 1: {avg1} cm")
        print(f"Final Average Distance 2: {avg2} cm")
    else:
        print("Failed to retrieve valid sensor data.")
