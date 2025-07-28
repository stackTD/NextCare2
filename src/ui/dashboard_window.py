"""
Dashboard window with real-time monitoring
"""

import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QComboBox, QTableWidget, 
                            QTableWidgetItem, QFrame, QGridLayout, QSplitter,
                            QDialog, QSpacerItem, QSizePolicy, QHeaderView,
                            QMessageBox, QTextEdit, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# Use try/except to handle both relative and absolute imports
try:
    from ..database.operations import db_ops
    from ..communication.sensor_client import sensor_client
    from ..utils.auth import auth_manager
    from ..utils.constants import *
    from .styles import get_application_style, get_dashboard_style
except ImportError:
    # Fallback to absolute imports when running directly
    from database.operations import db_ops
    from communication.sensor_client import sensor_client
    from utils.auth import auth_manager
    from utils.constants import *
    from ui.styles import get_application_style, get_dashboard_style

logger = logging.getLogger(__name__)

class MetricCard(QFrame):
    """Card widget for displaying sensor metrics"""
    
    def __init__(self, parameter_name, unit, parent=None):
        super().__init__(parent)
        self.parameter_name = parameter_name
        self.unit = unit
        self.current_value = 0.0
        self.alarm_low = 0.0
        self.alarm_high = 100.0
        # self.setStyleSheet(f"QMainWindow {{ background-color: {BACKGROUND_COLOR}; }}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the metric card UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border: 1px solid #E1E8ED;
                border-radius: 12px;
                padding: 16px;
                margin: 4px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Parameter name
        self.name_label = QLabel(self.parameter_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {SECONDARY_COLOR};
        """)
        layout.addWidget(self.name_label)
        
        # Value
        self.value_label = QLabel("--")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
        """)
        layout.addWidget(self.value_label)
        
        # Unit
        self.unit_label = QLabel(self.unit)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setStyleSheet(f"""
            font-size: 12px;
            color: {TEXT_COLOR};
        """)
        layout.addWidget(self.unit_label)
        
        # Status indicator
        self.status_label = QLabel("No Data")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {TEXT_COLOR};
            padding: 4px 8px;
            border-radius: 4px;
            background-color: #F1F3F4;
        """)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def update_value(self, value, timestamp=None, quality=True):
        """Update the metric value and status"""
        self.current_value = value
        self.value_label.setText(f"{value:.1f}")
        
        # Determine status based on alarm thresholds
        if not quality:
            self.set_status("COMM ERROR", ERROR_COLOR)
        elif value <= self.alarm_low:
            self.set_status("LOW ALARM", WARNING_COLOR)
        elif value >= self.alarm_high:
            self.set_status("HIGH ALARM", ERROR_COLOR)
        else:
            self.set_status("NORMAL", SUCCESS_COLOR)
    
    def set_status(self, status_text, color):
        """Set the status indicator"""
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            background-color: {color};
        """)
    
    def set_alarm_thresholds(self, low, high):
        """Set alarm thresholds"""
        self.alarm_low = low
        self.alarm_high = high

