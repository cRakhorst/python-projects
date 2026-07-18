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
ready_end_time = 0  # When to transition from READY to GO
reaction_time = 0
opponent_time = 0
round_count = 0
button_pressed = False
lives = 3
difficulty = 0  # Increments by 5ms per win
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
    global game_state, ready_end_time
    
    # Wait random time between 1-4 seconds
    wait_time = random.uniform(1, 4)
    print("Get ready...")
    
    # Set the time when we should transition to GO state (non-blocking)
    ready_end_time = time.time() + wait_time


def display_results():
    """Display the reaction time results"""
    global reaction_time, opponent_time, lives
    
    print("\n========== RESULTS ==========")
    print(f"Your reaction time: {reaction_time:.0f} ms")
    print(f"Opponent reaction time: {opponent_time:.0f} ms")
    print(f"Lives remaining: {lives}")
    
    if reaction_time < opponent_time:
        print(f"\n🎉 YOU WON! You were {opponent_time - reaction_time:.0f} ms faster!")
    elif reaction_time > opponent_time:
        print(f"\n😔 YOU LOST! Opponent was {reaction_time - opponent_time:.0f} ms faster.")
    else:
        print("\n🤝 IT'S A TIE!")
    
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
    global game_state, round_count, button_pressed, reaction_time, opponent_time, ser, lives, difficulty
    
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
                    print(f"Lives: {lives}")
                    game_state = STATE_READY
                    start_new_round()
            
            elif game_state == STATE_READY:
                # Check if it's time to transition to GO state
                if time.time() >= ready_end_time:
                    # Generate opponent's random reaction time (300-500ms) adjusted by difficulty
                    min_time = max(50, 300 - difficulty)  # Don't go below 50ms
                    max_time = max(55, 500 - difficulty)  # Ensure max is at least 5ms above min
                    opponent_time = random.uniform(min_time, max_time)
                    print(">>> REACT NOW! <<<")
                    game_state = STATE_GO
                    reaction_start_time = time.time()
                
                # Detect early clicks (clicking before "REACT NOW")
                elif button_pressed:
                    button_pressed = False
                    lives -= 1
                    print("\n❌ TOO EARLY! You clicked before 'REACT NOW'!")
                    print(f"Lost a life! Lives remaining: {lives}")
                    
                    if lives <= 0:
                        print("\n========== GAME OVER ==========")
                        print(f"Total rounds completed: {round_count - 1}")
                        print("============================\n")
                        return
                    
                    time.sleep(1)
                    game_state = STATE_WAITING
                    print("Press any button to try again!")
            
            elif game_state == STATE_GO:
                if button_pressed:
                    button_pressed = False
                    reaction_time = (time.time() - reaction_start_time) * 1000  # type: ignore # Convert to ms
                    game_state = STATE_RESULTS
                    display_results()
                    
                    # Check if player lost against opponent
                    if reaction_time > opponent_time:
                        lives -= 1
                        print(f"❌ You lost! Lost a life. Lives remaining: {lives}")
                        
                        if lives <= 0:
                            print("\n========== GAME OVER ==========")
                            print(f"Total rounds completed: {round_count}")
                            print("============================")
                            print(f"Final difficulty level: {difficulty // 5} wins")
                            print("============================\n")
                            return
                    else:
                        difficulty += 5
                        print(f"✅ You won! Keep it up! Opponent getting faster... (-{difficulty // 5 * 5}ms)")
                    
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
