import speech_recognition as sr

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize game status
game_status = 0  # 0 for paused, 1 for resumed

def listen_for_command():
    global game_status

    try:
        with sr.Microphone() as source:
            print("Listening for 'resume' or 'pause'...")

            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio).lower()
            print(f"Detected command: {command}")

            if "resume" in command:
                game_status = 1
                print("Game status set to: Resume")
            elif "pause" in command:
                game_status = 0
                print("Game status set to: Pause")

    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

def get_game_status():
    return game_status

if __name__ == "__main__":
    while True:
        listen_for_command()
        print(f"Current game status: {get_game_status()}")
