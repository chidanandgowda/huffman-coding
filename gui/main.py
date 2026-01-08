"""
Huffman Compressor - Main Application
Modern PyQt6 GUI with stats panel, tree visualization, and smart file detection
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QFrame, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from .widgets import DropZone, StatsPanel
from .tree_visualizer import HuffmanTreeWindow
from .styles import MAIN_STYLESHEET


class CompressionWorker(QThread):
    """Worker thread for compression/decompression operations"""
    finished = pyqtSignal(bool, str, dict)  # success, message, stats
    
    def __init__(self, operation, input_file, output_file, exe_path):
        super().__init__()
        self.operation = operation
        self.input_file = input_file
        self.output_file = output_file
        self.exe_path = exe_path
    
    def run(self):
        try:
            # Get original file size
            original_size = os.path.getsize(self.input_file)
            
            # Record start time
            start_time = time.time()
            
            result = subprocess.run(
                [self.exe_path, self.operation, self.input_file, self.output_file],
                capture_output=True,
                text=True
            )
            
            # Record end time
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                # Get result file size
                result_size = os.path.getsize(self.output_file) if os.path.exists(self.output_file) else 0
                
                # Read frequency data for tree visualization (only for compression)
                frequency_data = {}
                if self.operation == "compress":
                    frequency_data = self._read_frequency_data(self.input_file)
                
                stats = {
                    'original_size': original_size,
                    'result_size': result_size,
                    'time': elapsed_time,
                    'frequency_data': frequency_data,
                    'is_compression': self.operation == "compress"
                }
                
                action = 'compressed' if self.operation == 'compress' else 'decompressed'
                self.finished.emit(True, f"Successfully {action}!", stats)
            else:
                self.finished.emit(False, result.stderr or "Operation failed", {})
        except Exception as e:
            self.finished.emit(False, str(e), {})
    
    def _read_frequency_data(self, input_file):
        """Read file and calculate character frequencies"""
        frequency_data = {}
        try:
            with open(input_file, 'rb') as f:
                content = f.read()
                for byte in content:
                    char = chr(byte) if byte < 128 else f"0x{byte:02x}"
                    frequency_data[char] = frequency_data.get(char, 0) + 1
        except Exception:
            pass
        return frequency_data


class HuffmanCompressor(QMainWindow):
    """Main application window"""
    
    # File extensions that should trigger compress action
    COMPRESSIBLE_EXTENSIONS = {'.txt', '.md', '.json', '.xml', '.html', '.css', '.js', 
                               '.py', '.c', '.h', '.cpp', '.java', '.csv', '.log', '.ini'}
    # File extensions that should trigger decompress action
    COMPRESSED_EXTENSIONS = {'.bin', '.huff', '.compressed'}
    
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.last_frequency_data = None
        self.tree_window = None
        self.exe_path = self._find_executable()
        self._setup_window()
        self._setup_ui()
        self._apply_styles()
        self._update_button_states()
    
    def _find_executable(self):
        """Find the huffman executable"""
        base_dir = Path(__file__).parent.parent
        possible_paths = [
            base_dir / "huffman.exe",
            base_dir / "huffman",
            base_dir / "releases" / "huffman.exe",
            base_dir / "releases" / "huffman",
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)
        return str(base_dir / "huffman.exe")
    
    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Huffman Compressor")
        self.setFixedSize(600, 520)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def _setup_ui(self):
        """Build the user interface"""
        # Central widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(25, 20, 25, 25)
        main_layout.setSpacing(0)
        
        # Title bar with window controls
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 20)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Close button (red)
        close_btn = QPushButton()
        close_btn.setFixedSize(14, 14)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5f56;
                border-radius: 7px;
                border: none;
            }
            QPushButton:hover { background-color: #ff3b30; }
        """)
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        controls_layout.addWidget(close_btn)
        
        # Minimize button (yellow)
        min_btn = QPushButton()
        min_btn.setFixedSize(14, 14)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffbd2e;
                border-radius: 7px;
                border: none;
            }
            QPushButton:hover { background-color: #f5a623; }
        """)
        min_btn.clicked.connect(self.showMinimized)
        min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        controls_layout.addWidget(min_btn)
        
        title_bar.addLayout(controls_layout)
        title_bar.addStretch()
        main_layout.addLayout(title_bar)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("Huffman Compressor")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Lossless data compression using Huffman algorithm")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(30)
        
        # Input section card
        input_card = QFrame()
        input_card.setObjectName("inputCard")
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(25, 20, 25, 25)
        input_card_layout.setSpacing(15)
        
        input_label = QLabel("Input File")
        input_label.setObjectName("inputLabel")
        input_card_layout.addWidget(input_label)
        
        # File type indicator
        self.file_type_label = QLabel("")
        self.file_type_label.setObjectName("subtitleLabel")
        self.file_type_label.setVisible(False)
        input_card_layout.addWidget(self.file_type_label)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.browse_btn.clicked.connect(self._browse_file)
        self.drop_zone.fileDropped.connect(self._on_file_dropped)
        input_card_layout.addWidget(self.drop_zone)
        
        main_layout.addWidget(input_card)
        main_layout.addSpacing(20)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.compress_btn = QPushButton("Compress")
        self.compress_btn.setObjectName("compressBtn")
        self.compress_btn.setFixedSize(150, 48)
        self.compress_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.compress_btn.clicked.connect(self._compress)
        buttons_layout.addWidget(self.compress_btn)
        
        self.decompress_btn = QPushButton("Decompress")
        self.decompress_btn.setObjectName("decompressBtn")
        self.decompress_btn.setFixedSize(150, 48)
        self.decompress_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.decompress_btn.clicked.connect(self._decompress)
        buttons_layout.addWidget(self.decompress_btn)
        
        self.view_tree_btn = QPushButton("View Tree")
        self.view_tree_btn.setObjectName("viewTreeBtn")
        self.view_tree_btn.setFixedSize(100, 48)
        self.view_tree_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_tree_btn.clicked.connect(self._show_tree)
        self.view_tree_btn.setVisible(False)
        buttons_layout.addWidget(self.view_tree_btn)
        
        main_layout.addLayout(buttons_layout)
        main_layout.addSpacing(15)
        
        # Stats panel (inline, not popup)
        self.stats_panel = StatsPanel()
        main_layout.addWidget(self.stats_panel)
        
        main_layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        main_layout.addWidget(self.progress_bar)
    
    def _apply_styles(self):
        """Apply the stylesheet"""
        self.setStyleSheet(MAIN_STYLESHEET)
    
    def _detect_file_type(self, file_path):
        """Detect if file should be compressed or decompressed"""
        if not file_path:
            return None
        
        ext = Path(file_path).suffix.lower()
        
        if ext in self.COMPRESSED_EXTENSIONS:
            return "decompress"
        elif ext in self.COMPRESSIBLE_EXTENSIONS:
            return "compress"
        else:
            # For unknown extensions, check if it's likely binary
            try:
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)
                    # If file contains many non-printable chars, treat as binary/compressed
                    non_printable = sum(1 for b in chunk if b < 32 and b not in (9, 10, 13))
                    if len(chunk) > 0 and non_printable / len(chunk) > 0.3:
                        return "decompress"
            except:
                pass
            return "compress"  # Default to compress
    
    def _update_button_states(self):
        """Update button visibility based on selected file"""
        file_type = self._detect_file_type(self.selected_file) if self.selected_file else None
        
        if file_type == "compress":
            self.compress_btn.setVisible(True)
            self.compress_btn.setEnabled(True)
            self.decompress_btn.setVisible(False)
            self.file_type_label.setText("Text file detected - ready for compression")
            self.file_type_label.setVisible(True)
        elif file_type == "decompress":
            self.compress_btn.setVisible(False)
            self.decompress_btn.setVisible(True)
            self.decompress_btn.setEnabled(True)
            self.file_type_label.setText("Compressed file detected - ready for decompression")
            self.file_type_label.setVisible(True)
        else:
            # No file selected
            self.compress_btn.setVisible(True)
            self.compress_btn.setEnabled(False)
            self.decompress_btn.setVisible(True)
            self.decompress_btn.setEnabled(False)
            self.file_type_label.setVisible(False)
    
    def _browse_file(self):
        """Open file dialog to select a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "All Files (*);;Text Files (*.txt);;Binary Files (*.bin)"
        )
        if file_path:
            self._on_file_dropped(file_path)
    
    def _on_file_dropped(self, file_path):
        """Handle file selection"""
        self.selected_file = file_path
        self.drop_zone.set_file_path(file_path)
        self._update_button_states()
        self.stats_panel.hide_stats()
        self.view_tree_btn.setVisible(False)
    
    def _compress(self):
        """Start compression operation"""
        if not self.selected_file:
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Compressed File",
            os.path.splitext(self.selected_file)[0] + ".bin",
            "Binary Files (*.bin)"
        )
        if output_path:
            self._run_operation("compress", self.selected_file, output_path)
    
    def _decompress(self):
        """Start decompression operation"""
        if not self.selected_file:
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Decompressed File",
            os.path.splitext(self.selected_file)[0] + "_decompressed.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if output_path:
            self._run_operation("decompress", self.selected_file, output_path)
    
    def _run_operation(self, operation, input_file, output_file):
        """Execute compress/decompress operation in background"""
        self.compress_btn.setEnabled(False)
        self.decompress_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.worker = CompressionWorker(operation, input_file, output_file, self.exe_path)
        self.worker.finished.connect(self._on_operation_finished)
        self.worker.start()
    
    def _on_operation_finished(self, success, message, stats):
        """Handle operation completion"""
        self._update_button_states()
        self.progress_bar.setVisible(False)
        
        if success and stats:
            # Update stats panel
            self.stats_panel.update_stats(
                stats['original_size'],
                stats['result_size'],
                stats['time'],
                stats['is_compression']
            )
            
            # Store frequency data for tree visualization
            if stats.get('frequency_data'):
                self.last_frequency_data = stats['frequency_data']
                self.view_tree_btn.setVisible(True)
        
        if not success:
            self._show_message("Error", message, QMessageBox.Icon.Critical)
    
    def _show_tree(self):
        """Show the Huffman tree visualization"""
        if self.last_frequency_data:
            self.tree_window = HuffmanTreeWindow(self.last_frequency_data)
            self.tree_window.show()
    
    def _show_message(self, title, message, icon):
        """Show a styled message box"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec()
    
    # Window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = HuffmanCompressor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