class ParameterDetailDialog(QDialog):
    """Dialog showing detailed parameter information and trend"""
    
    def __init__(self, parameter_data, parent=None):
        super().__init__(parent)
        self.parameter_data = parameter_data
        self.setWindowTitle(f"Parameter Detail - {parameter_data['parameter_name']}")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_historical_data()
        
    def setup_ui(self):
        """Setup the detail dialog UI"""
        # Ensure dialog has proper background
        self.setStyleSheet(f"QDialog {{ background-color: {BACKGROUND_COLOR}; }}")
        
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"{self.parameter_data['parameter_name']} Detail")
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Parameter info
        info_group = QGroupBox("Parameter Information")
        info_layout = QGridLayout(info_group)
        
        info_layout.addWidget(QLabel("Current Value:"), 0, 0)
        current_value = self.parameter_data.get('value', 0) or 0
        value_label = QLabel(f"{current_value:.2f} {self.parameter_data.get('unit', '')}")
        value_label.setStyleSheet(f"font-weight: bold; color: {PRIMARY_COLOR};")
        info_layout.addWidget(value_label, 0, 1)
        
        info_layout.addWidget(QLabel("Unit:"), 1, 0)
        info_layout.addWidget(QLabel(str(self.parameter_data.get('unit', 'N/A'))), 1, 1)
        
        info_layout.addWidget(QLabel("Range:"), 2, 0)
        range_text = f"{self.parameter_data.get('alarm_low', 0):.1f} - {self.parameter_data.get('alarm_high', 100):.1f}"
        info_layout.addWidget(QLabel(range_text), 2, 1)
        
        info_layout.addWidget(QLabel("Last Update:"), 3, 0)
        timestamp = self.parameter_data.get('timestamp')
        if timestamp:
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "No data"
        info_layout.addWidget(QLabel(time_str), 3, 1)
        
        layout.addWidget(info_group)
        
        # Trend chart
        chart_group = QGroupBox("24-Hour Trend")
        chart_layout = QVBoxLayout(chart_group)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        layout.addWidget(chart_group)
        
        self.setLayout(layout)
    
    def load_historical_data(self):
        """Load and plot historical data"""
        try:
            parameter_id = self.parameter_data['parameter_id']
            history = db_ops.get_parameter_history(parameter_id, hours=24)
            
            if not history:
                # No historical data available
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, 'No historical data available', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14, color='gray')
                ax.set_title(f"{self.parameter_data['parameter_name']} - 24 Hour Trend")
                self.canvas.draw()
                return
            
            # Extract timestamps and values
            timestamps = [row['timestamp'] for row in history]
            values = [row['value'] for row in history]
            
            # Plot the data
            ax = self.figure.add_subplot(111)
            ax.clear()
            
            # Plot values
            ax.plot(timestamps, values, linewidth=2, color=PRIMARY_COLOR, label='Value')
            
            # Add alarm thresholds
            alarm_low = self.parameter_data.get('alarm_low')
            alarm_high = self.parameter_data.get('alarm_high')
            
            if alarm_low is not None:
                ax.axhline(y=alarm_low, color=WARNING_COLOR, linestyle='--', 
                          linewidth=1, alpha=0.7, label='Low Alarm')
            
            if alarm_high is not None:
                ax.axhline(y=alarm_high, color=ERROR_COLOR, linestyle='--', 
                          linewidth=1, alpha=0.7, label='High Alarm')
            
            # Formatting
            ax.set_title(f"{self.parameter_data['parameter_name']} - 24 Hour Trend")
            ax.set_xlabel('Time')
            ax.set_ylabel(f"Value ({self.parameter_data.get('unit', '')})")
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Format x-axis
            import matplotlib.dates as mdates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")

