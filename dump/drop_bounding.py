

import cv2
import numpy as np
from scipy.spatial import distance

# Constants for filtering and assumptions
MIN_AREA = 50
MAX_AREA = 5000
MAX_DISTANCE = 50  # Maximum distance for tracking droplets
CROP_OFFSET = 50  # Offset to retain more of the image
class Drop_Bound():


    # Function to process an image and find contours
    def process_image(self,image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian Blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 100)

        # Find white pixels
        white_pixels = cv2.findNonZero(edges)
        if white_pixels is None:
            return image, []

        # Find the block with the highest concentration of white pixels
        row_sum = np.sum(edges, axis=1)
        max_row = np.argmax(row_sum)

        # Crop the image with an offset to retain more of the ROI
        crop_start_row = max(0, max_row -0*CROP_OFFSET)
        cropped = image[crop_start_row:, :]

        # Convert cropped image to grayscale and apply edge detection again
        gray_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        blurred_cropped = cv2.GaussianBlur(gray_cropped, (5, 5), 0)
        edges_cropped = cv2.Canny(blurred_cropped, 50, 150)

        # Dilate the binary image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges_cropped, kernel, iterations=1)


        # extract edges
        image_edges = cv2.adaptiveThreshold(
            dilated,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            blockSize=5,
            C=3
        )

        # cv2.imshow("Edges",image_edges)
        # Find contours
        contours, _ = cv2.findContours(image_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area
        filtered_contours = [c for c in contours if MIN_AREA < cv2.contourArea(c) < MAX_AREA]

        # Fill closed contours
        filled_image = dilated.copy()
        for contour in filtered_contours:
            mask = np.zeros((dilated.shape[0] + 2, dilated.shape[1] + 2), np.uint8)
            cv2.floodFill(filled_image, mask, tuple(contour[0][0]), 255)

        return cropped, filtered_contours

    # Function to find the center of each contour
    def find_centers(self,contours):
        centers = []
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centers.append((cX, cY))
        return centers


    def find_box(self,image):
        processed_image, contours = self.process_image(image)
        centers = self.find_centers(contours)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(processed_image, (x, y), (x+w, y+h), (255, 0, 0), 2)  # Draw bounding box
        # Display the results
        for contour in contours:
            cv2.drawContours(processed_image, [contour], -1, (0, 255, 0), 2)
        for center in centers:
            cv2.circle(processed_image, center, 5, (0, 0, 255), -1)

        return processed_image
   

    # Implementing interactive adjustment of contours
    def adjust_contours(image, contours):
        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                print(f"Clicked at: ({x}, {y})")
                # Implement logic for adjusting contours interactively
                pass

        cv2.namedWindow('Adjust Contours')
        cv2.setMouseCallback('Adjust Contours', on_mouse)

        while True:
            image_copy = image.copy()
            for contour in contours:
                cv2.drawContours(image_copy, [contour], -1, (0, 255, 0), 2)
            cv2.imshow( "Copy",image_copy)
            key = cv2.waitKey(1)
            if key == 27:  # Esc key to exit
                break

        cv2.destroyAllWindows()

    # # Run the contour adjustment interface
    # adjust_contours(processed_image, contours)

if __name__ == "__main__":
     # # Example image path
    image_path = "trial_images/trial8.jpeg"  # Replace with your image path
    image = cv2.imread(image_path)

    # Process the image to find contours
    processed_image=Drop_Bound.find_box(image=image)

    cv2.imshow("Processed",processed_image)