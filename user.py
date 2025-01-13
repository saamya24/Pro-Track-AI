import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap

class ValidationSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validation System using Video Analytics")
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint)

        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Add spacing at the top
        self.main_layout.addSpacing(10)

        # Add title label
        self.title_label = QLabel("Process Validation System")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px;
            padding: 10px;
        """)
        self.main_layout.addWidget(self.title_label)

        # Create video display with increased size
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(QSize(800, 600))
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setStyleSheet("""
            QLabel {
                margin: 20px;
                padding: 10px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        self.main_layout.addWidget(self.video_label)

        # Create statistics grid
        self.stats_layout = QGridLayout()
        self.stats_layout.setSpacing(20)
        
        stat_style = """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
        """
        
        # Total Cycles
        self.total_cycles_label = QLabel("Total Cycles:")
        self.total_cycles_value = QLabel("0")
        self.total_cycles_label.setStyleSheet(stat_style)
        self.total_cycles_value.setStyleSheet(stat_style)
        self.stats_layout.addWidget(self.total_cycles_label, 0, 0)
        self.stats_layout.addWidget(self.total_cycles_value, 0, 1)
        
        # Correct Cycles
        self.correct_cycles_label = QLabel("Correct Cycles:")
        self.correct_cycles_value = QLabel("0")
        self.correct_cycles_label.setStyleSheet(stat_style)
        self.correct_cycles_value.setStyleSheet(stat_style)
        self.stats_layout.addWidget(self.correct_cycles_label, 0, 2)
        self.stats_layout.addWidget(self.correct_cycles_value, 0, 3)
        
        # Incorrect Cycles
        self.incorrect_cycles_label = QLabel("Incorrect Cycles:")
        self.incorrect_cycles_value = QLabel("0")
        self.incorrect_cycles_label.setStyleSheet(stat_style)
        self.incorrect_cycles_value.setStyleSheet(stat_style)
        self.stats_layout.addWidget(self.incorrect_cycles_label, 0, 4)
        self.stats_layout.addWidget(self.incorrect_cycles_value, 0, 5)

        self.main_layout.addSpacing(10)
        self.main_layout.addLayout(self.stats_layout)
        self.main_layout.addSpacing(10)

        # Create status message label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px;
        """)
        self.main_layout.addWidget(self.status_label)

        # Create Reset button
        self.reset_button = QPushButton("Reset Cycle")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                min-width: 150px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.reset_button.clicked.connect(self.reset_cycle)
        self.main_layout.addWidget(self.reset_button)
        
        self.main_layout.addSpacing(20)

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        
        # Initialize cycle counters
        self.total_cycles = 0
        self.correct_cycles = 0
        self.incorrect_cycles = 0

        # Load ROI definitions
        self.roi_definitions = self.load_roi_definitions()

        # Set up video timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def load_roi_definitions(self):
        roi_definitions = []
        try:
            with open('roi_definitions.txt', 'r') as f:
                for line in f:
                    label, x1, y1, x2, y2 = line.strip().split(',')
                    roi_definitions.append({
                        'label': label,
                        'start': (int(x1), int(y1)),
                        'end': (int(x2), int(y2))
                    })
        except FileNotFoundError:
            print("ROI definitions file not found")
        return roi_definitions

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Draw ROIs on the frame
            for roi in self.roi_definitions:
                # Draw rectangle
                cv2.rectangle(frame, roi['start'], roi['end'], (0, 255, 0), 2)
                
                # Add label above the rectangle
                label_position = (roi['start'][0], roi['start'][1] - 10)
                cv2.putText(frame, roi['label'], label_position,
                          cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Convert frame to Qt format
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale the image to fit the label while maintaining aspect ratio
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)

    def reset_cycle(self):
        # Reset current cycle and update status
        self.status_label.setText("Cycle Reset")
        self.total_cycles += 1
        self.incorrect_cycles += 1
        self.update_cycle_counts()

    def update_cycle_counts(self):
        # Update the display of cycle counts
        self.total_cycles_value.setText(str(self.total_cycles))
        self.correct_cycles_value.setText(str(self.correct_cycles))
        self.incorrect_cycles_value.setText(str(self.incorrect_cycles))

    def closeEvent(self, event):
        # Clean up resources when closing
        self.cap.release()

if __name__ == '__main__':
    app = QApplication([])
    window = ValidationSystem()
    window.show()
    app.exec_()