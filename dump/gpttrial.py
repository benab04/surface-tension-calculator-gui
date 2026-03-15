import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QVBoxLayout, QWidget, QLineEdit, QFileDialog, QMessageBox,QSizePolicy,QSlider,QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import QTimer, Qt, QPoint
import cv2
import numpy as np
import imutils
import itertools
import math


class CameraFeedWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Live Camera Feed")
        self.setGeometry(100, 100, 640, 480)
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(0, 0, 640, 480)
        self.capture = cv2.VideoCapture('output_video.mp4')
        self.processed_image_window = ProcessedImageWindow()
        self.processed_image_window.show()
        self.update_camera_feed()

    def update_camera_feed(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.camera_label.setPixmap(pixmap)
            self.camera_label.show()
            self.processed_image_window.update_processed_image(frame)
        else:
            self.camera_label.setText("Camera not found!")

        QTimer.singleShot(10, self.update_camera_feed)

class ProcessedImageWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edge Detection")
        self.setGeometry(750, 100, 640, 480)
        self.image_label = QLabel(self)
        self.image_label.setGeometry(0, 0, 640, 480)
        self.lower_threshold = 30  # Default lower threshold
        self.upper_threshold = 90 
        self.blur_value = 21
        self.contrast_factor = 1.0

        
    def update_canny_parameters(self, lower_threshold, upper_threshold ,blur_value, contrast_factor):
        self.contrast_factor =contrast_factor
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.blur_value = blur_value
        if blur_value %2==0:
            self.blur_value=blur_value+1
    def update_processed_image(self, frame):
        
        image_copy = frame.copy()
        image_float = np.float32(image_copy)

        contrast_factor = self.contrast_factor
        mean_brightness = np.mean(image_float)
        contrasted_image = contrast_factor * (image_float - mean_brightness) + mean_brightness
        contrasted_image = np.clip(contrasted_image, 0, 255)
        image_copy = np.uint8(contrasted_image)

        gray = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (self.blur_value, self.blur_value), 0)
        edges = cv2.Canny(blurred, self.lower_threshold, self.upper_threshold)
        color_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        edges_resized = cv2.resize(color_edges, (640, 480))
        image = QImage(edges_resized.data, edges_resized.shape[1], edges_resized.shape[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)
        self.image_label.show()
        

class CameraGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera GUI")
        self.setGeometry(100, 100, 800, 600)

        # Central widget to hold captured image
        self.central_widget = QLabel(self)
        self.central_widget.setFixedSize(640, 480)
        self.setCentralWidget(self.central_widget)

        # Container widget for buttons
        self.button_container = QWidget(self)
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_container.setGeometry(650, 0, 150, 460)
        self.button_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Dropdown for camera selection
        self.camera_dropdown = QComboBox()
        self.camera_dropdown.setFixedSize(120, 30)
        self.camera_dropdown.addItems(["Default Camera"])
        self.button_layout.addWidget(self.camera_dropdown)
        
        self.open_camera_button = QPushButton("Open Camera")
        self.open_camera_button.setFixedSize(120, 30)
        self.open_camera_button.clicked.connect(self.open_camera_feed)
        self.button_layout.addWidget(self.open_camera_button)
        # Capture image button
        self.capture_button = QPushButton("Capture Image")
        self.capture_button.setFixedSize(120, 30)
        self.capture_button.clicked.connect(self.single_capture)
        self.button_layout.addWidget(self.capture_button)

        # Burst capture button
        # self.burst_button = QPushButton("Burst Capture")
        # self.burst_button.setFixedSize(120, 30)
        # self.burst_button.clicked.connect(self.burst_capture)
        # self.button_layout.addWidget(self.burst_button)

        # Browse image button
        self.browse_button = QPushButton("Browse Image")
        self.browse_button.setFixedSize(120, 30)
        self.browse_button.clicked.connect(self.browse_image)
        self.button_layout.addWidget(self.browse_button)
        
        self.default_button = QPushButton("Restore Defaults")
        self.default_button.setFixedSize(120, 30)
        self.default_button.clicked.connect(self.restore_defaults)
        self.button_layout.addWidget(self.default_button)
        
        # # Sliders for Canny edge detection parameters
        # self.lower_slider_label = QLabel("Lower Threshold:", self)
        # self.button_layout.addWidget(self.lower_slider_label)
        # self.lower_slider = QSlider(Qt.Horizontal, self)
        # self.lower_slider.setMinimum(0)
        # self.lower_slider.setMaximum(255)
        # self.lower_slider.setValue(30)
        # self.lower_slider.setTickPosition(QSlider.TicksBelow)
        # self.button_layout.addWidget(self.lower_slider)

        # self.upper_slider_label = QLabel("Upper Threshold:", self)
        # self.button_layout.addWidget(self.upper_slider_label)
        # self.upper_slider = QSlider(Qt.Horizontal, self)
        # self.upper_slider.setMinimum(0)
        # self.upper_slider.setMaximum(255)
        # self.upper_slider.setValue(90)
        # self.upper_slider.setTickPosition(QSlider.TicksBelow)
        # self.button_layout.addWidget(self.upper_slider)

        # Connect slider value change signals to corresponding slots
        # self.lower_slider.valueChanged.connect(self.update_processed_image_parameters)
        # self.upper_slider.valueChanged.connect(self.update_processed_image_parameters)

        self.blur_layout = QHBoxLayout()
        self.blur_label = QLabel("Change Blur:", self)
        self.blur_layout.addWidget(self.blur_label)

        

        self.button_layout.addLayout(self.blur_layout)
        self.blur_slider = QSlider(Qt.Horizontal, self)
        self.blur_slider.setMinimum(5)
        self.blur_slider.setMaximum(35)
        self.blur_slider.setValue(21)
        self.blur_slider.setTickInterval(2)
        self.blur_slider.setTickPosition(QSlider.TicksBelow)
        self.button_layout.addWidget(self.blur_slider)
        self.blur_value_label = QLabel(f"{self.blur_slider.value()}", self)
        self.blur_layout.addWidget(self.blur_value_label)
        
        self.blur_slider.valueChanged.connect(self.update_processed_image_parameters)
        
        self.contrast_layout = QHBoxLayout()
        self.contrast_label = QLabel("Change Contrast:", self)
        self.contrast_layout.addWidget(self.contrast_label)

        

        self.button_layout.addLayout(self.contrast_layout)
        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setMinimum(1)
        self.contrast_slider.setMaximum(10)
        self.contrast_slider.setValue(1)
        self.contrast_slider.setTickInterval(2)
        self.contrast_slider.setTickPosition(QSlider.TicksBelow)
        self.button_layout.addWidget(self.contrast_slider)
        self.contrast_value_label = QLabel(f"{self.contrast_slider.value()}", self)
        self.contrast_layout.addWidget(self.contrast_value_label)
        
        self.contrast_slider.valueChanged.connect(self.update_processed_image_parameters)
        
        # Heading for parameter inputs
        self.parameter_heading = QLabel("Parameter Inputs", self)
        self.parameter_heading.setAlignment(Qt.AlignCenter)
        self.parameter_heading.setFixedSize(120, 30)
        self.button_layout.addWidget(self.parameter_heading)

        self.scale = QLineEdit(self)
        self.scale.setPlaceholderText("Needle Width :")
        self.parameter_heading.setFixedSize(120, 30)
        self.button_layout.addWidget(self.scale)

        # Input fields for parameters
        self.rho1_input = QLineEdit(self)
        self.rho1_input.setPlaceholderText("ρ1 :")
        self.parameter_heading.setFixedSize(120, 30)
        self.button_layout.addWidget(self.rho1_input)

        self.rho2_input = QLineEdit(self)
        self.rho2_input.setPlaceholderText("ρ2 :")
        self.parameter_heading.setFixedSize(120, 30)
        self.button_layout.addWidget(self.rho2_input)

        # self.T_input = QLineEdit(self)
        # self.T_input.setPlaceholderText("T :")
        # self.parameter_heading.setFixedSize(120, 30)
        # self.button_layout.addWidget(self.T_input)

        # self.P_input = QLineEdit(self)
        # self.P_input.setPlaceholderText("P :")
        # self.parameter_heading.setFixedSize(120, 30)
        # self.button_layout.addWidget(self.P_input)

        # Calculate button
        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.clicked.connect(self.calculate_parameters)
        self.button_layout.addWidget(self.calculate_button)
        self.parameter_heading.setFixedSize(120, 30)

        # Adjust spacing between dropdown menu and capture image button
        self.button_layout.addSpacing(10) 

        self.camera_feed_window = CameraFeedWindow()
        self.camera_feed_window.show()
    
    def restore_defaults(self):
        try:
            if self.originalDefaultImage is not None:
                self.display_image(self.originalDefaultImage)
        except Exception as e:
            print(e)
    
    def closeEvent(self, event):
        # Close the camera feed window if it exists
        if self.camera_feed_window is not None:
            self.camera_feed_window.close()

        if self.camera_feed_window.processed_image_window is not None:
            self.camera_feed_window.processed_image_window.close()

        event.accept()
        
    def open_camera_feed(self):
        if self.camera_feed_window is None or not self.camera_feed_window.isVisible():
            self.camera_feed_window = CameraFeedWindow()
            self.camera_feed_window.show()
        else:
            self.camera_feed_window.activateWindow()
    def single_capture(self):
        ret, frame = self.camera_feed_window.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            self.originalDefaultImage=frame
            
            self.display_image(frame, "captures/captured_image.png")

    def burst_capture(self):
        for i in range(10):
            ret, frame = self.camera_feed_window.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                self.display_image(frame, f"burst_captures/image_{i+1}.png")

    def browse_image(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if filepath:
            image = cv2.imread(filepath)
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.display_image(image)
                
                
    def update_processed_image_parameters (self):
        # lower_threshold = self.lower_slider.value()
        # upper_threshold = self.upper_slider.value()
        blur_value=self.blur_slider.value()
        if blur_value %2==0:
            blur_value=blur_value+1
        self.blur_value_label.setText(str(blur_value))
        
        contrast_factor=self.contrast_slider.value()
        self.contrast_value_label.setText(str(contrast_factor))

        # Update the processed image window with the new Canny parameters
        self.camera_feed_window.processed_image_window.update_canny_parameters(30, 90,blur_value, contrast_factor)
        
        
    def calculate_parameters(self, image):
        # T = self.T_input.text()
        # P = self.P_input.text()
    
        try:
            finalImage, sigma=self.find_IFT(self.imageToBeProcessed)
            self.display_image(finalImage)
            message = f"IFT value is: {sigma}"
            QMessageBox.information(self, "Sum of Input Values", message)
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "Error", "Please enter appropriate values") 
        # try:
        #     total_sum = float(rho1) + float(rho2) + float(T) + float(P)
        #     message = f"Sum of input values: {total_sum}"
        #     QMessageBox.information(self, "Sum of Input Values", message)
        # except ValueError:
        #     QMessageBox.warning(self, "Error", "Invalid input values. Please enter valid numbers.") 

    def display_image(self, image, filepath=None):
        if filepath:
            cv2.imwrite(filepath, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            print("Image captured successfully:", filepath)
            
        self.imageToBeProcessed = image
        original_height, original_width = image.shape[:2]
        aspect_ratio = original_width / original_height
        new_width = int(480 * aspect_ratio)
        
        # Resize the image with the new dimensions
        image_resized = cv2.resize(image, (new_width, 480))
        
        # Convert the resized image to QImage
        displayImage = QImage(image_resized.data, image_resized.shape[1], image_resized.shape[0], image_resized.strides[0], QImage.Format_RGB888)
        
        # Convert QImage to QPixmap for drawing gridlines
        pixmap = QPixmap.fromImage(displayImage)

        self.central_widget.setPixmap(pixmap)
        self.central_widget.show()

        
        # finalImage = QImage(finalImage.data, finalImage.shape[1], finalImage.shape[0], QImage.Format_RGB888)
        # pixmap = QPixmap.fromImage(finalImage)
        # self.central_widget.setPixmap(pixmap)
        # self.central_widget.show()
        
        
    
    def find_IFT(self, frame):
        
        
        # Get all the values
        blur_value=self.blur_slider.value()
        rho1 = float(self.rho1_input.text().strip())
        rho2 = float(self.rho2_input.text().strip())
        width_needle=float(self.scale.text().strip())
        width_needle=float(width_needle/1000)
        contrast_factor = self.contrast_slider.value()
        
        if blur_value %2==0:
            blur_value=blur_value+1 #ensure blur value is odd always
            
    
        original_image=frame.copy()
        self.originalDefaultImage=original_image #set global variabe of default image
        image_copy = frame.copy()
        
        # steps start to apply contrast if contrast>1
        if contrast_factor>1:     
            image_float = np.float32(image_copy)           
            mean_brightness = np.mean(image_float)
            contrasted_image = contrast_factor * (image_float - mean_brightness) + mean_brightness
            contrasted_image = np.clip(contrasted_image, 0, 255)
            image_copy = np.uint8(contrasted_image) #store in back in image_copy
            
            
        gray = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
        edges = cv2.Canny(blurred, 30, 90)
        # find out edges of drop
        
        color_edges = np.zeros_like(image_copy) # create a null image with size of image_copy

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find out the contours from edges

        for contour in contours:
            # Approximate the contour to make a polygon
            epsilon = 0.000001 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            # Draw the contour on the color edges
            cv2.drawContours(color_edges, [approx], -1, (255, 255, 255), 2)
        
        # find out edges from color_edges again
        gray = cv2.cvtColor(color_edges, cv2.COLOR_BGR2GRAY) 
        blurred = cv2.GaussianBlur(gray, (1, 1), 0) # apply very little blur
        edges = cv2.Canny(blurred, 30, 90)
        
        image_copy = original_image.copy() #temporary line

        # find out parallel lines from the new edges. keep threshold and minlength low
        lines = cv2.HoughLinesP(edges, 3, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)

        # Select the two separate parallel lines of the needle
        def select_distinct_lines(all_lines):
            selected_lines=[] 
            if(lines.any() and len(lines)>=2):
                for line1, line2 in itertools.combinations(lines, 2):
                    x1_line1, y1_line1, x2_line1, y2_line1 = line1[0]
                    x1_line2, y1_line2, x2_line2, y2_line2 = line2[0]

                    # Check if the difference in x-coordinates is greater than 10 units
                    if abs(x1_line1 - x1_line2) > 10 or abs(x2_line1 - x2_line2) > 10:
                        print("Distinct lines found")
                        selected_lines.append(line1)
                        selected_lines.append(line2)
                        pixel_width_temp=abs(x1_line1-x1_line2)
                        #get the lowest y coordinate of the needle line
                        npoint_y= int(max(float((y1_line1+y2_line1)/2),float((y1_line2+y2_line2)/2)))
                        
                        # get the points
                        npoint1=(x1_line1,npoint_y) 
                        npoint2=(x1_line2,npoint_y) 
                        
                        return selected_lines, pixel_width_temp, npoint1,npoint2
                    
        # invoke that function
        selected_lines, pixel_width, needle_point1, needle_point2=select_distinct_lines(lines)
        
        image_cc=image_copy.copy()  #temporary line
        for line in selected_lines: #temporary line
            x1, y1, x2, y2 = line[0] #temporary line
            cv2.line(image_cc, (x1, y1), (x2, y2), (0, 255, 0),2) #temporary line
        
        
        # Rotation of image starts here, till needle is vertical
        
        rotation_step = 1  # declare rotation step
        max_iterations = 180 // rotation_step  # Define a maximum number of iterations to prevent infinite loop
        
        # function to check if needle i within tolerance angle
        def is_vertical(angle, tolerance=1):
            return abs(abs(angle) - 90) <= tolerance
        
        # find out points and angle of second line (arbitrary)
        x1, y1, x2, y2 = selected_lines[1][0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
        print("Original Angle: ", angle)

        # store copies of original, edges and colored edges
        rotated_image = image_copy.copy()
        rotated_edges = edges.copy()
        
        
        
        for _ in range(max_iterations):
            if is_vertical(angle):
                break

            # Rotate the image by the defined step size and store it temporarily
            rotated_edges_temp = imutils.rotate_bound(edges, rotation_step)
            rotated_image_temp = imutils.rotate_bound(image_copy, rotation_step)

            # Extract the angle of the first selected line in the rotated image
            edges_rotated = cv2.Canny(rotated_edges_temp, 30, 90)
            lines_rotated = cv2.HoughLinesP(edges_rotated, 3, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

            # again find out the distinct lines
            
            selected_lines_rotated, _, needle_point1,needle_point2=select_distinct_lines(lines_rotated)
            
            if selected_lines_rotated is not None and len(selected_lines_rotated) >= 2:
                x1, y1, x2, y2 = selected_lines_rotated[1][0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
                # print("Angle after rotation: ", angle)
                rotated_edges = rotated_edges_temp
                rotated_image = rotated_image_temp
        
            elif lines_rotated is not None and len(lines_rotated) >= 2:
                x1, y1, x2, y2 = lines_rotated[1][0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
                # print("Angle after rotation: ", angle)
                rotated_edges = rotated_edges_temp
                rotated_image = rotated_image_temp
            else:
                print("No lines detected, breaking loop.")
                break
            

            # Stop rotation of image if the angle is closer to vertical
            if is_vertical(angle):
                break
        
        
        
        image_ccc=rotated_image.copy() # temporary line
        contours, _ = cv2.findContours(rotated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        lowerbound=1
        upperbound=1
        distance=0
        lowermost_point_y=-9999999
        
        
        for contour in contours:
            # Find the lowermost point in the contour based on its ordinate
            new_lowermost_point = max(contour, key=lambda point: point[0][1])
            if new_lowermost_point[0][1] > lowermost_point_y:
                lowermost_point_y=new_lowermost_point[0][1]
                lowermost_point=np.array([new_lowermost_point[0][0]+9, new_lowermost_point[0][1]])
                print("Lowermost point:", lowermost_point_y)
                cv2.circle(image_ccc, tuple(lowermost_point), 3, (0, 0, 255), -1)
                selected_contour=contour # temporary line
        
        
        for contour in contours:
            epsilon = 0.000001 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            cv2.drawContours(image_ccc, [approx], -1, (0, 0, 255), 1) # draw the contours, temporary line
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image_ccc, (x+lowerbound, y), (x + w-upperbound, y + h), (0, 255, 0), 2)
            w=w+lowerbound+upperbound
            horizontal_line_y = lowermost_point[1] - w
            cv2.line(image_ccc, (x+lowerbound, horizontal_line_y), (x + w-upperbound, horizontal_line_y),(255, 0, 0), 2)
            intersection_points = []
            for point in contour:
                px, py = point[0]
                if py <= horizontal_line_y+2  and py>=horizontal_line_y-2 :
                    intersection_points.append(point[0])
            for point in intersection_points:
                cv2.circle(image_ccc, tuple(point), 3, (255, 0, 0), -1)
            print("Found ",len(intersection_points), "intersection points")
            # print("Horizontal line y-coordinate:", horizontal_line_y)

            if len(intersection_points) >= 2:
                for i in range(len(intersection_points) - 1):
                    for j in range(i + 1, len(intersection_points)):
                        point1 = intersection_points[i]
                        point2 = intersection_points[j]
                        newDistance=math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
                        # print(f"Distance between {point1} and {point2}: {newDistance:.2f}")
                        if newDistance>distance:
                            distance = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
                    
        try:
            print(f"Final Distance between {point1} and {point2}: {distance:.2f}")
        except Exception as e:
            print(e)
        
        # compute shape parameter
        S=distance/w
        # set the scale
        scale=width_needle/pixel_width
        D=w*scale
        print("D: ", round(D, 5), "m")
        print("S: ",S)
        
        # compute empirical constants
        def assign_values(S):
            if 0.401 <= S < 0.46:
                A, B4, B3, B2, B1, B0 = 2.56651, 0.3272, 0, 0.97553, 0.84059, 0.18069
            elif 0.46 <= S < 0.59:
                A, B4, B3, B2, B1, B0 = 2.59725, 0.31968, 0, 0.46898, 0.50059, 0.13261
            elif 0.59 <= S < 0.68:
                A, B4, B3, B2, B1, B0 = 2.62435, 0.31522, 0, 0.11714, 0.15756, 0.05285
            elif 0.68 <= S < 0.9:
                A, B4, B3, B2, B1, B0 = 2.64267, 0.31345, 0, 0.09155, 0.14701, 0.05877
            elif 0.9 <= S <= 1.00:
                A, B4, B3, B2, B1, B0 = 2.84636, 0.30715, 0.69116, 1.08315, 0.18341, 0.2097
            else:
                raise ValueError("S value is out of the expected range.")
                # A, B4, B3, B2, B1, B0 = 0,0,0,0,0,0
            return A, B4, B3, B2, B1, B0

        A, B4, B3, B2, B1, B0 = assign_values(S)
        print(f"A: {A}, B4: {B4}, B3: {B3}, B2: {B2}, B1: {B1}, B0: {B0}")

        InvH= B4/(pow(S,A))+ B3*(pow(S,3))-B2*(pow(S,2))+B1*S-B0 #calculate 1/H

        sigma=1000*(abs(rho1-rho2))*9.81*(pow(D,2)) *InvH # compute IFT

        print("sigma: ",sigma, "mN/m")
        
        
        # cv2.line(image_ccc, needle_point1,needle_point2,(255, 0, 0), 2)
        
        
        return image_ccc, sigma
        
        
        
        
        
        
        
        
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraGUI()
    window.show()
    sys.exit(app.exec_())
