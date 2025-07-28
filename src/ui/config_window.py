"""
Configuration window for machine and parameter management
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                            QLabel, QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox,
                            QGroupBox, QFormLayout, QMessageBox, QHeaderView,
                            QDialog, QDialogButtonBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Use try/except to handle both relative and absolute imports
try:
    from ..database.operations import db_ops
    from ..utils.auth import auth_manager
    from ..utils.constants import *
    from .styles import get_application_style
except ImportError:
    # Fallback to absolute imports when running directly
    from database.operations import db_ops
    from utils.auth import auth_manager
    from utils.constants import *
    from ui.styles import get_application_style

logger = logging.getLogger(__name__)

class MachineDialog(QDialog):
    """Dialog for adding/editing machines"""
    
    def __init__(self, machine_data=None, parent=None):
        super().__init__(parent)
        self.machine_data = machine_data
        self.is_editing = machine_data is not None
        
        self.setWindowTitle("Edit Machine" if self.is_editing else "Add Machine")
        self.setFixedSize(400, 300)
        
        self.setup_ui()
        
        if self.is_editing:
            self.populate_fields()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Ensure dialog has proper background
        self.setStyleSheet(f"QDialog {{ background-color: {BACKGROUND_COLOR}; }}")
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self.name_input = QLineEdit()
        form_layout.addRow("Name*:", self.name_input)
        
        # Description field
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
        # Location field
        self.location_input = QLineEdit()
        form_layout.addRow("Location:", self.location_input)
        
        # Machine type field
        self.type_input = QComboBox()
        self.type_input.setEditable(True)
        self.type_input.addItems([
            "Centrifugal Pump", "AC Motor", "Screw Compressor",
            "Gear Box", "Fan", "Conveyor", "Hydraulic System",
            "Pneumatic System", "Heat Exchanger", "Boiler"
        ])
        form_layout.addRow("Type:", self.type_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def populate_fields(self):
        """Populate fields with existing machine data"""
        if not self.machine_data:
            return
        
        self.name_input.setText(self.machine_data.get('name', ''))
        self.description_input.setPlainText(self.machine_data.get('description', ''))
        self.location_input.setText(self.machine_data.get('location', ''))
        self.type_input.setCurrentText(self.machine_data.get('machine_type', ''))
    
    def get_machine_data(self):
        """Get machine data from form"""
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'location': self.location_input.text().strip(),
            'machine_type': self.type_input.currentText().strip()
        }
    
    def accept(self):
        """Validate and accept the dialog"""
        data = self.get_machine_data()
        
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", "Machine name is required!")
            return
        
        super().accept()

class ParameterDialog(QDialog):
    """Dialog for adding/editing parameters"""
    
    def __init__(self, parameter_data=None, parent=None):
        super().__init__(parent)
        self.parameter_data = parameter_data
        self.is_editing = parameter_data is not None
        
        self.setWindowTitle("Edit Parameter" if self.is_editing else "Add Parameter")
        self.setFixedSize(450, 400)
        
        self.setup_ui()
        
        if self.is_editing:
            self.populate_fields()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Ensure dialog has proper background
        self.setStyleSheet(f"QDialog {{ background-color: {BACKGROUND_COLOR}; }}")
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self.name_input = QLineEdit()
        form_layout.addRow("Name*:", self.name_input)
        
        # Register address field
        self.register_input = QComboBox()
        self.register_input.setEditable(True)
        self.register_input.addItems(list(REGISTER_MAP.keys()))
        form_layout.addRow("Register Address*:", self.register_input)
        
        # Unit field
        self.unit_input = QComboBox()
        self.unit_input.setEditable(True)
        units = list(set(config['unit'] for config in REGISTER_MAP.values()))
        self.unit_input.addItems(units)
        form_layout.addRow("Unit:", self.unit_input)
        
        # Min value
        self.min_value_input = QDoubleSpinBox()
        self.min_value_input.setRange(-999999, 999999)
        self.min_value_input.setDecimals(2)
        form_layout.addRow("Min Value:", self.min_value_input)
        
        # Max value
        self.max_value_input = QDoubleSpinBox()
        self.max_value_input.setRange(-999999, 999999)
        self.max_value_input.setDecimals(2)
        self.max_value_input.setValue(100)
        form_layout.addRow("Max Value:", self.max_value_input)
        
        # Alarm low
        self.alarm_low_input = QDoubleSpinBox()
        self.alarm_low_input.setRange(-999999, 999999)
        self.alarm_low_input.setDecimals(2)
        form_layout.addRow("Alarm Low:", self.alarm_low_input)
        
        # Alarm high
        self.alarm_high_input = QDoubleSpinBox()
        self.alarm_high_input.setRange(-999999, 999999)
        self.alarm_high_input.setDecimals(2)
        self.alarm_high_input.setValue(90)
        form_layout.addRow("Alarm High:", self.alarm_high_input)
        
        layout.addLayout(form_layout)
        
        # Connect register selection to auto-fill
        self.register_input.currentTextChanged.connect(self.on_register_changed)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def on_register_changed(self, register):
        """Auto-fill fields based on selected register"""
        if register in REGISTER_MAP:
            config = REGISTER_MAP[register]
            self.name_input.setText(config['name'])
            self.unit_input.setCurrentText(config['unit'])
            self.min_value_input.setValue(config['min'])
            self.max_value_input.setValue(config['max'])
            
            # Set reasonable alarm thresholds
            range_val = config['max'] - config['min']
            self.alarm_low_input.setValue(config['min'] + range_val * 0.1)
            self.alarm_high_input.setValue(config['max'] - range_val * 0.1)
    
    def populate_fields(self):
        """Populate fields with existing parameter data"""
        if not self.parameter_data:
            return
        
        self.name_input.setText(self.parameter_data.get('name', ''))
        self.register_input.setCurrentText(self.parameter_data.get('register_address', ''))
        self.unit_input.setCurrentText(self.parameter_data.get('unit', ''))
        self.min_value_input.setValue(self.parameter_data.get('min_value', 0))
        self.max_value_input.setValue(self.parameter_data.get('max_value', 100))
        self.alarm_low_input.setValue(self.parameter_data.get('alarm_low', 0))
        self.alarm_high_input.setValue(self.parameter_data.get('alarm_high', 90))
    
    def get_parameter_data(self):
        """Get parameter data from form"""
        return {
            'name': self.name_input.text().strip(),
            'register_address': self.register_input.currentText().strip(),
            'unit': self.unit_input.currentText().strip(),
            'min_value': self.min_value_input.value(),
            'max_value': self.max_value_input.value(),
            'alarm_low': self.alarm_low_input.value(),
            'alarm_high': self.alarm_high_input.value()
        }
    
    def accept(self):
        """Validate and accept the dialog"""
        data = self.get_parameter_data()
        
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", "Parameter name is required!")
            return
        
        if not data['register_address']:
            QMessageBox.warning(self, "Validation Error", "Register address is required!")
            return
        
        if data['min_value'] >= data['max_value']:
            QMessageBox.warning(self, "Validation Error", "Max value must be greater than min value!")
            return
        
        super().accept()

class ConfigurationWindow(QMainWindow):
    """Configuration window for machines and parameters"""
    
    skip_to_dashboard = pyqtSignal()  # Signal to skip to dashboard
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} - Configuration")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        self.current_machine_id = None
        
        self.setup_ui()
        self.load_machines()
        
        # Apply styling
        self.setStyleSheet(get_application_style())
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")  # Ensure background is set
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Machine management tab
        self.create_machine_tab()
        
        # Parameter management tab
        self.create_parameter_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        self.create_bottom_buttons(layout)
    
    def create_header(self, layout):
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("System Configuration")
        title_label.setObjectName("header")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 16px 0px;
        """)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # User info
        user = auth_manager.get_current_user()
        if user:
            user_label = QLabel(f"Logged in as: {user['full_name']} ({user['role'].title()})")
            user_label.setStyleSheet(f"color: {SECONDARY_COLOR}; font-weight: 600;")
            header_layout.addWidget(user_label)
        
        layout.addLayout(header_layout)
    
    def create_machine_tab(self):
        """Create machine management tab"""
        machine_widget = QWidget()
        layout = QVBoxLayout(machine_widget)
        
        # Machine list header
        header_layout = QHBoxLayout()
        
        machines_label = QLabel("Machines")
        machines_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {PRIMARY_COLOR};")
        header_layout.addWidget(machines_label)
        
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Machine management buttons (only for admins/managers)
        if auth_manager.can_manage_machines():
            self.add_machine_btn = QPushButton("Add Machine")
            self.add_machine_btn.clicked.connect(self.add_machine)
            header_layout.addWidget(self.add_machine_btn)
            
            self.edit_machine_btn = QPushButton("Edit Machine")
            self.edit_machine_btn.clicked.connect(self.edit_machine)
            self.edit_machine_btn.setEnabled(False)
            # header_layout.addWidget(self.edit_machine_btn)
            
            self.delete_machine_btn = QPushButton("Delete Machine")
            self.delete_machine_btn.clicked.connect(self.delete_machine)
            self.delete_machine_btn.setEnabled(False)
            self.delete_machine_btn.setStyleSheet("""
	QPushButton {
		background-color: #E74C3C;
		color: white;
           	border: 1px solid #45a049;
            	padding: 8px 16px;
            	border-radius: 4px;
                    }
        QPushButton:hover {
            background-color: #E74C3C;
        }
                QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """)
            header_layout.addWidget(self.delete_machine_btn)
        
        layout.addLayout(header_layout)
        
        # Machine table
        self.machine_table = QTableWidget()
        self.machine_table.setColumnCount(5)
        self.machine_table.setHorizontalHeaderLabels([
            "Name", "Type", "Location", "Description", "Created By"
        ])
        
        # Configure table
        header = self.machine_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.machine_table.selectionModel().selectionChanged.connect(self.on_machine_selection_changed)
        layout.addWidget(self.machine_table)
        
        self.tab_widget.addTab(machine_widget, "Machines")
    
    def create_parameter_tab(self):
        """Create parameter management tab"""
        parameter_widget = QWidget()
        layout = QVBoxLayout(parameter_widget)
        
        # Machine selection
        machine_layout = QHBoxLayout()
        
        machine_label = QLabel("Select Machine:")
        machine_label.setStyleSheet(f"font-weight: bold; color: {TEXT_COLOR};")
        machine_layout.addWidget(machine_label)
        
        self.machine_combo = QComboBox()
        self.machine_combo.currentIndexChanged.connect(self.on_machine_combo_changed)
        machine_layout.addWidget(self.machine_combo)
        
        machine_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        layout.addLayout(machine_layout)
        
        # Parameter list header
        header_layout = QHBoxLayout()
        
        parameters_label = QLabel("Parameters")
        parameters_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {PRIMARY_COLOR};")
        header_layout.addWidget(parameters_label)
        
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Parameter management buttons (only for admins/managers)
        if auth_manager.can_manage_machines():
            self.add_parameter_btn = QPushButton("Add Parameter")
            self.add_parameter_btn.clicked.connect(self.add_parameter)
            self.add_parameter_btn.setEnabled(False)
            self.add_parameter_btn.setStyleSheet("""
QPushButton {
background-color: #4CAF50;
color: white;
                                                            border: 1px solid #45a049;
            padding: 8px 16px;
            border-radius: 4px;
                    }
        QPushButton:hover {
            background-color: #45a049;
        }
                QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """)
            header_layout.addWidget(self.add_parameter_btn)
            
            self.edit_parameter_btn = QPushButton("Edit Parameter")
            self.edit_parameter_btn.clicked.connect(self.edit_parameter)
            self.edit_parameter_btn.setEnabled(False)
            # header_layout.addWidget(self.edit_parameter_btn)
            
            self.delete_parameter_btn = QPushButton("Delete Parameter")
            self.delete_parameter_btn.clicked.connect(self.delete_parameter)
            self.delete_parameter_btn.setEnabled(False)
            self.delete_parameter_btn.setStyleSheet("""
	QPushButton {
		background-color: #E74C3C;
		color: white;
           	border: 1px solid #45a049;
            	padding: 8px 16px;
            	border-radius: 4px;
                    }
        QPushButton:hover {
            background-color: #E74C3C;
        }
                QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """)
            header_layout.addWidget(self.delete_parameter_btn)
        
        layout.addLayout(header_layout)
        
        # Parameter table
        self.parameter_table = QTableWidget()
        self.parameter_table.setColumnCount(7)
        self.parameter_table.setHorizontalHeaderLabels([
            "Name", "Register", "Unit", "Min Value", "Max Value", "Alarm Low", "Alarm High"
        ])
        
        # Configure table
        header = self.parameter_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.parameter_table.selectionModel().selectionChanged.connect(self.on_parameter_selection_changed)
        layout.addWidget(self.parameter_table)
        
        self.tab_widget.addTab(parameter_widget, "Parameters")
    
    def create_bottom_buttons(self, layout):
        """Create bottom button section"""
        button_layout = QHBoxLayout()
        
        # Skip to dashboard button
        self.skip_button = QPushButton("Skip to Dashboard")
        self.skip_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }}
        """)
        self.skip_button.clicked.connect(self.skip_to_dashboard.emit)
        button_layout.addWidget(self.skip_button)
        
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet(f"background-color: {ERROR_COLOR};")
        self.logout_button.clicked.connect(self.logout)
        button_layout.addWidget(self.logout_button)
        
        layout.addLayout(button_layout)
    
    def load_machines(self):
        """Load machines into table and combo box"""
        try:
            user = auth_manager.get_current_user()
            machines = db_ops.get_machines(user['id'], user['role'])
            
            # Update machine table
            self.machine_table.setRowCount(len(machines))
            
            for row, machine in enumerate(machines):
                self.machine_table.setItem(row, 0, QTableWidgetItem(machine.get('name', '')))
                self.machine_table.setItem(row, 1, QTableWidgetItem(machine.get('machine_type', '')))
                self.machine_table.setItem(row, 2, QTableWidgetItem(machine.get('location', '')))
                self.machine_table.setItem(row, 3, QTableWidgetItem(machine.get('description', '')))
                self.machine_table.setItem(row, 4, QTableWidgetItem(machine.get('created_by_name', '')))
                
                # Store machine ID in first item
                self.machine_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, machine['id'])
            
            # Update machine combo box
            self.machine_combo.clear()
            self.machine_combo.addItem("Select a machine...", None)
            
            for machine in machines:
                self.machine_combo.addItem(machine['name'], machine['id'])
                
        except Exception as e:
            logger.error(f"Error loading machines: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load machines: {str(e)}")
    
    def load_parameters(self, machine_id):
        """Load parameters for selected machine"""
        try:
            parameters = db_ops.get_parameters(machine_id)
            
            self.parameter_table.setRowCount(len(parameters))
            
            for row, param in enumerate(parameters):
                self.parameter_table.setItem(row, 0, QTableWidgetItem(param.get('name', '')))
                self.parameter_table.setItem(row, 1, QTableWidgetItem(param.get('register_address', '')))
                self.parameter_table.setItem(row, 2, QTableWidgetItem(param.get('unit', '')))
                self.parameter_table.setItem(row, 3, QTableWidgetItem(str(param.get('min_value', 0))))
                self.parameter_table.setItem(row, 4, QTableWidgetItem(str(param.get('max_value', 100))))
                self.parameter_table.setItem(row, 5, QTableWidgetItem(str(param.get('alarm_low', 0))))
                self.parameter_table.setItem(row, 6, QTableWidgetItem(str(param.get('alarm_high', 90))))
                
                # Store parameter ID in first item
                self.parameter_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, param['id'])
                
        except Exception as e:
            logger.error(f"Error loading parameters: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load parameters: {str(e)}")
    
    def on_machine_selection_changed(self):
        """Handle machine selection change"""
        selected = self.machine_table.selectionModel().hasSelection()
        
        if auth_manager.can_manage_machines():
            self.edit_machine_btn.setEnabled(selected)
            self.delete_machine_btn.setEnabled(selected)
    
    def on_parameter_selection_changed(self):
        """Handle parameter selection change"""
        selected = self.parameter_table.selectionModel().hasSelection()
        
        if auth_manager.can_manage_machines():
            # self.edit_parameter_btn.setEnabled(selected)
            self.delete_parameter_btn.setEnabled(selected)
    
    def on_machine_combo_changed(self):
        """Handle machine combo box selection change"""
        machine_id = self.machine_combo.currentData()
        self.current_machine_id = machine_id
        
        if machine_id:
            self.load_parameters(machine_id)
            if auth_manager.can_manage_machines():
                self.add_parameter_btn.setEnabled(True)
        else:
            self.parameter_table.setRowCount(0)
            if auth_manager.can_manage_machines():
                self.add_parameter_btn.setEnabled(False)
    
    def add_machine(self):
        """Add new machine"""
        dialog = MachineDialog(parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_machine_data()
            user = auth_manager.get_current_user()
            
            try:
                machine_id = db_ops.create_machine(
                    data['name'], data['description'], data['location'],
                    data['machine_type'], user['id']
                )
                
                if machine_id:
                    QMessageBox.information(self, "Success", "Machine added successfully!")
                    self.load_machines()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add machine!")
                    
            except Exception as e:
                logger.error(f"Error adding machine: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add machine: {str(e)}")
    
    def edit_machine(self):
        """Edit selected machine"""
        current_row = self.machine_table.currentRow()
        if current_row < 0:
            return
        
        machine_id = self.machine_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get current machine data
        machine_data = {
            'id': machine_id,
            'name': self.machine_table.item(current_row, 0).text(),
            'machine_type': self.machine_table.item(current_row, 1).text(),
            'location': self.machine_table.item(current_row, 2).text(),
            'description': self.machine_table.item(current_row, 3).text()
        }
        
        dialog = MachineDialog(machine_data, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_machine_data()
            
            try:
                if db_ops.update_machine(
                    machine_id, data['name'], data['description'],
                    data['location'], data['machine_type']
                ):
                    QMessageBox.information(self, "Success", "Machine updated successfully!")
                    self.load_machines()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update machine!")
                    
            except Exception as e:
                logger.error(f"Error updating machine: {e}")
                QMessageBox.critical(self, "Error", f"Failed to update machine: {str(e)}")
    
    def delete_machine(self):
        """Delete selected machine"""
        current_row = self.machine_table.currentRow()
        if current_row < 0:
            return
        
        machine_name = self.machine_table.item(current_row, 0).text()
        machine_id = self.machine_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete machine '{machine_name}'?\n\n"
            "This will also delete all associated parameters and data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db_ops.delete_machine(machine_id):
                    QMessageBox.information(self, "Success", "Machine deleted successfully!")
                    self.load_machines()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete machine!")
                    
            except Exception as e:
                logger.error(f"Error deleting machine: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete machine: {str(e)}")
    
    def add_parameter(self):
        """Add new parameter"""
        if not self.current_machine_id:
            QMessageBox.warning(self, "Error", "Please select a machine first!")
            return
        
        dialog = ParameterDialog(parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_parameter_data()
            
            try:
                if db_ops.create_parameter(
                    self.current_machine_id, data['name'], data['register_address'],
                    data['unit'], data['min_value'], data['max_value'],
                    data['alarm_low'], data['alarm_high']
                ):
                    QMessageBox.information(self, "Success", "Parameter added successfully!")
                    self.load_parameters(self.current_machine_id)
                else:
                    QMessageBox.warning(self, "Error", "Failed to add parameter!")
                    
            except Exception as e:
                logger.error(f"Error adding parameter: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add parameter: {str(e)}")
    
    def edit_parameter(self):
        """Edit selected parameter"""
        current_row = self.parameter_table.currentRow()
        if current_row < 0:
            return
        
        parameter_id = self.parameter_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get current parameter data
        parameter_data = {
            'id': parameter_id,
            'name': self.parameter_table.item(current_row, 0).text(),
            'register_address': self.parameter_table.item(current_row, 1).text(),
            'unit': self.parameter_table.item(current_row, 2).text(),
            'min_value': float(self.parameter_table.item(current_row, 3).text()),
            'max_value': float(self.parameter_table.item(current_row, 4).text()),
            'alarm_low': float(self.parameter_table.item(current_row, 5).text()),
            'alarm_high': float(self.parameter_table.item(current_row, 6).text())
        }
        
        dialog = ParameterDialog(parameter_data, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_parameter_data()
            
            try:
                if db_ops.update_parameter(
                    parameter_id, data['name'], data['register_address'],
                    data['unit'], data['min_value'], data['max_value'],
                    data['alarm_low'], data['alarm_high']
                ):
                    QMessageBox.information(self, "Success", "Parameter updated successfully!")
                    self.load_parameters(self.current_machine_id)
                else:
                    QMessageBox.warning(self, "Error", "Failed to update parameter!")
                    
            except Exception as e:
                logger.error(f"Error updating parameter: {e}")
                QMessageBox.critical(self, "Error", f"Failed to update parameter: {str(e)}")
    
    def delete_parameter(self):
        """Delete selected parameter"""
        current_row = self.parameter_table.currentRow()
        if current_row < 0:
            return
        
        parameter_name = self.parameter_table.item(current_row, 0).text()
        parameter_id = self.parameter_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete parameter '{parameter_name}'?\n\n"
            "This will also delete all associated sensor data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db_ops.delete_parameter(parameter_id):
                    QMessageBox.information(self, "Success", "Parameter deleted successfully!")
                    self.load_parameters(self.current_machine_id)
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete parameter!")
                    
            except Exception as e:
                logger.error(f"Error deleting parameter: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete parameter: {str(e)}")
    
    def logout(self):
        """Logout and close window"""
        auth_manager.logout()
        self.close()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyleSheet(get_application_style())
    
    # For testing, simulate a logged-in admin user
    auth_manager.current_user = {
        'id': 1,
        'username': 'admin',
        'role': 'admin',
        'full_name': 'Test Admin',
        'email': 'admin@test.com'
    }
    
    window = ConfigurationWindow()
    window.show()
    
    sys.exit(app.exec())