class DashboardWindow(QMainWindow):
    """Main dashboard window with real-time monitoring"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} - Dashboard")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        self.current_machine_id = None
        self.metric_cards = {}
        self.sensor_data = {}
        
        self.setup_ui()
        self.setup_sensor_communication()
        self.load_machines()
        
        # Apply styling
        self.setStyleSheet(get_application_style() + get_dashboard_style())
        
        # Start data refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")  # Ensure background is set
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 5, 20, 20)  # Reduced top margin from 10 to 5
        layout.setSpacing(8)  # Reduced spacing from 10 to 8
        
        # Header
        self.create_header(layout)
        
        # Machine selection
        self.create_machine_selection(layout)
        
        # Main content area
        self.create_main_content(layout)
        
        # Bottom buttons
        self.create_bottom_buttons(layout)
    
    def create_header(self, layout):
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Real-time Dashboard")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 8px 0px;
        """)
        header_layout.addWidget(title_label)
        
        # Connection status
        self.connection_status = QLabel("● Disconnected")
        self.connection_status.setStyleSheet(f"color: {ERROR_COLOR}; font-weight: 600;")
        header_layout.addWidget(self.connection_status)
        
        # Spacer
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # User info
        user = auth_manager.get_current_user()
        if user:
            user_label = QLabel(f"Logged in as: {user['full_name']} ({user['role'].title()})")
            user_label.setStyleSheet(f"color: {SECONDARY_COLOR}; font-weight: 600;")
            header_layout.addWidget(user_label)
        
        layout.addLayout(header_layout)
    
    def create_machine_selection(self, layout):
        """Create machine selection section"""
        selection_layout = QHBoxLayout()
        
        # Machine selection
        machine_label = QLabel("Select Machine:")
        machine_label.setStyleSheet(f"font-weight: bold; color: {TEXT_COLOR};")
        selection_layout.addWidget(machine_label)
        
        self.machine_combo = QComboBox()
        self.machine_combo.setMinimumWidth(200)
        self.machine_combo.currentIndexChanged.connect(self.on_machine_changed)
        selection_layout.addWidget(self.machine_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.clicked.connect(self.refresh_data)
        selection_layout.addWidget(self.refresh_btn)
        
        selection_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        layout.addLayout(selection_layout)
    
    def create_main_content(self, layout):
        """Create main content area"""
        # Splitter for metrics and detail view
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section - Metrics cards
        metrics_widget = QWidget()
        metrics_layout = QVBoxLayout(metrics_widget)
        
        # Metrics header
        metrics_header = QLabel("Live Parameters")
        metrics_header.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 8px 0px;
        """)
        metrics_layout.addWidget(metrics_header)
        
        # Scroll area for metrics
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.metrics_container = QWidget()
        self.metrics_layout = QGridLayout(self.metrics_container)
        scroll_area.setWidget(self.metrics_container)
        
        metrics_layout.addWidget(scroll_area)
        
        # Bottom section - Parameter details table
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Details header
        details_header = QLabel("Parameter Details")
        details_header.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 8px 0px;
        """)
        details_layout.addWidget(details_header)
        
        # Parameters table
        self.parameters_table = QTableWidget()
        self.parameters_table.setColumnCount(6)
        self.parameters_table.setHorizontalHeaderLabels([
            "Parameter", "Current Value", "Unit", "Status", "Last Update", "Action"
        ])
        
        # Configure table
        header = self.parameters_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        details_layout.addWidget(self.parameters_table)
        
        # Add to splitter
        splitter.addWidget(metrics_widget)
        splitter.addWidget(details_widget)
        splitter.setSizes([300, 400])  # Set initial sizes for vertical layout
        
        layout.addWidget(splitter)
    
    def create_bottom_buttons(self, layout):
        """Create bottom button section"""
        button_layout = QHBoxLayout()
        
        # Configuration button (only for admins/managers)
        if auth_manager.has_manager_access():
            self.config_button = QPushButton("Configuration")
            self.config_button.clicked.connect(self.open_configuration)
            button_layout.addWidget(self.config_button)
        
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Logout button
        self.logout_button = QPushButton("Exit")
        self.logout_button.setStyleSheet(f"background-color: {ERROR_COLOR};")
        self.logout_button.clicked.connect(self.logout)
        button_layout.addWidget(self.logout_button)
        
        layout.addLayout(button_layout)
    
    def setup_sensor_communication(self):
        """Setup sensor communication"""
        # Connect signals
        sensor_client.data_received.connect(self.on_sensor_data_received)
        sensor_client.connection_status_changed.connect(self.on_connection_status_changed)
        sensor_client.error_occurred.connect(self.on_sensor_error)
        
        # Try to connect
        if sensor_client.connect_to_sensor():
            sensor_client.start_polling()
    
    @pyqtSlot(dict)
    def on_sensor_data_received(self, data):
        """Handle received sensor data"""
        self.sensor_data.update(data)
        self.update_parameter_displays()
    
    @pyqtSlot(bool)
    def on_connection_status_changed(self, connected):
        """Handle connection status change"""
        if connected:
            self.connection_status.setText("● Connected")
            self.connection_status.setStyleSheet(f"color: {SUCCESS_COLOR}; font-weight: 600;")
        else:
            self.connection_status.setText("● Disconnected")
            self.connection_status.setStyleSheet(f"color: {ERROR_COLOR}; font-weight: 600;")
    
    @pyqtSlot(str)
    def on_sensor_error(self, error_message):
        """Handle sensor communication error"""
        logger.warning(f"Sensor error: {error_message}")
    
    def load_machines(self):
        """Load machines based on user access"""
        try:
            user = auth_manager.get_current_user()
            machines = db_ops.get_machines(user['id'], user['role'])
            
            self.machine_combo.clear()
            self.machine_combo.addItem("Select a machine...", None)
            
            for machine in machines:
                self.machine_combo.addItem(machine['name'], machine['id'])
                
        except Exception as e:
            logger.error(f"Error loading machines: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load machines: {str(e)}")
    
    def on_machine_changed(self):
        """Handle machine selection change"""
        machine_id = self.machine_combo.currentData()
        self.current_machine_id = machine_id
        
        if machine_id:
            self.load_machine_parameters(machine_id)
        else:
            self.clear_displays()
    
    def load_machine_parameters(self, machine_id):
        """Load parameters for selected machine"""
        try:
            parameters = db_ops.get_parameters(machine_id)
            
            # Clear existing displays
            self.clear_displays()
            
            # Create metric cards
            row, col = 0, 0
            max_cols = 4
            
            for param in parameters:
                # Create metric card
                card = MetricCard(param['name'], param.get('unit', ''))
                card.set_alarm_thresholds(
                    param.get('alarm_low', 0),
                    param.get('alarm_high', 100)
                )
                
                self.metrics_layout.addWidget(card, row, col)
                self.metric_cards[param['register_address']] = card
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Update parameters table
            self.update_parameters_table(parameters)
            
            # Load latest sensor data
            self.load_latest_data(machine_id)
            
        except Exception as e:
            logger.error(f"Error loading machine parameters: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load machine parameters: {str(e)}")
    
    def update_parameters_table(self, parameters):
        """Update the parameters table"""
        self.parameters_table.setRowCount(len(parameters))
        
        for row, param in enumerate(parameters):
            # Parameter name
            self.parameters_table.setItem(row, 0, QTableWidgetItem(param['name']))
            
            # Current value (will be updated with real data)
            self.parameters_table.setItem(row, 1, QTableWidgetItem("--"))
            
            # Unit
            self.parameters_table.setItem(row, 2, QTableWidgetItem(param.get('unit', '')))
            
            # Status (will be updated with real data)
            self.parameters_table.setItem(row, 3, QTableWidgetItem("No Data"))
            
            # Last update (will be updated with real data)
            self.parameters_table.setItem(row, 4, QTableWidgetItem("--"))
            
            # Detail button
            detail_btn = QPushButton("Detail")
            detail_btn.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: white; padding: 4px 8px; border-radius: 4px;")
            detail_btn.clicked.connect(lambda checked, p=param: self.show_parameter_detail(p))
            self.parameters_table.setCellWidget(row, 5, detail_btn)
            
            # Store parameter data
            self.parameters_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, param)
    
    def load_latest_data(self, machine_id):
        """Load latest sensor data for machine"""
        try:
            latest_data = db_ops.get_latest_sensor_data(machine_id)
            
            for data_row in latest_data:
                register = None
                # Find register for this parameter (from parameters)
                parameters = db_ops.get_parameters(machine_id)
                for param in parameters:
                    if param['id'] == data_row['parameter_id']:
                        register = param['register_address']
                        break
                
                if register and data_row['value'] is not None:
                    # Update metric card if exists
                    if register in self.metric_cards:
                        self.metric_cards[register].update_value(
                            data_row['value'],
                            data_row['timestamp'],
                            data_row.get('quality', True)
                        )
                    
                    # Update table row
                    self.update_table_row_for_parameter(data_row['parameter_id'], data_row)
                    
        except Exception as e:
            logger.error(f"Error loading latest data: {e}")
    
    def update_parameter_displays(self):
        """Update parameter displays with current sensor data"""
        if not self.current_machine_id:
            return
        
        # Update metric cards with live sensor data
        for register, value in self.sensor_data.items():
            if register in self.metric_cards:
                self.metric_cards[register].update_value(value, datetime.now(), True)
        
        # Store sensor data to database
        self.store_sensor_data()
    
    def store_sensor_data(self):
        """Store current sensor data to database"""
        if not self.current_machine_id or not self.sensor_data:
            return
        
        try:
            # Get parameters for current machine
            parameters = db_ops.get_parameters(self.current_machine_id)
            
            for param in parameters:
                register = param['register_address']
                if register in self.sensor_data:
                    value = self.sensor_data[register]
                    db_ops.insert_sensor_data(param['id'], value, True)
                    
                    # Update table row
                    self.update_table_row_for_parameter(param['id'], {
                        'value': value,
                        'timestamp': datetime.now(),
                        'quality': True
                    })
                    
        except Exception as e:
            logger.error(f"Error storing sensor data: {e}")
    
    def update_table_row_for_parameter(self, parameter_id, data):
        """Update table row for specific parameter"""
        for row in range(self.parameters_table.rowCount()):
            item = self.parameters_table.item(row, 0)
            if item:
                param_data = item.data(Qt.ItemDataRole.UserRole)
                if param_data and param_data['id'] == parameter_id:
                    # Update value
                    value = data.get('value', 0)
                    unit = param_data.get('unit', '')
                    self.parameters_table.setItem(row, 1, QTableWidgetItem(f"{value:.2f}"))
                    
                    # Update status
                    quality = data.get('quality', True)
                    alarm_low = param_data.get('alarm_low', 0)
                    alarm_high = param_data.get('alarm_high', 100)
                    
                    if not quality:
                        status = "COMM ERROR"
                        status_color = ERROR_COLOR
                    elif value <= alarm_low:
                        status = "LOW ALARM"
                        status_color = WARNING_COLOR
                    elif value >= alarm_high:
                        status = "HIGH ALARM"
                        status_color = ERROR_COLOR
                    else:
                        status = "NORMAL"
                        status_color = SUCCESS_COLOR
                    
                    status_item = QTableWidgetItem(status)
                    status_item.setBackground(QColor(status_color))
                    status_item.setForeground(QColor("white"))
                    self.parameters_table.setItem(row, 3, status_item)
                    
                    # Update timestamp
                    timestamp = data.get('timestamp')
                    if timestamp:
                        time_str = timestamp.strftime("%H:%M:%S")
                        self.parameters_table.setItem(row, 4, QTableWidgetItem(time_str))
                    
                    break
    
    def clear_displays(self):
        """Clear all parameter displays"""
        # Clear metric cards
        for card in self.metric_cards.values():
            card.setParent(None)
        self.metric_cards.clear()
        
        # Clear table
        self.parameters_table.setRowCount(0)
    
    def refresh_data(self):
        """Refresh all data displays"""
        if self.current_machine_id:
            self.load_latest_data(self.current_machine_id)
    
    def show_parameter_detail(self, parameter_data):
        """Show detailed parameter information"""
        # Get latest data for this parameter
        try:
            latest_data = db_ops.get_latest_sensor_data(self.current_machine_id)
            
            # Find data for this parameter
            param_data = None
            for data_row in latest_data:
                if data_row['parameter_id'] == parameter_data['id']:
                    param_data = data_row
                    break
            
            if param_data:
                # Merge parameter info with latest data
                combined_data = {**parameter_data, **param_data}
            else:
                combined_data = parameter_data
            
            dialog = ParameterDetailDialog(combined_data, self)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing parameter detail: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load parameter detail: {str(e)}")
    
    def open_configuration(self):
        """Open configuration window"""
        from .config_window import ConfigurationWindow
        
        config_window = ConfigurationWindow()
        config_window.skip_to_dashboard.connect(config_window.close)
        config_window.show()
    
    def logout(self):
        """Logout and close window"""
        # Stop sensor communication
        sensor_client.stop_polling()
        sensor_client.disconnect_from_sensor()
        
        auth_manager.logout()
        self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop timers and sensor communication
        self.refresh_timer.stop()
        sensor_client.stop_polling()
        sensor_client.disconnect_from_sensor()
        
        event.accept()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyleSheet(get_application_style())
    
    # For testing, simulate a logged-in user
    auth_manager.current_user = {
        'id': 1,
        'username': 'admin',
        'role': 'admin',
        'full_name': 'Test Admin',
        'email': 'admin@test.com'
    }
    
    window = DashboardWindow()
    window.show()
    
    sys.exit(app.exec())