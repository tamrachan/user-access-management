# User Access Management System

A desktop GUI application for managing user access across projects using MySQL and Tkinter.  

This is my OCR A Level Computer Science project which scored an A*. My client, [Cartesian](https://www.cartesian.com), requested that I convert their manual access management system into an automated Python GUI. Using CSV formatted data exported from the company's Linux servers, I created a Graphical User Interface, using Tkinter, which could filter, display and update the CSV file data as required - data from the CSV file could be appended, removed. The system even includes a login system which uses email verification. As the data provided is confidential, I have included substitute anomalysed data instead. This project is specific to the data provided by Cartesian.

## Features

- Admin/Manager login system
- Upload, compare, and edit CSV user access
- Assign and manage project approvers
- Reset user passwords
- MySQL integration

## Setup

1. Clone the repo
2. Create a `.env` file with your DB credentials:

```env
DB_PASSWORD=your_mysql_password
DB_USER=root
DB_HOST=localhost
DB_NAME=CartesianAccessDB

EMAIL_PASSWORD=your_email_password
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
python main.py
```

## Requirements

- Python 3.8+
- MySQL server
- CustomTkinter
