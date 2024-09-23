
from flask_cors import CORS  # Import CORS
from flask import Flask, jsonify, request
import Image_capture
import threading
from generator import generate_fen, generate_move_and_update_fen
import speechTest
import serial
import time
import logging
import warnings
import sys
import os

app = Flask(__name__)
CORS(app)




SERIAL_PORT = '/dev/ttyACM1'
BAUD_RATE = 9600
SERIAL_PORT2 = '/dev/ttyAMA0'

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
ser2 = serial.Serial(SERIAL_PORT2, BAUD_RATE)
# Start the camera thread
camera_thread = threading.Thread(target=Image_capture.initialize_camera)
camera_thread.daemon = True
camera_thread.start()

# game global variables
current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"
move = ""
next_fen = ""

# Motion inactivity tracker
last_motion_time = time.time()
MOTION_TIMEOUT = 120

def read_sensor_data():
    ser.flushInput()
    line = ser.readline().decode('utf-8').strip()
    return map(float, line.split(','))


@app.route('/process', methods=['GET'])
def process_request():
    global current_fen
    global next_fen
    global last_motion_time

    try:
        # Check if the game is paused
        if speechTest.get_game_status() == 0:
            return jsonify({"error": "Game is paused, resume it to play"}), 400

        print(f"current fen: {current_fen} \n")

        # Read sensor data
        distance1, distance2, weight, motion = read_sensor_data()


        if motion == 0:

            # If no motion, check how long it's been since motion was last detected
            if time.time() - last_motion_time > MOTION_TIMEOUT:
                return jsonify({"error": "Player left the game"}), 400
        else:
            # Motion detected, reset the last motion time
            last_motion_time = time.time()

        # sensor range
        MIN_DISTANCE = 60
        MAX_DISTANCE = 1000
        MIN_DISTANCE2 = 75
        MAX_DISTANCE2 = 83
        MIN_WEIGHT = 10
        MAX_WEIGHT = 1000

        # Check if sensor data is within the acceptable range
        if not (MIN_DISTANCE2 <= distance2 <= MAX_DISTANCE2):
            return jsonify("Obstacles detected by sensor 2"), 400

        elif not (MIN_DISTANCE <= distance1 <= MAX_DISTANCE):
            return jsonify("Obstacles detected by sensor 1"), 400

        elif not (MIN_WEIGHT <= weight <= MAX_WEIGHT):
            return jsonify("Piece not detected for retrieval"), 400

        else:
            save_dir = "Full_boards"
            #Image_capture.capture_and_process_image(save_dir)  #commented this line to disable camera


            next_fen, changes, extracted_move, is_legal = generate_fen(current_fen)
            print(f"next_fen: {next_fen} \n"
                  f"changes: {changes} \n"
                  f"extracted move: {extracted_move} \n"
                  f"is legal: {is_legal} \n")

            if changes == 2:
                if is_legal:
                    return jsonify(next_fen), 200
                else:
                    return jsonify("Illegal move"), 400

            elif changes < 5 and changes > 0:
                if is_legal:
                 return jsonify(next_fen), 200
                else:
                  return jsonify("Illegal move"), 400

            else:
                return jsonify({"error": "Too many changes"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/setFen', methods=['POST'])
def set_fen():
    global current_fen
    global next_fen

    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        fen = data.get('fen')
        if not fen:
            return jsonify({"error": "FEN is missing in the request data"}), 400

        fen_complete = f"{fen} b - - 0 1"

        print(f"Received FEN: {fen}")
        print(f"Complete FEN: {fen_complete}")

        current_fen = fen_complete
        next_fen = ""

        result = generate_move_and_update_fen(current_fen)

        if result and len(result) == 4:
            updated_fen, move, move_type, is_checkmate = result
            command = f"{move}{move_type}".upper()

            ser2.write(command.encode())
            print(f"Updated FEN: {updated_fen}"
                  f"checkmate?: {is_checkmate}")

        else:
            return jsonify({"error": "Failed to generate move"}), 500

        current_fen = updated_fen
        return jsonify({"updated_fen": updated_fen}), 200

    except Exception as e:

        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/confirmFen', methods=['POST'])
def confirm_fen():
    global current_fen
    global next_fen

    try:

        updated_fen, done_move, move_type, is_checkmate = generate_move_and_update_fen(next_fen)

        current_fen = updated_fen

        print(f"Updated FEN: {updated_fen}"
              f"checkmate?: {is_checkmate}"
              f"current fen : {current_fen} ")

        next_fen = ""
        command = f"{done_move}{move_type}".upper()
        ser2.write(command.encode())

        return jsonify(current_fen), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
