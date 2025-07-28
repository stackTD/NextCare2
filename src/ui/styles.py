"""
Professional UI styling for NextCare2 application
"""

from ..utils.constants import *

def get_application_style():
    """Get the main application stylesheet"""
    return f"""
    /* Main Application Styling */
    QApplication {{
        background-color: {BACKGROUND_COLOR};
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        font-size: 11px;
    }}
    
    /* Main Windows */
    QMainWindow {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    
    QWidget {{
        background-color: transparent;
        color: {TEXT_COLOR};
    }}
    
    /* Card-like containers */
    .card {{
        background-color: {CARD_COLOR};
        border: 1px solid #E1E8ED;
        border-radius: 8px;
        padding: 16px;
        margin: 8px;
    }}
    
    /* Headers and Titles */
    QLabel.header {{
        font-size: 18px;
        font-weight: bold;
        color: {PRIMARY_COLOR};
        padding: 8px 0px;
    }}
    
    QLabel.subheader {{
        font-size: 14px;
        font-weight: 600;
        color: {SECONDARY_COLOR};
        padding: 4px 0px;
    }}
    
    QLabel.title {{
        font-size: 24px;
        font-weight: bold;
        color: {PRIMARY_COLOR};
        padding: 16px 0px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 11px;
        min-height: 24px;
    }}
    
    QPushButton:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    
    QPushButton:pressed {{
        background-color: #1a2330;
    }}
    
    QPushButton:disabled {{
        background-color: #BDC3C7;
        color: #7F8C8D;
    }}
    
    QPushButton.primary {{
        background-color: {PRIMARY_COLOR};
    }}
    
    QPushButton.secondary {{
        background-color: {SECONDARY_COLOR};
    }}
    
    QPushButton.success {{
        background-color: {SUCCESS_COLOR};
    }}
    
    QPushButton.warning {{
        background-color: {WARNING_COLOR};
    }}
    
    QPushButton.danger {{
        background-color: {ERROR_COLOR};
    }}
    
    QPushButton.outline {{
        background-color: transparent;
        color: {PRIMARY_COLOR};
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    QPushButton.outline:hover {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
    
    /* Input Fields */
    QLineEdit {{
        background-color: white;
        border: 2px solid #E1E8ED;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11px;
        min-height: 20px;
    }}
    
    QLineEdit:focus {{
        border-color: {ACCENT_COLOR};
        outline: none;
    }}
    
    QLineEdit:hover {{
        border-color: {SECONDARY_COLOR};
    }}
    
    QTextEdit {{
        background-color: white;
        border: 2px solid #E1E8ED;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11px;
    }}
    
    QTextEdit:focus {{
        border-color: {ACCENT_COLOR};
    }}
    
    /* Combo Boxes */
    QComboBox {{
        background-color: white;
        border: 2px solid #E1E8ED;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 11px;
        min-height: 20px;
    }}
    
    QComboBox:focus {{
        border-color: {ACCENT_COLOR};
    }}
    
    QComboBox::drop-down {{
        border: none;
        background-color: transparent;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid {TEXT_COLOR};
        margin-right: 6px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: white;
        border: 2px solid {ACCENT_COLOR};
        border-radius: 6px;
        selection-background-color: {ACCENT_COLOR};
        selection-color: white;
    }}
    
    /* Tables */
    QTableWidget {{
        background-color: white;
        border: 1px solid #E1E8ED;
        border-radius: 8px;
        gridline-color: #F1F3F4;
        selection-background-color: {ACCENT_COLOR};
        selection-color: white;
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid #F1F3F4;
    }}
    
    QTableWidget::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    
    QHeaderView::section {{
        background-color: {PRIMARY_COLOR};
        color: white;
        padding: 8px;
        border: none;
        font-weight: 600;
    }}
    
    QHeaderView::section:first {{
        border-top-left-radius: 8px;
    }}
    
    QHeaderView::section:last {{
        border-top-right-radius: 8px;
    }}
    
    /* List Widgets */
    QListWidget {{
        background-color: white;
        border: 1px solid #E1E8ED;
        border-radius: 8px;
        selection-background-color: {ACCENT_COLOR};
        selection-color: white;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-bottom: 1px solid #F1F3F4;
    }}
    
    QListWidget::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    
    /* Group Boxes */
    QGroupBox {{
        font-weight: 600;
        font-size: 12px;
        color: {PRIMARY_COLOR};
        border: 2px solid #E1E8ED;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: {BACKGROUND_COLOR};
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid #E1E8ED;
        border-radius: 8px;
        background-color: white;
    }}
    
    QTabBar::tab {{
        background-color: #F8F9FA;
        color: {TEXT_COLOR};
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-weight: 600;
    }}
    
    QTabBar::tab:selected {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    
    /* Progress Bars */
    QProgressBar {{
        background-color: #F1F3F4;
        border: none;
        border-radius: 8px;
        height: 16px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {SUCCESS_COLOR};
        border-radius: 8px;
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        background-color: #F1F3F4;
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: #BDC3C7;
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: #F1F3F4;
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: #BDC3C7;
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {CARD_COLOR};
        border-top: 1px solid #E1E8ED;
        color: {TEXT_COLOR};
        font-size: 10px;
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {CARD_COLOR};
        color: {TEXT_COLOR};
        border-bottom: 1px solid #E1E8ED;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    
    QMenu {{
        background-color: white;
        border: 1px solid #E1E8ED;
        border-radius: 6px;
    }}
    
    QMenu::item {{
        padding: 8px 16px;
    }}
    
    QMenu::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    
    /* Tool Tips */
    QToolTip {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 10px;
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: #E1E8ED;
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    """

