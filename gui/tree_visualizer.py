"""
Huffman Tree Visualization Widget
Renders the Huffman tree structure using QPainter with zoom support
"""

import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QWheelEvent, QTransform

from .styles import TREE_WINDOW_STYLESHEET


class TreeNode:
    """Represents a node in the Huffman tree"""
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
        self.x = 0
        self.y = 0
    
    def is_leaf(self):
        return self.left is None and self.right is None


class TreeCanvas(QWidget):
    """Canvas widget for drawing the Huffman tree with zoom and pan support"""
    
    NODE_RADIUS = 25
    LEVEL_HEIGHT = 80
    MIN_NODE_SPACING = 60
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = None
        self.zoom_level = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        # Pan offset
        self.pan_x = 0
        self.pan_y = 0
        self._last_mouse_pos = None
        self._is_panning = False
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #1e1e36;")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
    
    def set_zoom(self, zoom):
        """Set zoom level"""
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, zoom))
        if self.root:
            tree_width = self._calculate_tree_width(self.root)
            tree_height = self._get_tree_height(self.root) * self.LEVEL_HEIGHT + 100
            self.setMinimumSize(
                int(max(800, tree_width + 100) * self.zoom_level),
                int(max(600, tree_height) * self.zoom_level)
            )
        self.update()
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.set_zoom(self.zoom_level * 1.1)
        else:
            self.set_zoom(self.zoom_level / 1.1)
        event.accept()
    
    def mousePressEvent(self, event):
        """Start panning on left click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Pan the view while dragging"""
        if self._is_panning and self._last_mouse_pos:
            delta = event.position() - self._last_mouse_pos
            self.pan_x += delta.x() / self.zoom_level
            self.pan_y += delta.y() / self.zoom_level
            self._last_mouse_pos = event.position()
            self.update()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Stop panning"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = False
            self._last_mouse_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
    
    def reset_pan(self):
        """Reset pan to origin"""
        self.pan_x = 0
        self.pan_y = 0
        self.update()
    
    def fit_to_view(self, viewport_width, viewport_height):
        """Calculate zoom level to fit entire tree in viewport"""
        if self.root is None:
            return
        
        tree_width = self._calculate_tree_width(self.root) + 100  # Add margins
        tree_height = self._get_tree_height(self.root) * self.LEVEL_HEIGHT + 120  # Add margins
        
        # Calculate zoom to fit
        zoom_x = viewport_width / tree_width if tree_width > 0 else 1.0
        zoom_y = viewport_height / tree_height if tree_height > 0 else 1.0
        
        # Use the smaller zoom to ensure everything fits
        optimal_zoom = min(zoom_x, zoom_y, 1.0)  # Cap at 1.0 (100%)
        optimal_zoom = max(optimal_zoom, self.min_zoom)  # Respect minimum zoom
        
        self.zoom_level = optimal_zoom
        self.pan_x = 0
        self.pan_y = 0
        
        # Update size based on new zoom
        self.setMinimumSize(
            int(max(800, tree_width) * self.zoom_level),
            int(max(600, tree_height) * self.zoom_level)
        )
        self.update()
    
    def set_tree(self, frequency_data):
        """Build and set the Huffman tree from frequency data"""
        if not frequency_data:
            self.root = None
            self.update()
            return
        
        # Build Huffman tree from frequency data
        self.root = self._build_tree(frequency_data)
        
        # Calculate node positions
        if self.root:
            tree_width = self._calculate_tree_width(self.root)
            self._calculate_positions(self.root, 0, tree_width, 0)
            self.setMinimumSize(
                int(max(800, tree_width + 100) * self.zoom_level),
                int(max(600, self._get_tree_height(self.root) * self.LEVEL_HEIGHT + 100) * self.zoom_level)
            )
        
        self.update()
    
    def _build_tree(self, frequency_data):
        """Build Huffman tree using priority queue approach"""
        nodes = [TreeNode(char=char, freq=freq) for char, freq in frequency_data.items() if freq > 0]
        
        if not nodes:
            return None
        
        if len(nodes) == 1:
            return nodes[0]
        
        while len(nodes) > 1:
            nodes.sort(key=lambda x: x.freq)
            left = nodes.pop(0)
            right = nodes.pop(0)
            parent = TreeNode(freq=left.freq + right.freq, left=left, right=right)
            nodes.append(parent)
        
        return nodes[0]
    
    def _calculate_tree_width(self, node):
        """Calculate total width needed for the tree"""
        if node is None:
            return 0
        if node.is_leaf():
            return self.MIN_NODE_SPACING
        return self._calculate_tree_width(node.left) + self._calculate_tree_width(node.right)
    
    def _get_tree_height(self, node):
        """Get the height of the tree"""
        if node is None:
            return 0
        return 1 + max(self._get_tree_height(node.left), self._get_tree_height(node.right))
    
    def _calculate_positions(self, node, x_start, x_end, level):
        """Calculate x, y positions for each node"""
        if node is None:
            return
        
        node.x = (x_start + x_end) / 2
        node.y = level * self.LEVEL_HEIGHT + 60
        
        if node.left:
            mid = (x_start + x_end) / 2
            self._calculate_positions(node.left, x_start, mid, level + 1)
        
        if node.right:
            mid = (x_start + x_end) / 2
            self._calculate_positions(node.right, mid, x_end, level + 1)
    
    def paintEvent(self, event):
        """Draw the tree"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Apply zoom and pan transforms
        painter.scale(self.zoom_level, self.zoom_level)
        painter.translate(self.pan_x, self.pan_y)
        
        if self.root is None:
            painter.setPen(QColor("#6b7280"))
            painter.setFont(QFont("Segoe UI", 14))
            rect = QRectF(0, 0, self.width() / self.zoom_level, self.height() / self.zoom_level)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, 
                           "No tree data available\nCompress a file to see the tree")
            return
        
        self._draw_node(painter, self.root)
    
    def _draw_node(self, painter, node):
        """Recursively draw nodes and edges"""
        if node is None:
            return
        
        if node.left:
            self._draw_edge(painter, node, node.left, "0")
            self._draw_node(painter, node.left)
        
        if node.right:
            self._draw_edge(painter, node, node.right, "1")
            self._draw_node(painter, node.right)
        
        self._draw_single_node(painter, node)
    
    def _draw_edge(self, painter, parent, child, label):
        """Draw an edge between parent and child nodes"""
        pen = QPen(QColor("#4a4a6a"), 2)
        painter.setPen(pen)
        painter.drawLine(int(parent.x), int(parent.y + self.NODE_RADIUS),
                        int(child.x), int(child.y - self.NODE_RADIUS))
        
        mid_x = (parent.x + child.x) / 2
        mid_y = (parent.y + child.y) / 2
        
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor("#8b5cf6"))
        
        offset = -15 if label == "0" else 15
        painter.drawText(int(mid_x + offset - 5), int(mid_y), label)
    
    def _draw_single_node(self, painter, node):
        """Draw a single node"""
        x, y = int(node.x), int(node.y)
        r = self.NODE_RADIUS
        
        if node.is_leaf():
            painter.setBrush(QBrush(QColor("#22c55e")))
            painter.setPen(QPen(QColor("#16a34a"), 2))
        else:
            painter.setBrush(QBrush(QColor("#8b5cf6")))
            painter.setPen(QPen(QColor("#7c3aed"), 2))
        
        painter.drawEllipse(x - r, y - r, r * 2, r * 2)
        
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        
        if node.is_leaf():
            char_display = node.char if node.char and len(node.char) == 1 and node.char.isprintable() else "."
            if node.char == ' ':
                char_display = "_"
            elif node.char == '\n':
                char_display = "\\n"
            elif node.char == '\t':
                char_display = "\\t"
            painter.drawText(x - r, y - r, r * 2, r * 2, 
                           Qt.AlignmentFlag.AlignCenter, char_display)
        else:
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(x - r, y - r, r * 2, r * 2, 
                           Qt.AlignmentFlag.AlignCenter, str(node.freq))


class HuffmanTreeWindow(QWidget):
    """Window displaying the Huffman tree visualization"""
    
    def __init__(self, frequency_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Huffman Tree Visualization")
        self.resize(1000, 700)  # Larger default size
        self.setMinimumSize(800, 600)
        self.setObjectName("treeWindow")
        self.setStyleSheet(TREE_WINDOW_STYLESHEET)
        self._setup_ui()
        
        if frequency_data:
            self.set_frequency_data(frequency_data)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QVBoxLayout()
        header.setSpacing(5)
        
        title = QLabel("Huffman Tree")
        title.setObjectName("treeTitle")
        header.addWidget(title)
        
        subtitle = QLabel("Visual representation of the compression tree structure (scroll to zoom)")
        subtitle.setObjectName("treeSubtitle")
        header.addWidget(subtitle)
        
        layout.addLayout(header)
        
        # Legend and zoom controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        
        for color, label in [("#8b5cf6", "Internal Node (frequency)"), 
                            ("#22c55e", "Leaf Node (character)")]:
            legend_item = QHBoxLayout()
            legend_item.setSpacing(8)
            
            color_box = QFrame()
            color_box.setFixedSize(16, 16)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 8px;")
            legend_item.addWidget(color_box)
            
            legend_label = QLabel(label)
            legend_label.setObjectName("legendLabel")
            legend_item.addWidget(legend_label)
            
            controls_layout.addLayout(legend_item)
        
        controls_layout.addStretch()
        
        # Zoom hint
        zoom_hint = QLabel("Scroll to zoom | Drag to pan")
        zoom_hint.setObjectName("legendLabel")
        controls_layout.addWidget(zoom_hint)
        
        # Reset button
        reset_btn = QPushButton("Reset View")
        reset_btn.setObjectName("resetBtn")
        reset_btn.setFixedSize(80, 28)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d5c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a6a;
            }
        """)
        reset_btn.clicked.connect(self._reset_view)
        controls_layout.addWidget(reset_btn)
        
        layout.addLayout(controls_layout)
        
        # Scroll area for tree canvas
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #3d3d5c;
                border-radius: 8px;
                background-color: #1e1e36;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #252540;
                width: 12px;
                height: 12px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #4a4a6a;
                border-radius: 6px;
                min-height: 30px;
                min-width: 30px;
            }
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background-color: #5a5a7a;
            }
        """)
        
        self.tree_canvas = TreeCanvas()
        self.scroll.setWidget(self.tree_canvas)
        layout.addWidget(self.scroll, 1)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _reset_view(self):
        """Reset view to show entire tree"""
        # Get scroll area viewport size
        viewport = self.scroll.viewport()
        self.tree_canvas.fit_to_view(viewport.width(), viewport.height())
    
    def set_frequency_data(self, frequency_data):
        """Set the frequency data and update the tree visualization"""
        self.tree_canvas.set_tree(frequency_data)
