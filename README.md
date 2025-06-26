# Automatic Timetable Management System

**Course Project** • Mar 2025 – Apr 2025  
**Developer:** Rahul Chandrakant Patne · 23CS10084  
**Mentor:** Prof. Debasis Samantha, Software Engineering Laboratory

---

## 🔹 Project Summary

A full-stack web application designed to automate academic timetable generation, ensuring conflict-free, balanced schedules for both students and faculty. The system significantly reduces manual effort, prevents scheduling errors, and supports real-time updates through an intuitive interface.

---

## 🔹 Core Features

### Automated Scheduling
- **Smart Algorithm**: Custom greedy algorithm for fair session allocation
- **Conflict Resolution**: Prevents clashes between rooms, instructors, and student groups
- **Availability Management**: Automatic scheduling based on instructor and course availability
- **Balanced Distribution**: Fair class distribution across weekdays

### Dynamic Management
- **Real-time Updates**: Interactive UI for immediate schedule modifications
- **Multi-role Access**: Tailored interfaces for different user types
- **Profile Management**: Comprehensive user and course information handling
---

## 🔹 User Roles & Permissions

### 👨‍🎓 Student/Teacher
- View personal profile information
- Access individual timetables
- Real-time schedule updates

### 👨‍💼 HOD (Head of Department)
- Create and modify courses
- Schedule courses in timetables
- Manage departmental resources

### 🔧 Admin
- Full Django admin access
- Handle all system operations
- User and system management

> **Note:** Visual examples of user interfaces can be found in the `images/` directory.

---

## 🔹 Technologies

| Category | Technology |
|----------|------------|
| **Backend** | Django |
| **Frontend** | Django Templates, HTML, CSS, JavaScript |
| **Interactivity** | HTMX |
| **Database** | SQLite |
| **Testing** | Unit Tests - Github Actions CI |

---

## 🔹 Key Technical Contributions

- **Custom Algorithm**: Designed and implemented a greedy algorithm for optimal timetable generation
- **Dynamic UI**: Built responsive interfaces using HTMX for seamless user experience
- **CI/CD Pipeline**: Established automated testing and continuous integration workflow
- **Conflict Management**: Developed sophisticated conflict resolution system

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 4.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ATMA.git
   cd ATMA
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   cd atma_backend
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run the application**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:8000`

---

## 🧪 Testing

Run the test suite:
```bash
    python manage.py test
```

Automated testing is configured via GitHub Actions for continuous integration.

---

## 📄 License

This project is part of academic coursework at IIT Kharagpur.

---

## 👨‍💻 Author

**Rahul Chandrakant Patne**  
Roll No: 23CS10084  
IIT Kharagpur

---

## 🙏 Acknowledgments

- **Prof. Debasis Samantha** - Project Mentor
- **Software Engineering Laboratory** - IIT Kharagpur
- Django Community for excellent documentation and resources