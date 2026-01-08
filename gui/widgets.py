"""
Custom widgets for Huffman Compressor GUI
"""

import os
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DropZone(QFrame):
    """Custom drop zone widget for file selection with drag & drop support"""
    fileDropped = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)  # Remove vertical margins
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Center all items vertically
        
        # File path label
        self.file_label = QLabel("Select a file or drag & drop here...")
        self.file_label.setObjectName("fileLabel")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.file_label.setMinimumWidth(350)
        self.file_label.setWordWrap(False)
        layout.addWidget(self.file_label, 1, Qt.AlignmentFlag.AlignVCenter)
        
        # Browse button
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setFixedSize(100, 36)
        layout.addWidget(self.browse_btn, 0, Qt.AlignmentFlag.AlignVCenter)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragOver", True)
            self.style().polish(self)
    
    def dragLeaveEvent(self, event):
        self.setProperty("dragOver", False)
        self.style().polish(self)
    
    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragOver", False)
        self.style().polish(self)
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.fileDropped.emit(file_path)
    
    def set_file_path(self, path):
        if path:
            display_name = os.path.basename(path)
            self.file_label.setText(display_name)
            self.file_label.setToolTip(path)
            self.file_label.setStyleSheet("color: #ffffff;")
        else:
            self.file_label.setText("Select a file or drag & drop here...")
            self.file_label.setStyleSheet("color: #6b7280;")


class StatsPanel(QFrame):
    """Inline statistics panel showing compression/decompression results"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statsPanel")
        self.setVisible(False)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Compression Statistics")
        title.setObjectName("statsPanelTitle")
        layout.addWidget(title)
        
        # Stats grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(8)
        
        # Original size
        self.original_label = QLabel("Original Size")
        self.original_label.setObjectName("statsLabel")
        self.original_value = QLabel("—")
        self.original_value.setObjectName("statsValue")
        grid.addWidget(self.original_label, 0, 0)
        grid.addWidget(self.original_value, 0, 1)
        
        # Result size
        self.result_label = QLabel("Compressed Size")
        self.result_label.setObjectName("statsLabel")
        self.result_value = QLabel("—")
        self.result_value.setObjectName("statsValue")
        grid.addWidget(self.result_label, 0, 2)
        grid.addWidget(self.result_value, 0, 3)
        
        # Ratio
        self.ratio_label = QLabel("Compression Ratio")
        self.ratio_label.setObjectName("statsLabel")
        self.ratio_value = QLabel("—")
        self.ratio_value.setObjectName("statsValueGreen")
        grid.addWidget(self.ratio_label, 1, 0)
        grid.addWidget(self.ratio_value, 1, 1)
        
        # Time taken
        self.time_label = QLabel("Time Taken")
        self.time_label.setObjectName("statsLabel")
        self.time_value = QLabel("—")
        self.time_value.setObjectName("statsValue")
        grid.addWidget(self.time_label, 1, 2)
        grid.addWidget(self.time_value, 1, 3)
        
        layout.addLayout(grid)
    
    def format_size(self, size_bytes):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    def update_stats(self, original_size, result_size, time_taken, is_compression=True):
        """Update the statistics display"""
        self.original_value.setText(self.format_size(original_size))
        self.result_value.setText(self.format_size(result_size))
        self.time_value.setText(f"{time_taken:.3f}s")
        
        if is_compression:
            self.result_label.setText("Compressed Size")
            if original_size > 0:
                ratio = ((original_size - result_size) / original_size) * 100
                if ratio >= 0:
                    self.ratio_value.setText(f"{ratio:.1f}% saved")
                    self.ratio_value.setObjectName("statsValueGreen")
                else:
                    self.ratio_value.setText(f"{abs(ratio):.1f}% larger")
                    self.ratio_value.setObjectName("statsValueRed")
                self.ratio_value.style().polish(self.ratio_value)
        else:
            self.result_label.setText("Decompressed Size")
            if result_size > 0:
                ratio = ((result_size - original_size) / result_size) * 100
                self.ratio_value.setText(f"Restored {ratio:.1f}%")
                self.ratio_value.setObjectName("statsValueGreen")
                self.ratio_value.style().polish(self.ratio_value)
        
        self.setVisible(True)
    
    def hide_stats(self):
        """Hide the stats panel"""
        self.setVisible(False)
