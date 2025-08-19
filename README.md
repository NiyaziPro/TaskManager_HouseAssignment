# TaskMeister - Worker Assignment System

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive GUI application for managing worker assignments to houses with email notifications and comprehensive tracking capabilities.

![TaskMeister Screenshot](docs/screenshot.png)

## Features

### 🏠 House Management
- Add, edit, and delete houses
- Real-time search functionality
- Smart filtering to prevent double assignments
- Comment system for house-specific notes

### 👷 Worker Management  
- Complete worker database with contact information
- Easy selection and assignment interface
- Edit and delete capabilities
- Worker unselection for flexible workflow

### 📅 Smart Assignment Planning
- Date picker with tomorrow's date as default
- Prevents assignments to already-assigned houses
- Quantity specification for bedding sets
- House-specific commenting system

### 📧 Email Integration
- Automatic email notifications to workers
- Professional email formatting
- SMTP configuration for various email providers
- Assignment confirmation tracking

### 📊 Comprehensive History
- Complete assignment history tracking
- Advanced filtering capabilities
- CSV export functionality
- Status tracking (Sent/Pending)

### 🔍 Search & Filter
- Real-time house search
- History filtering
- Dynamic UI updates
- Case-insensitive search

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Required Packages
```bash
pip install tkcalendar
```

### Optional Dependencies
For enhanced functionality:
```bash
pip install Pillow  # For potential future image support
```

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/taskmeister.git
cd taskmeister
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure email settings:**
   - Open `taskmeister.py`
   - Update the `Config` class with your SMTP settings:
   ```python
   class Config:
       SMTP_SERVER = "smtp.gmail.com"  # Your SMTP server
       SMTP_PORT = 587
       EMAIL_USER = "your_email@gmail.com"  # Your email
       EMAIL_PASS = "your_app_password"     # Your app password
   ```

4. **Run the application:**
```bash
python taskmeister.py
```

## Configuration

### Email Setup

#### Gmail Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Update `Config.EMAIL_USER` and `Config.EMAIL_PASS` in the code

#### Other Email Providers
Update the SMTP settings in the `Config` class:

**Outlook/Hotmail:**
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
```

**Yahoo:**
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
```

### Database Configuration
The application uses SQLite database stored as `task_assignments.db` in the application directory. The database is created automatically on first run.

## Usage

### Getting Started
1. **Add Workers:** Use the "Add" button in the Workers panel to add team members
2. **Add Houses:** Use the "Add House" button to create your house database
3. **Select Assignment Date:** Choose the date using the date picker (defaults to tomorrow)
4. **Make Assignments:** 
   - Select a worker from the list
   - Check houses to assign
   - Set quantities and add comments if needed
   - Click "Send Assignments"

### Daily Workflow
1. Select tomorrow's date (default)
2. Choose the worker for assignments
3. Select houses from the available list (already assigned houses are hidden)
4. Add quantities and comments as needed
5. Send assignments via email
6. Review history as needed

### Advanced Features

#### Search Functionality
- Use the search box above the house list to quickly find specific houses
- Search is case-insensitive and updates in real-time

#### Comment System
- Click the "+" button next to any house to add comments
- Comments are house-specific and included in email notifications
- The button changes to "✎" when a comment is saved

#### History Management
- View complete assignment history
- Filter by worker, house, or notes
- Export data to CSV for external analysis
- Track email sending status

## File Structure

```
taskmeister/
├── taskmeister.py          # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE                # MIT License
└── tests/                 # Unit tests (future)
    └── test_taskmeister.py
```

## Architecture

### Clean Code Principles
- **Single Responsibility:** Each class has a clear, single purpose
- **Dependency Injection:** Services are injected rather than hardcoded
- **Error Handling:** Comprehensive error handling throughout
- **Documentation:** Full docstrings and type hints
- **Modular Design:** Separate classes for different concerns

### Key Components

#### DatabaseManager
Handles all database operations with SQLite, including:
- Table creation and migration
- CRUD operations
- Query execution with proper error handling

#### EmailService  
Manages email functionality:
- SMTP configuration
- Email composition
- Sending with error handling

#### Dialog Classes
Reusable dialog components:
- WorkerDialog for adding/editing workers
- HouseDialog for adding/editing houses
- ListSelectionDialog for generic list selection

#### Main Application (TaskMeisterApp)
The primary GUI application managing:
- UI layout and components
- Event handling
- Business logic coordination
- State management

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Include docstrings for all public methods
- Write descriptive commit messages

## Troubleshooting

### Common Issues

#### "tkcalendar module not found"
```bash
pip install tkcalendar
```

#### "SMTP Authentication Error"
- Verify your email credentials
- For Gmail, ensure you're using an App Password, not your regular password
- Check that 2-Factor Authentication is enabled

#### "Database locked" Error
- Close any other instances of the application
- Check file permissions in the application directory

#### Email Not Sending
1. Verify SMTP settings in the Config class
2. Check internet connectivity
3. Verify email credentials
4. Check if firewall is blocking SMTP ports

### Getting Help
- Check the [Issues](https://github.com/yourusername/taskmeister/issues) page
- Create a new issue with detailed error information
- Include your Python version and operating system

## Roadmap

### Planned Features
- [ ] Multi-language support
- [ ] Advanced reporting and analytics
- [ ] Mobile app companion
- [ ] Calendar integration
- [ ] Batch assignment operations
- [ ] Worker availability tracking
- [ ] Automatic backup functionality
- [ ] REST API for integration

### Version History
- **v1.0.0** - Initial release with core functionality
- **v0.9.0** - Beta release for testing
- **v0.8.0** - Alpha release with basic features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and tkinter
- Uses tkcalendar for date selection
- Inspired by modern task management systems
- Thanks to all contributors and testers

## Contact

- **Project Maintainer:** [Niyazi Cholak](mailto:your.email@example.com)
- **Issues:** [GitHub Issues](https://github.com/yourusername/taskmeister/issues)
- **Documentation:** [Wiki](https://github.com/yourusername/taskmeister/wiki)

---

**Happy Task Managing! 🎯**