def get_login_style():
    """Get specific styling for login window"""
    return f"""
    QDialog {{
        background-color: {CARD_COLOR};
        border-radius: 12px;
    }}
    
    .login-container {{
        background-color: {CARD_COLOR};
        border-radius: 12px;
        padding: 32px;
    }}
    
    .login-header {{
        font-size: 28px;
        font-weight: bold;
        color: {PRIMARY_COLOR};
        text-align: center;
        margin-bottom: 24px;
    }}
    
    .login-subtitle {{
        font-size: 14px;
        color: {SECONDARY_COLOR};
        text-align: center;
        margin-bottom: 32px;
    }}
    
    .login-button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        min-height: 40px;
    }}
    
    .login-button:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    
    .login-input {{
        background-color: white;
        border: 2px solid #E1E8ED;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        min-height: 20px;
        margin-bottom: 16px;
    }}
    
    .login-input:focus {{
        border-color: {ACCENT_COLOR};
    }}
    
    .error-label {{
        color: {ERROR_COLOR};
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
    }}
    
    .success-label {{
        color: {SUCCESS_COLOR};
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
    }}
    """

def get_dashboard_style():
    """Get specific styling for dashboard"""
    return f"""
    .metric-card {{
        background-color: {CARD_COLOR};
        border: 1px solid #E1E8ED;
        border-radius: 12px;
        padding: 20px;
        margin: 8px;
    }}
    
    .metric-value {{
        font-size: 32px;
        font-weight: bold;
        color: {PRIMARY_COLOR};
        text-align: center;
    }}
    
    .metric-label {{
        font-size: 14px;
        color: {SECONDARY_COLOR};
        text-align: center;
        margin-top: 8px;
    }}
    
    .metric-unit {{
        font-size: 12px;
        color: {TEXT_COLOR};
        text-align: center;
    }}
    
    .status-good {{
        color: {SUCCESS_COLOR};
        font-weight: bold;
    }}
    
    .status-warning {{
        color: {WARNING_COLOR};
        font-weight: bold;
    }}
    
    .status-alarm {{
        color: {ERROR_COLOR};
        font-weight: bold;
    }}
    
    .machine-card {{
        background-color: {CARD_COLOR};
        border: 2px solid #E1E8ED;
        border-radius: 12px;
        padding: 16px;
        margin: 8px;
    }}
    
    .machine-card:hover {{
        border-color: {ACCENT_COLOR};
        cursor: pointer;
    }}
    
    .machine-card.selected {{
        border-color: {PRIMARY_COLOR};
        background-color: #F8F9FF;
    }}
    """