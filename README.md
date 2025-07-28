# NextCare2 - Predictive Maintenance System

A professional PyQt6-based predictive maintenance application with real-time sensor monitoring, role-based access control, and comprehensive machine management capabilities.

## Features

### 🔐 Authentication & Access Control
- Role-based authentication (Admin, Manager, Engineer)
- Secure password hashing with bcrypt
- Role-specific UI adaptation and permissions

### 🏭 Machine Management
- Add, edit, and delete machines
- Machine type categorization
- Location tracking and descriptions
- Role-based machine access control

### 📊 Parameter Configuration
- Configure sensor parameters for each machine
- Register address mapping (D20, D21, etc.)
- Alarm threshold configuration
- Unit and range specifications

### 📈 Real-time Dashboard
- Live sensor data monitoring
- Professional metric cards with status indicators
- Parameter detail views with 24-hour trend charts
- Alarm status visualization
- Connection status monitoring

### 🔌 Sensor Communication
- TCP-based sensor communication
- Mock PLC simulator for testing
- Real-time data polling and storage
- Connection health monitoring

### 🎨 Professional UI
- Modern industrial-themed design
- Responsive layout with proper spacing
- Professional color scheme and typography
- Card-based interface elements

## Architecture

```
NextCare2/
├── src/
│   ├── main.py                 # Application entry point
│   ├── ui/                     # User interface components
│   │   ├── login_window.py     # Login screen
│   │   ├── config_window.py    # Configuration screens
│   │   ├── dashboard_window.py # Dashboard with real-time monitoring
│   │   └── styles.py           # Professional UI styling
│   ├── database/               # Database layer
│   │   ├── models.py           # Database schema
│   │   ├── connection.py       # Database connection management
│   │   └── operations.py       # Database operations
│   ├── communication/          # Sensor communication
│   │   └── sensor_client.py    # TCP sensor client
│   ├── mock_sensor/            # Testing utilities
│   │   └── mock_plc.py         # Mock PLC simulator
│   └── utils/                  # Utilities
│       ├── auth.py             # Authentication management
│       └── constants.py        # Application constants
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **PostgreSQL 12 or higher**
3. **Git**

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/stackTD/NextCare2.git
   cd NextCare2
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database:**
   ```sql
   -- Create database user
   CREATE USER nextcare_user WITH PASSWORD 'nextcare_password';
   
   -- Create database
   CREATE DATABASE nextcare2 OWNER nextcare_user;
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE nextcare2 TO nextcare_user;
   ```

5. **Configure environment variables (optional):**
   Create a `.env` file in the root directory:
   ```bash
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=nextcare2
   DB_USER=nextcare_user
   DB_PASSWORD=nextcare_password
   ```

## Usage

### Running the Application

1. **Start the main application:**
   ```bash
   python src/main.py
   ```

2. **Login with default credentials:**
   
   **Administrator:**
   - Username: `admin`
   - Password: `password`
   
   **Manager:**
   - Username: `manager1`
   - Password: `password`
   
   **Engineer:**
   - Username: `engineer1`
   - Password: `password`

### Running the Mock PLC Simulator

For testing with simulated sensor data:

```bash
python src/mock_sensor/mock_plc.py
```

The mock PLC will start on `localhost:8888` and provide realistic sensor data simulation.

## User Roles & Permissions

### Administrator
- Full system access
- User management (create/edit/delete users)
- Machine management (create/edit/delete machines)
- Parameter configuration
- Dashboard access
- Access to all machines

### Manager
- Machine management (create/edit/delete machines)
- Parameter configuration
- Dashboard access
- Access to all machines
- Cannot manage users

### Engineer
- Dashboard access only
- Access to assigned machines only
- View-only access to configurations

## Database Schema

### Core Tables

- **users** - User accounts and roles
- **machines** - Machine definitions and metadata
- **parameters** - Sensor parameters per machine
- **sensor_data** - Time-series sensor readings
- **user_machine_access** - Engineer machine access control
- **alarms** - Alarm history and acknowledgments

### Key Relationships

- Users can have access to multiple machines
- Machines can have multiple parameters
- Parameters generate sensor data over time
- Alarms are triggered based on parameter thresholds

## Configuration

### Sensor Register Mapping

The application supports standard PLC register addresses:

- **D20** - Temperature (°C)
- **D21** - Pressure (bar)
- **D22** - Vibration (mm/s)
- **D23** - Speed (RPM)
- **D24** - Current (A)
- **D25** - Voltage (V)

### Alarm Thresholds

Each parameter can have:
- Low alarm threshold
- High alarm threshold
- Min/max operational ranges
- Custom units and descriptions

## Development

### Adding New Parameter Types

1. Update `REGISTER_MAP` in `utils/constants.py`
2. Add simulation logic in `mock_sensor/mock_plc.py`
3. Update UI components if needed

### Customizing UI Themes

Modify color constants in `utils/constants.py`:
- `PRIMARY_COLOR` - Main brand color
- `SECONDARY_COLOR` - Secondary brand color
- `ACCENT_COLOR` - Accent highlights
- `SUCCESS_COLOR` - Success indicators
- `WARNING_COLOR` - Warning indicators
- `ERROR_COLOR` - Error indicators

### Database Migrations

The application automatically creates tables and initial data on first run. For schema changes:

1. Update models in `database/models.py`
2. Add migration logic to `database/connection.py`
3. Test with a fresh database

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database exists and user has permissions

2. **Sensor Communication Error**
   - Start mock PLC simulator: `python src/mock_sensor/mock_plc.py`
   - Check firewall settings for port 8888
   - Verify network connectivity

3. **Application Won't Start**
   - Check Python version (3.8+ required)
   - Verify all dependencies installed: `pip install -r requirements.txt`
   - Check log file: `nextcare2.log`

4. **Login Issues**
   - Use default credentials (see Usage section)
   - Check database connection
   - Verify user table was created properly

### Logging

Application logs are written to:
- `nextcare2.log` - Main application log
- Console output - Real-time logging

Log levels can be adjusted in `src/main.py`.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m "Description"`
5. Push to branch: `git push origin feature-name`
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review application logs for error details

## Version History

### v1.0.0 (Current)
- Initial release
- Complete CRUD operations for machines and parameters
- Real-time dashboard with sensor monitoring
- Role-based authentication and access control
- Professional UI with industrial theme
- Mock PLC simulator for testing
- PostgreSQL database integration
- TCP sensor communication

---

Built with ❤️ using PyQt6, PostgreSQL, and modern Python practices.