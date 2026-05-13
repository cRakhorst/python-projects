import time
import random
import serial
import threading

# Game states
STATE_WAITING = 0
STATE_READY = 1
STATE_GO = 2
STATE_RESULTS = 3

game_state = STATE_WAITING
reaction_start_time = 0
reaction_time = 0
round_count = 0
button_pressed = False
ser = None


def read_serial():
    """Read from Arduino serial port in a separate thread"""
    global button_pressed, ser
    
    while True:
        try:
            if ser and ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line == "1":  # Arduino sends "1" on button press
                    button_pressed = True
        except Exception as e:
            print(f"Serial read error: {e}")
            break
        time.sleep(0.01)


def start_new_round():
    """Start a new reaction time round"""
    global game_state, reaction_start_time
    
    # Wait random time between 1-4 seconds
    wait_time = random.uniform(1, 4)
    print("Get ready...")
    time.sleep(wait_time)
    
    # Signal to react
    print(">>> REACT NOW! <<<")
    game_state = STATE_GO
    reaction_start_time = time.time()


def display_results():
    """Display the reaction time results"""
    global reaction_time
    
    print("\n========== RESULTS ==========")
    print(f"Your reaction time: {reaction_time:.0f} ms")
    
    if reaction_time < 150:
        print("Incredible! You're superhuman!")
    elif reaction_time < 200:
        print("Excellent! Professional gamer material!")
    elif reaction_time < 250:
        print("Great! That's a solid reaction time!")
    elif reaction_time < 300:
        print("Good! Average human reaction time!")
    else:
        print("Not bad! Try to be faster next time!")
    
    print("=============================\n")


def find_arduino_port():
    """Find the Arduino COM port"""
    import subprocess
    
    try:
        # List available COM ports on Windows
        result = subprocess.run(['wmic', 'logicaldisk', 'get', 'name'], capture_output=True)
        
        # Try common Arduino ports
        for port in ['COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']:
            try:
                test_ser = serial.Serial(port, 9600, timeout=1)
                time.sleep(1)
                test_ser.close()
                return port
            except:
                continue
    except:
        pass
    
    return None


def main():
    """Main game loop"""
    global game_state, round_count, button_pressed, reaction_time, ser
    
    # Try to connect to Arduino
    print("Looking for Arduino...")
    port = find_arduino_port()
    
    if not port:
        # Ask user for port
        port = input("Enter Arduino COM port (e.g., COM3): ").strip()
    
    # Try to connect with retry logic
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            print(f"Connected to Arduino on {port}\n")
            break
        except PermissionError:
            retry_count += 1
            if retry_count < max_retries:
                print(f"\n⚠ Port {port} is already in use!")
                print("Common causes:")
                print("  - Arduino IDE Serial Monitor is open")
                print("  - Another program is using this port")
                print("\nPlease close any other programs using this port.")
                response = input(f"Retry connection? (y/n): ").strip().lower()
                if response != 'y':
                    print("Exiting...")
                    return
            else:
                print(f"\nFailed to connect after {max_retries} attempts.")
                return
        except Exception as e:
            print(f"Failed to connect to Arduino on {port}: {e}")
            return
    
    print("\n========================================")
    print("   REACTION TIME GAME")
    print("   (Arduino Controller)")
    print("========================================")
    print("Press any button on your joystick to start!")
    print("========================================\n")
    
    # Start serial reader thread
    reader_thread = threading.Thread(target=read_serial, daemon=True)
    reader_thread.start()
    
    try:
        while True:
            if game_state == STATE_WAITING:
                if button_pressed:
                    button_pressed = False
                    round_count += 1
                    print(f"\n>>> ROUND {round_count} <<<")
                    game_state = STATE_READY
                    start_new_round()
            
            elif game_state == STATE_GO:
                if button_pressed:
                    button_pressed = False
                    reaction_time = (time.time() - reaction_start_time) * 1000  # Convert to ms
                    game_state = STATE_RESULTS
                    display_results()
                    time.sleep(2)
                    game_state = STATE_WAITING
                    print("Press any button to play again!")
            
            time.sleep(0.01)  # Small delay to prevent busy waiting
    
    except KeyboardInterrupt:
        print("\n\nThanks for playing!")
    finally:
        if ser:
            ser.close()


if __name__ == "__main__":
    main()
