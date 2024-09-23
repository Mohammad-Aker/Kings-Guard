import os
import modelTest
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def process_image(image_path):
    try:

        detections = modelTest.detect_obj(image_path)


        detected_class = None
        conf = None


        if detections and isinstance(detections, list) and len(detections) > 0:

            first_detection = detections[0]
            detected_class = first_detection.get('class')
            conf = first_detection.get('confidence')


        return {
            'image': os.path.basename(image_path),
            'detected_class': detected_class,
            'conf': conf
        }

    except Exception as e:
        # Handle errors in detection
        print(f"Error processing image {image_path}: {e}")
        return {
            'image': os.path.basename(image_path),
            'detected_class': 'error',
            'conf': None
        }

def process_images_detections(directory):

    image_files = [os.path.join(directory, f) for f in sorted(os.listdir(directory)) if
                   f.endswith(('.jpg', '.jpeg', '.png'))]


    if len(image_files) != 64:
        raise ValueError("The directory should contain exactly 64 images.")

    detections_list = []


    with ThreadPoolExecutor() as executor:

        future_to_image = {executor.submit(process_image, image_path): image_path for image_path in image_files}

        for future in as_completed(future_to_image):
            image_path = future_to_image[future]
            try:
                result = future.result()
                detections_list.append(result)
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                detections_list.append({
                    'image': os.path.basename(image_path),
                    'detected_class': 'error',
                    'conf': None
                })
    sorted_detections_list = sorted(detections_list, key=lambda x: x['image'] or '')

    return sorted_detections_list

#Example usage:
#start_time = time.time()

# Example usage:
#directory = "divided_output"
#results = process_images_detections(directory)

#end_time = time.time()

#print(f"Execution time: {end_time - start_time:.2f} seconds")
