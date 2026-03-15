import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox,QCheckBox, QPushButton, QVBoxLayout, QWidget, QLineEdit, QFileDialog, QMessageBox,QSizePolicy,QSlider,QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen,QTransform
from PyQt5.QtCore import QTimer, Qt, QPoint,pyqtSignal
from PyQt5.QtMultimedia import QCameraInfo
import cv2
import numpy as np
import imutils
import itertools
import os
import math
import datetime
import random
import string
import csv

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Directory created: {directory}")
        except Exception as e:
            print(f"Failed to create directory {directory}: {e}")
    else:
        print(f"Directory already exists: {directory}")


        
        
class CameraFeedWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Live Camera Feed")
        self.setGeometry(100, 100, 640, 480)
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(0, 0, 640, 480)
        self.capture = cv2.VideoCapture(0)
        self.processed_image_window = ProcessedImageWindow()
        self.processed_image_window.show()
        self.update_camera_feed()

    def update_camera_feed(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.imageWithOriginalAspect=frame
            newframe = cv2.resize(frame, (640,480))
            image = QImage(newframe.data, newframe.shape[1], newframe.shape[0], QImage.Format.Format_RGB888)
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
        self.contrast_factor = contrast_factor
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
        
class DisplayImageProcessedWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Image")
        self.setGeometry(100, 100, 640, 480)
        self.image_label = QLabel(self)
        self.image_label.setGeometry(0, 0, 640, 480)
        self.lower_threshold = 30  # Default lower threshold
        self.upper_threshold = 90 
        self.blur_value = 21
        self.contrast_factor = 1.0

        
    def update_canny_parameters(self, lower_threshold, upper_threshold ,blur_value, contrast_factor):
        self.contrast_factor = contrast_factor
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.blur_value = blur_value
        if blur_value %2==0:
            self.blur_value=blur_value+1
    def update_processed_image(self, frame):
        
        image_copy = frame.copy()
        height, width=image_copy.shape[:2]
        ratio=float(width)/height
        self.setGeometry(100, 100, int(540*ratio), 540)
        self.image_label.setGeometry(0, 0,int(540*ratio), 540)
        
        image_float = np.float32(image_copy)

        contrast_factor = self.contrast_factor
        mean_brightness = np.mean(image_float)
        contrasted_image = contrast_factor * (image_float - mean_brightness) + mean_brightness
        contrasted_image = np.clip(contrasted_image, 0, 255)
        image_copy = np.uint8(contrasted_image)

        gray = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (self.blur_value, self.blur_value), 0)
        edges = cv2.Canny(blurred, self.lower_threshold, self.upper_threshold)
        color_edges = np.zeros_like(image_copy)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            epsilon = 0.000001 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            cv2.drawContours(color_edges, [approx], -1, (255, 255, 255), 1)
        
        edges_resized = cv2.resize(color_edges, (int(540*ratio), 540))
        image = QImage(edges_resized.data, edges_resized.shape[1], edges_resized.shape[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)
        self.image_label.show()
        
        
        
        
class CameraGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera GUI")
        self.setGeometry(400, 100, 1120, 660)

        # Central widget to hold captured image
        self.central_widget = QLabel(self)
        self.central_widget.setFixedSize(960, 540)
        self.setCentralWidget(self.central_widget)

        # Container widget for buttons
        self.button_container = QWidget(self)
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_container.setGeometry(970, 0, 150, 650)
        self.button_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.camera_dropdown = QComboBox()
        self.camera_dropdown.setFixedSize(120, 30)
        self.button_layout.addWidget(self.camera_dropdown)
        
        # Populate the dropdown with available cameras
        self.populate_camera_dropdown()
        self.camera_dropdown.currentIndexChanged.connect(self.on_camera_selected)
        
        
        self.open_camera_button = QPushButton("Open Camera")
        self.open_camera_button.setFixedSize(120, 30)
        self.open_camera_button.clicked.connect(self.open_camera_feed)
        self.button_layout.addWidget(self.open_camera_button)
        # Capture image button
        self.capture_button = QPushButton("Capture Image")
        self.capture_button.setFixedSize(120, 30)
        self.capture_button.clicked.connect(self.single_capture)
        self.button_layout.addWidget(self.capture_button)

        # Browse image button
        self.browse_button = QPushButton("Browse Image")
        self.browse_button.setFixedSize(120, 30)
        self.browse_button.clicked.connect(self.browse_image)
        self.button_layout.addWidget(self.browse_button)
        
        self.default_button = QPushButton("Restore Defaults")
        self.default_button.setFixedSize(120, 30)
        self.default_button.clicked.connect(self.restore_defaults)
        self.button_layout.addWidget(self.default_button)
        
        self.isInverted=False
        self.checkbox = QCheckBox("Inverted Drop", self)
        self.checkbox.setChecked(self.isInverted)  # Initial state
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        self.button_layout.addWidget(self.checkbox)
        
        
        self.multipleChecks=False
        self.checkbox_mutliple = QCheckBox("Multiple Checks", self)
        self.checkbox_mutliple.setChecked(self.multipleChecks)  # Initial state
        self.checkbox_mutliple.stateChanged.connect(self.on_checkbox_multiple_changed)
        self.button_layout.addWidget(self.checkbox_mutliple)
        
        self.blur_layout = QHBoxLayout()
        self.blur_label = QLabel("Change Blur:", self)
        self.blur_layout.addWidget(self.blur_label)

        

        self.button_layout.addLayout(self.blur_layout)
        self.blur_slider = QSlider(Qt.Horizontal, self)
        self.blur_slider.setMinimum(5)
        self.blur_slider.setMaximum(45)
        self.blur_slider.setValue(23)
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
        
        
        # Zoom Slider
        self.zoom_layout = QHBoxLayout()
        self.zoom_label = QLabel("Zoom:", self)
        self.zoom_layout.addWidget(self.zoom_label)

        self.button_layout.addLayout(self.zoom_layout)
        self.zoom_slider = QSlider(Qt.Horizontal, self)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(5)  # Allow up to 5x zoom
        self.zoom_slider.setValue(1)  # Default zoom level is 1 (no zoom)
        self.zoom_slider.setTickInterval(1)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.button_layout.addWidget(self.zoom_slider)
        self.zoom_value_label = QLabel(f"{self.zoom_slider.value()}x", self)
        self.zoom_layout.addWidget(self.zoom_value_label)

        self.zoom_slider.valueChanged.connect(self.update_zoom)
        
        self.arrow_layout = QHBoxLayout()

        # Rotate left button
        self.bblowerbound = QLineEdit(self)
        self.bblowerbound.setPlaceholderText("Lower")
        self.bblowerbound.setFixedSize(60, 25)
        # self.rotate_left_button.clicked.connect(lambda: self.rotate_image(-1))
        self.arrow_layout.addWidget(self.bblowerbound)

        # Rotate right button
        self.bbupperbound = QLineEdit(self)
        self.bbupperbound.setPlaceholderText("Upper")
        self.bbupperbound.setFixedSize(60, 25)
        # self.rotate_left_button.clicked.connect(lambda: self.rotate_image(-1))
        self.arrow_layout.addWidget(self.bbupperbound)
        # Add the button layout to the main layout of your window
        self.button_layout.addLayout(self.arrow_layout)
        
        # Heading for medium inputs
        self.name_heading = QLabel("Medium Names", self)
        self.name_heading.setAlignment(Qt.AlignCenter)
        self.name_heading.setFixedSize(120, 30)
        self.button_layout.addWidget(self.name_heading)
        
        # Input fields for mediums
        self.m1 = QLineEdit(self)
        self.m1.setPlaceholderText("Medium 1 :")
        self.name_heading.setFixedSize(120, 30)
        self.button_layout.addWidget(self.m1)

        self.m2 = QLineEdit(self)
        self.m2.setPlaceholderText("Medium 2 :")
        self.name_heading.setFixedSize(120, 30)
        self.button_layout.addWidget(self.m2)
        
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

        # Calculate button
        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.clicked.connect(self.calculate_parameters)
        self.button_layout.addWidget(self.calculate_button)
        self.parameter_heading.setFixedSize(120, 30)

        # Adjust spacing between dropdown menu and capture image button
        self.button_layout.addSpacing(10) 
        
        
        self.current_image = None
        self.current_rotation_angle = 0
        
        
        self.camera_feed_window = CameraFeedWindow()
        self.camera_feed_window.show()
        
        
        
    
                
    def populate_camera_dropdown(self):
        self.cameras = QCameraInfo.availableCameras()
        if self.cameras:
            for index, camera_info in enumerate(self.cameras):
                print(camera_info.description())
                self.camera_dropdown.addItem(f"{camera_info.description()}")
        else:
            self.camera_dropdown.addItem("No Cameras Found")
            
    def on_camera_selected(self, index):
        if self.camera_feed_window.capture is not None:
            self.camera_feed_window.capture.release()
        
        if self.cameras and index < len(self.cameras):
            camera_info = self.cameras[index]
            camera_index = self.cameras.index(camera_info)
            self.camera_feed_window.capture = cv2.VideoCapture(camera_index)
            
    def qimage_to_numpy(image):
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  # Assuming 4 channels (RGBA)
        return arr
    def on_checkbox_changed(self, state):
        if state ==  Qt.Checked:
            self.isInverted=True
            print("Inverted Drop Checkbox is checked")
        else:
            self.isInverted=False
            print("Inverted Drop Checkbox is unchecked")
            
    def on_checkbox_multiple_changed(self, state):
        if state ==  Qt.Checked:
            self.multipleChecks=True
            print("Multiple Checkbox is checked")
        else:
            self.multipleChecks=False
            print("Multiple Checkbox is unchecked")
    def rotate_image(self, angle):
        if self.current_image:
            self.current_rotation_angle += angle
            transform = QTransform().rotate(self.current_rotation_angle)
            rotated_image = self.current_image.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            imagearr=self.qimage_to_numpy(rotated_image)
            self.display_image(imagearr)
    
    def restore_defaults(self):
        try:
            if self.originalDefaultImage is not None:
                self.display_image(self.originalDefaultImage)
        except Exception as e:
            print(e)
    
    def closeEvent(self, event):
        # Close the camera feed window if it exists
        if self.camera_feed_window is not None:
            self.camera_feed_window.capture.release()
            self.camera_feed_window.close()

        if self.camera_feed_window.processed_image_window is not None:
            self.camera_feed_window.capture.release()
            self.camera_feed_window.processed_image_window.close()
        try:    
            if self.display_processed_window is not None:
                self.display_processed_window.close()
        except Exception as e:
            pass
        event.accept()
        
    def open_camera_feed(self):
        if self.camera_feed_window is None or not self.camera_feed_window.isVisible():
            self.camera_feed_window = CameraFeedWindow()
            self.camera_feed_window.show()
        else:
            self.camera_feed_window.activateWindow()
    def update_zoom(self):
        zoom_factor = self.zoom_slider.value()
        self.zoom_value_label.setText(f"{zoom_factor}x")
        try:
            if self.imageToBeProcessed is not None:
                self.display_image(self.imageToBeProcessed, zoom_factor=zoom_factor)
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "Error", "No image found") 
    def single_capture(self):
        ret, frame = self.camera_feed_window.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            newframe = cv2.resize(frame, (640, 480))
            self.originalDefaultImage=frame
            self.current_image = QImage(newframe.data, newframe.shape[1], newframe.shape[0], newframe.strides[0], QImage.Format.Format_RGB888)
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            script_dir = os.path.dirname(os.path.abspath(__file__))
            captures_dir = os.path.join(script_dir, "captures")
            ensure_directory_exists(captures_dir)
            filename = os.path.join(captures_dir, f"{timestamp}_{random_string}.png")
            self.display_image(frame,filename)

    def burst_capture(self):
        for i in range(10):
            ret, frame = self.camera_feed_window.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.display_image(frame, f"burst_captures/image_{i+1}.png")

    def browse_image(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if filepath:
            image = cv2.imread(filepath)
            self.originalDefaultImage=image
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                # newframe = cv2.resize(image, (640, 480))
                self.display_image(image)
                
                
    def update_processed_image_parameters (self):
        try:
            blur_value=self.blur_slider.value()
            if blur_value %2==0:
                blur_value=blur_value+1
            self.blur_value_label.setText(str(blur_value))
            
            contrast_factor=self.contrast_slider.value()
            self.contrast_value_label.setText(str(contrast_factor))
            self.camera_feed_window.processed_image_window.update_canny_parameters(30, 90,blur_value, contrast_factor)
            try:
                # Update the processed image window with the new Canny parameters
                if self.originalDefaultImage is not None:
                    self.display_processed_window = DisplayImageProcessedWindow()
                    self.display_processed_window.update_canny_parameters(30, 90,blur_value, contrast_factor)
                    self.display_processed_window.show()
                    self.display_processed_window.update_processed_image(self.originalDefaultImage)
            except Exception as e:
                pass
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "Error", "No image found") 
        
    def calculate_parameters(self, image):
    
        try:
            if self.multipleChecks ==False:
                finalImage, sigma=self.find_IFT(self.imageToBeProcessed)
                filename=None
                if sigma>0:
                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y%m%d_%H%M%S")
                    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    processed_dir = os.path.join(script_dir, "processed")
                    ensure_directory_exists(processed_dir)
                    filename = os.path.join(processed_dir, f"{timestamp}_{random_string}.png")
                self.display_image(finalImage,filename)
                message = f"IFT value is: {sigma}"
                QMessageBox.information(self, "Result", message)
            else:
                
                def filter_outliers(data):
                    # Sort the data
                    sorted_data = sorted(data)
                    
                    filtered_data=[]
                    for x in sorted_data:
                        if 0<x <426:
                            filtered_data.append(x)
                    
                    return filtered_data


                
                blur_original=self.blur_slider.value()
                if blur_original %2==0:
                    blur_original=blur_original+1 
                current_blur=blur_original-8
                if current_blur<0:
                    current_blur=1
                    
                

                sigma_values=[]
                blur_values=[]
                finalImages=[]
                for i in range(9):
                    self.blur_slider.setValue(current_blur)
                    blur_values.append(current_blur)
                    finalImage=self.imageToBeProcessed
                    sigma=0
                    try:
                        finalImage, sigma = self.find_IFT(self.imageToBeProcessed )
                    except Exception as e:
                        pass
                    current_blur=current_blur+2
                    self.display_image(finalImage)
                    sigma_values.append(sigma)
                    if sigma>0:
                        finalImages.append(finalImage)
                    self.restore_defaults()
                    
                for processed_image in finalImages:
                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y%m%d_%H%M%S")
                    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    processed_dir = os.path.join(script_dir, "processed")
                    ensure_directory_exists(processed_dir)
                    filename = os.path.join(processed_dir, f"{timestamp}_{random_string}.png")    
                    cv2.imwrite(filename, cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))
                    
                self.blur_slider.setValue(blur_original)    
                message = "IFT values for different blur values: \n\n"
                error_blurs=[]
                for blur, sigma in zip(blur_values, sigma_values):
                    if sigma>0:
                        message += f"IFT: {sigma:.5f}   Blur: {blur}\n"
                    else:
                        error_blurs.append(blur)
                        
                filtered_values = filter_outliers(sigma_values)
                print(filtered_values)
                median_value = np.median(filtered_values)
                message+=f"\nMedian value is: {median_value:.5f}\n"
                
                if len(error_blurs)!=0:
                    message+="\nErrors occured for blur = [ "
                    for i in range(len(error_blurs)):
                        if i == len(error_blurs)-1:
                            message += f"{error_blurs[i]}"
                        else:
                            message += f"{error_blurs[i]}, "
                    message+= f" ]\n"       
                # Show the message in a QMessageBox
                QMessageBox.information(self, "Results", message)    
                
                
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "Error", "Something went wrong") 

    def display_image(self, image, filepath=None, zoom_factor=1):
        if filepath:
            cv2.imwrite(filepath, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            print("Image captured successfully:", filepath)

        self.imageToBeProcessed = image
        original_height, original_width = image.shape[:2]
        aspect_ratio = original_width / original_height
        new_width = int(540 * aspect_ratio)

        if zoom_factor > 1:
            center_x, center_y = original_width // 2, original_height // 2
            zoomed_width, zoomed_height = original_width // zoom_factor, original_height // zoom_factor
            top_left_x = max(center_x - zoomed_width // 2, 0)
            top_left_y = max(center_y - zoomed_height // 2, 0)
            bottom_right_x = min(top_left_x + zoomed_width, original_width)
            bottom_right_y = min(top_left_y + zoomed_height, original_height)
            cropped_image = image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
            image_resized = cv2.resize(cropped_image, (new_width, 540))
        else:
            image_resized = cv2.resize(image, (new_width, 540))

        display_image = QImage(image_resized.data, image_resized.shape[1], image_resized.shape[0], image_resized.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(display_image)
        self.central_widget.setPixmap(pixmap)
        self.central_widget.show()

        
    def append_to_csv(self,data):
        # Determine the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Script directory: {script_dir}")
        
        # Construct the path to the results directory and CSV file
        results_dir = os.path.join(script_dir, "results")
        filenameResults = os.path.join(results_dir, "Results.csv")
        print(f"Results directory: {results_dir}")
        print(f"CSV file path: {filenameResults}")
        
        # Ensure the results directory exists
        ensure_directory_exists(results_dir)
        
        # Check if the CSV file already exists
        file_exists = os.path.isfile(filenameResults)
        print(f"File exists: {file_exists}")
        
        # Open the CSV file in append mode ('a')
        try:
            with open(filenameResults, 'a', newline='') as file:
                writer = csv.writer(file)
                
                # If the file does not exist, write the header
                if not file_exists:
                    writer.writerow([ 
                        'Timestamp', 'Medium 1', 'Density 1 (kg/m^3)', 'Medium 2', 'Density 2 (kg/m^3)', 'IFT (mN/m)',
                        'Temperature (K)', 'Pressure (bar)', 'Salinity (g/L)',
                        'Inverted Drop', 'd', 'D', 'S', 'InvH'
                    ])
                
                # Write the data
                writer.writerow(data)
                print(f"Data appended to CSV file: {data}")
        except Exception as e:
            print(f"Failed to write to CSV file {filenameResults}: {e}")
    def find_IFT(self, frame):
        
        heightFrame, widthFrame =frame.shape[:2]
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
        lines = cv2.HoughLinesP(edges, 3, np.pi/180, threshold=50, minLineLength=50, maxLineGap=20)

        # Select the two separate parallel lines of the needle
                    
        selected_lines=[] 
        if(lines.any() and len(lines)>=2):
            for line1, line2 in itertools.combinations(lines, 2):
                x1_line1, y1_line1, x2_line1, y2_line1 = line1[0]
                x1_line2, y1_line2, x2_line2, y2_line2 = line2[0]

                # Check if the difference in x-coordinates is greater than 10 units
                if abs(x1_line1 - x1_line2) > 10 or abs(x2_line1 - x2_line2) > 10:
                    # print("Distinct lines found")
                    selected_lines.append(line1)
                    selected_lines.append(line2)
                    pixel_width=abs(x1_line1-x1_line2)
                    
                    break
                    
        # selected_lines, pixel_width, needle_point1, needle_point2=select_distinct_lines(lines)
        print("Pixel Width: ", pixel_width)
        
        
        
        # Rotation of image starts here, till needle is vertical
        rotation_step = 1  # Declare rotation step
        max_iterations = 180 // rotation_step  # Define a maximum number of iterations to prevent infinite loop

        # Function to check if needle is within tolerance angle
        tolerance=0.5
        def is_vertical(angle):
            return abs(abs(angle) - 90) <= tolerance

        # Find out points and angle of the second line (arbitrary)
        x1, y1, x2, y2 = selected_lines[1][0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
        print("Original Angle: ", angle)

        # Store copies of the original, edges, and colored edges
        rotated_image = image_copy.copy()
        rotated_edges = edges.copy()
        rotated_color_edges = color_edges.copy()

        # Rotate the image until the needle is vertical
        for _ in range(max_iterations):
            if is_vertical(angle):
                break

            # Rotate the image by the defined step size and store it temporarily
            if angle > 0:  # If angle is positive, rotate clockwise
                rotated_edges_temp = imutils.rotate(rotated_edges, -rotation_step)
                rotated_image_temp = imutils.rotate(rotated_image, -rotation_step)
                rotated_color_edges_temp = imutils.rotate(rotated_color_edges, -rotation_step)
            else:  # If angle is negative, rotate counterclockwise
                rotated_edges_temp = imutils.rotate(rotated_edges, +rotation_step)
                rotated_image_temp = imutils.rotate(rotated_image, +rotation_step)
                rotated_color_edges_temp = imutils.rotate(rotated_color_edges, +rotation_step)

            # Extract the angle of the first selected line in the rotated image
            edges_rotated = cv2.Canny(rotated_edges_temp, 30, 90)
            lines_rotated = cv2.HoughLinesP(edges_rotated, 3, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=20)

            if lines_rotated is not None and len(lines_rotated) >= 2:
                x1, y1, x2, y2 = lines_rotated[1][0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
                rotated_edges = rotated_edges_temp
                rotated_image = rotated_image_temp
                rotated_color_edges = rotated_color_edges_temp
            else:
                print("No lines detected, breaking loop.")
                break

            # Stop rotation of image if the angle is closer to vertical
            if is_vertical(angle):
                break
        
        print("Angle after rotation: ", angle)
        
        
        image_ccc=rotated_color_edges.copy() # temporary line
        contours, _ = cv2.findContours(rotated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        
        
        if self.isInverted == False:
            lowerbound=int(self.bblowerbound.text()) if self.bblowerbound.text()!='' else -1
            upperbound=int(self.bbupperbound.text()) if self.bbupperbound.text()!='' else 1
            distance=0
            lowermost_point_y=-9999999
            
            
            for contour in contours:
                # Find the lowermost point in the contour based on its ordinate
                new_lowermost_point = max(contour, key=lambda point: point[0][1])
                if new_lowermost_point[0][1] >= lowermost_point_y:
                    lowermost_point_y=new_lowermost_point[0][1]
                    lowermost_point_x=new_lowermost_point[0][0]
                    
                    lowermost_point=np.array([lowermost_point_x+2, lowermost_point_y])
                    # temporary line
                    
            print("Lowermost point:", lowermost_point_y)
            cv2.circle(image_ccc, tuple(lowermost_point), 3, (0, 0, 255), -1)
            
            maxArea=-99999
            for contour in contours:
                epsilon = 0.000001 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                # cv2.drawContours(image_ccc, [approx], -1, (0, 0, 255), 1) # draw the contours, temporary line
                xt, yt, wt, ht = cv2.boundingRect(contour)
                area=wt*ht
                if area>maxArea:
                    selected_contour=contour
                    x,y,w,h= cv2.boundingRect(contour)
                    
            
            
            
            cv2.rectangle(image_ccc, (x+lowerbound, y), (x + w+upperbound, y + h), (0, 255, 0), 2)
            w=w-lowerbound+upperbound
            horizontal_line_y = lowermost_point[1] - w
            cv2.line(image_ccc, (x+lowerbound, horizontal_line_y), (x + w+upperbound, horizontal_line_y),(255, 0, 0), 2)
            intersection_points = []
            for point in selected_contour:
                px, py = point[0]
                if py <= horizontal_line_y+2  and py>=horizontal_line_y-2 :
                    intersection_points.append(point[0])
            # for point in intersection_points:
            #     cv2.circle(image_ccc, tuple(point), 3, (255, 0, 0), -1)
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
                            cv2.circle(image_ccc, tuple(point1), 3, (255, 0, 0), -1)
                            cv2.circle(image_ccc, tuple(point2), 3, (255, 0, 0), -1)
                                
                                
                        
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
            
            m1Name = "Medium 1" if self.m1.text()=='' else self.m1.text()
            m2Name = "Medium 2" if self.m2.text()=='' else self.m2.text()
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y/%m/%d_%H:%M:%S")
            if sigma>0 and sigma <500:
                now=datetime.datetime.now()
                datatobeAppended=[timestamp,m1Name,rho1,m2Name,rho2,sigma,'298','1','NaN' ,self.isInverted, distance*scale, D, S, InvH ]
                self.append_to_csv(datatobeAppended)
            
            return image_ccc, sigma
        
        else:
            lowerbound=int(self.bblowerbound.text()) if self.bblowerbound.text()!='' else -1
            upperbound=int(self.bbupperbound.text()) if self.bbupperbound.text()!='' else 1
            distance=0
            lowermost_point_y=heightFrame
            
            
            for contour in contours:
                # Find the lowermost point in the contour based on its ordinate
                new_lowermost_point = min(contour, key=lambda point: point[0][1])
                if new_lowermost_point[0][1] <= lowermost_point_y:
                    lowermost_point_y=new_lowermost_point[0][1]
                    lowermost_point_x=new_lowermost_point[0][0]
                    
                    lowermost_point=np.array([lowermost_point_x+2, lowermost_point_y])
                    # temporary line
                    
            print("Lowermost point:", lowermost_point_y)
            cv2.circle(image_ccc, tuple(lowermost_point), 3, (0, 0, 255), -1)
            
            maxArea=-99999
            for contour in contours:
                epsilon = 0.000001 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                # cv2.drawContours(image_ccc, [approx], -1, (0, 0, 255), 1) # draw the contours, temporary line
                xt, yt, wt, ht = cv2.boundingRect(contour)
                area=wt*ht
                if area>maxArea:
                    selected_contour=contour
                    x,y,w,h= cv2.boundingRect(contour)
                    
            
            
            
            cv2.rectangle(image_ccc, (x+lowerbound, y), (x + w+upperbound, y + h), (0, 255, 0), 2)
            w=w-lowerbound+upperbound
            horizontal_line_y = lowermost_point[1] + w
            cv2.line(image_ccc, (x+lowerbound, horizontal_line_y), (x + w+upperbound, horizontal_line_y),(255, 0, 0), 2)
            intersection_points = []
            for point in selected_contour:
                px, py = point[0]
                if py <= horizontal_line_y+2  and py>=horizontal_line_y-2 :
                    intersection_points.append(point[0])
            # for point in intersection_points:
            #     cv2.circle(image_ccc, tuple(point), 3, (255, 0, 0), -1)
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
                            cv2.circle(image_ccc, tuple(point1), 3, (255, 0, 0), -1)
                            cv2.circle(image_ccc, tuple(point2), 3, (255, 0, 0), -1)
                                
                                
                        
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
                return A, B4, B3, B2, B1, B0

            A, B4, B3, B2, B1, B0 = assign_values(S)
            print(f"A: {A}, B4: {B4}, B3: {B3}, B2: {B2}, B1: {B1}, B0: {B0}")

            InvH= B4/(pow(S,A))+ B3*(pow(S,3))-B2*(pow(S,2))+B1*S-B0 #calculate 1/H

            sigma=1000*(abs(rho1-rho2))*9.81*(pow(D,2)) *InvH # compute IFT

            print("sigma: ",sigma, "mN/m")
            
            
            
            m1Name = "Medium 1" if self.m1.text()=='' else self.m1.text()
            m2Name = "Medium 2" if self.m2.text()=='' else self.m2.text()
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y/%m/%d_%H:%M:%S")
            if sigma>0 and sigma <500:
                now=datetime.datetime.now()
                datatobeAppended=[timestamp,m1Name,rho1,m2Name,rho2,sigma,'298','1','NaN' ,self.isInverted, distance*scale, D, S, InvH ]
                self.append_to_csv(datatobeAppended)
                
                
            return image_ccc, sigma
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraGUI()
    window.show()
    sys.exit(app.exec_())
