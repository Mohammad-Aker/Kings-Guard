import os
import time
from stockfish import Stockfish
import cv2
import numpy as np

def rotate_and_save_image(image_path, initial_angle, output_filename):
    image = cv2.imread(image_path)

    (h, w) = image.shape[:2]

    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, initial_angle, 1.0)
    cos_theta = np.abs(M[0, 0])
    sin_theta = np.abs(M[0, 1])
    new_w = int((h * sin_theta) + (w * cos_theta))
    new_h = int((h * cos_theta) + (w * sin_theta))
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    rotated_image = cv2.warpAffine(image, M, (new_w, new_h))

    # Save the resultant image
    cv2.imwrite(output_filename, rotated_image)

    print(f"Resultant image saved as '{output_filename}'.")


def divide_static_chessboard(image_path, num_rows, num_cols, output_dir):
    corners = [(1078, 172), (2934, 172), (2934, 2028), (1078, 2028)]
    image = cv2.imread(image_path)

    # Define the destination points for perspective transform
    width, height = 1856, 1856
    dst_pts = np.float32([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ])

    M = cv2.getPerspectiveTransform(np.float32(corners), dst_pts)
    warped_image = cv2.warpPerspective(image, M, (width, height))

    cell_height = height // num_rows
    cell_width = width // num_cols

    os.makedirs(output_dir, exist_ok=True)

    # Prepare the file names in the correct order (row by row from top to bottom)
    file_names = ['h8', 'h7', 'h6', 'h5', 'h4', 'h3', 'h2', 'h1',
                'g8', 'g7', 'g6', 'g5', 'g4', 'g3', 'g2', 'g1',
                  'f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1',
                  'e8', 'e7', 'e6', 'e5', 'e4', 'e3', 'e2', 'e1',
                  'd8', 'd7', 'd6', 'd5', 'd4', 'd3', 'd2', 'd1',
                  'c8', 'c7', 'c6', 'c5', 'c4', 'c3', 'c2', 'c1',
                  'b8', 'b7', 'b6', 'b5', 'b4', 'b3', 'b2', 'b1',
                  'a8', 'a7', 'a6', 'a5', 'a4', 'a3', 'a2', 'a1']


    for i in range(num_rows):
        for j in range(num_cols):
            x_start = j * cell_width
            y_start = i * cell_height
            cell = warped_image[y_start:y_start + cell_height, x_start:x_start + cell_width]
            cell_filename = os.path.join(output_dir, f'{file_names[i * num_cols + j]}.jpg')
            cv2.imwrite(cell_filename, cell)

    print(f"Chessboard divided into {num_rows * num_cols} cells and saved in '{output_dir}'.")

    # Draw grid lines on the warped image for visualization
    for i in range(1, num_rows):
        y = i * cell_height
        cv2.line(warped_image, (0, y), (width, y), (0, 255, 0), 2)  # Horizontal lines

    for j in range(1, num_cols):
        x = j * cell_width
        cv2.line(warped_image, (x, 0), (x, height), (0, 255, 0), 2)  # Vertical lines

    # Save the image with grid lines
    # cv2.imwrite(os.path.join(output_dir, 'DividedChessboardWithLines.jpg'), warped_image)

    # Optionally show the image
    # cv2.imshow("Divided Chessboard with Lines", warped_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #print(file_names)

def board_divider(image_path):
    initial_angle = -1  # Angle to rotate the image initially
    output_filename = 'resultant_image.jpg'  # Output file name
    rotate_and_save_image(image_path, initial_angle, output_filename)
    divide_static_chessboard(output_filename, 8, 8, 'divided_output')
