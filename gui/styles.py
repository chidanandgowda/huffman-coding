"""
Stylesheet definitions for Huffman Compressor GUI
"""

MAIN_STYLESHEET = """
    #centralWidget {
        background-color: #1a1a2e;
        border-radius: 16px;
        border: 1px solid #2d2d44;
    }
    
    #titleLabel {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
        font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
    }
    
    #subtitleLabel {
        font-size: 14px;
        color: #8b8b9e;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #inputCard {
        background-color: #252540;
        border-radius: 12px;
        border: 1px solid #3d3d5c;
    }
    
    #inputLabel {
        font-size: 14px;
        font-weight: 600;
        color: #4ade80;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #dropZone {
        background-color: #1a1a2e;
        border: 2px dashed #4ade80;
        border-radius: 8px;
        min-height: 50px;
    }
    
    #dropZone[dragOver="true"] {
        border-color: #22d3ee;
        background-color: #1e293b;
    }
    
    #fileLabel {
        font-size: 14px;
        color: #6b7280;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #browseBtn {
        background-color: #3d3d5c;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #browseBtn:hover {
        background-color: #4a4a6a;
    }
    
    #browseBtn:pressed {
        background-color: #353550;
    }
    
    #compressBtn {
        background-color: #22c55e;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #compressBtn:hover {
        background-color: #16a34a;
    }
    
    #compressBtn:pressed {
        background-color: #15803d;
    }
    
    #compressBtn:disabled {
        background-color: #374151;
        color: #6b7280;
    }
    
    #decompressBtn {
        background-color: #3b82f6;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #decompressBtn:hover {
        background-color: #2563eb;
    }
    
    #decompressBtn:pressed {
        background-color: #1d4ed8;
    }
    
    #decompressBtn:disabled {
        background-color: #374151;
        color: #6b7280;
    }
    
    #viewTreeBtn {
        background-color: #8b5cf6;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #viewTreeBtn:hover {
        background-color: #7c3aed;
    }
    
    #viewTreeBtn:pressed {
        background-color: #6d28d9;
    }
    
    #progressBar {
        background-color: #374151;
        border: none;
        border-radius: 2px;
    }
    
    #progressBar::chunk {
        background-color: #22c55e;
        border-radius: 2px;
    }
    
    /* Stats Panel Styles */
    #statsPanel {
        background-color: #252540;
        border-radius: 12px;
        border: 1px solid #3d3d5c;
    }
    
    #statsPanelTitle {
        font-size: 14px;
        font-weight: 600;
        color: #8b5cf6;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #statsLabel {
        font-size: 13px;
        color: #9ca3af;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #statsValue {
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #statsValueGreen {
        font-size: 13px;
        font-weight: 600;
        color: #4ade80;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #statsValueRed {
        font-size: 13px;
        font-weight: 600;
        color: #f87171;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    QMessageBox {
        background-color: #1a1a2e;
    }
    
    QMessageBox QLabel {
        color: #ffffff;
    }
    
    QMessageBox QPushButton {
        background-color: #3b82f6;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        min-width: 80px;
    }
    
    QMessageBox QPushButton:hover {
        background-color: #2563eb;
    }
"""

TREE_WINDOW_STYLESHEET = """
    QWidget#treeWindow {
        background-color: #1a1a2e;
    }
    
    #treeTitle {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #treeSubtitle {
        font-size: 12px;
        color: #8b8b9e;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #legendLabel {
        font-size: 11px;
        color: #9ca3af;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #closeBtn {
        background-color: #ef4444;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 20px;
    }
    
    #closeBtn:hover {
        background-color: #dc2626;
    }
"""
