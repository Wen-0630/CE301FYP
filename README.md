
# NeuroPlanner Project - Detailed Setup Guide

Welcome to the Net Plus project. This guide will walk you through the detailed steps required to set up and run the project using Visual Studio Code (VS Code). Please follow the steps carefully to ensure a successful setup. If you encounter any issues, feel free to call me at +65 81912109.

## Table of Contents

1. [Background](#background)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
   - [1. Install Visual Studio Code](#1-install-visual-studio-code)
   - [2. Install Required Extensions](#2-install-required-extensions)
   - [3. Clone the Repository](#3-clone-the-repository)
   - [4. Install Python](#4-install-python)
   - [5. Install Project Dependencies](#5-install-project-dependencies)
   - [6. Configure MongoDB Atlas](#6-configure-mongodb-atlas)
   - [7. Run the Project](#7-run-the-project)

## Background

The Net Plus project is a web application designed to manage financial records. The project uses the following technologies:
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB Atlas (cloud database)

## Prerequisites

Before setting up the project, ensure you have the following installed:
- [Visual Studio Code](https://code.visualstudio.com/)
- [Python](https://www.python.org/downloads/) (version 3.8 or higher)
- [Git](https://git-scm.com/downloads)

## Setup Instructions

### 1. Install Visual Studio Code

1. Download and install Visual Studio Code from the [official website](https://code.visualstudio.com/).
2. Launch Visual Studio Code after installation.

### 2. Install Required Extensions

1. Open Visual Studio Code.
2. Go to the Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or by pressing `Ctrl+Shift+X`.
3. Install the following extensions:
   - Python (ms-python.python)
   - MongoDB for VS Code (mongodb.mongodb-vscode)
   - Pylance (ms-python.vscode-pylance)
   - Python Debugger (ms-python.python)

### 3. Clone the Repository

1. Open Visual Studio Code.
2. Open the Command Palette by pressing `Ctrl+Shift+P`.
3. Type `Git: Clone` and select the option.
4. Enter the repository URL and select a local folder to clone the repository into.

### 4. Install Python

1. Download and install Python from the [official website](https://www.python.org/downloads/).
2. Ensure that Python is added to your system PATH during the installation.

### 5. Install Project Dependencies

1. With the virtual environment activated, run the following command to install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 6. Configure MongoDB Atlas

1. Create a MongoDB Atlas account at [mongodb.com](https://www.mongodb.com/cloud/atlas). Verify your email and log in. Complete the "Get to know you" stage by answering the following:
   - **Programming Language**: Python
   - **Data Types**: Time series data
2. Deploy a new cluster:
   - Choose **M0** for the free tier (512MB storage).
   - Name the cluster **Database** (this name is compulsory).
   - Select **AWS** as the provider.
   - Ensure **Automate security setup** and **Preload sample dataset** are ticked.
3. Configure network access:
   - Add your current IP address or another as needed.
4. Create a database user:
   - Set a username and password, then click **Create database user**.
5. Obtain the connection string:
   - Format: `mongodb+srv://<username>:<password>@database.<xxxxxx>.mongodb.net/CE-301?retryWrites=true&w=majority&appName=Database`
   - Replace `<username>`,`<password>`and `<xxxxxx>` with your credentials.

6. Create the database and collection:
   - Open **Browse Collections**.
   - Create a database named `CE-301` (ensure the name is exact, suggest to direct copy and paste).
   - Create a collection named `users`.
   - Populate the database using `populateDB.py` with the connection string updated in `MongoClient`. You will see print("All data inserted successfully!"), meaning data is present correctly in the database.

7. If you encounter issues, email the Net Plus team at "laiyiwen005@gmail.com" to receive an invitation and the connection string.

### 7. Run the Project

1. Create a `.env` file in the project root directory and add the following environment variables:
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@database.<xxxxxx>.mongodb.net/CE-301?retryWrites=true&w=majority&appName=Database
   SECRET_KEY=CE301-CapstoneProject-HHH
   DB_NAME=CE-301
   ```
   Replace `<username>` and `<password>` with your MongoDB Atlas credentials.
2. Open Visual Studio Code.
3. Open a terminal in Visual Studio Code by pressing `Ctrl+` (backtick).
4. Ensure the virtual environment is activated.
5. Run the following command to start the Flask server:
   ```bash
   flask run
   ```
6. Run the main.py file and click on the provided link http://127.0.0.1:5000/ in the terminal to access the application.

If you encounter any issues during the setup, please call me at +65 81912109 for assistance.

## Project Structure

Here's a brief overview of the project structure:

```
CE301-CapstoneProject-MVP/
├── src/
│   ├── _init_.py/
│   ├── auth.py/
│   ├── cashFlow.py/
│   ├── creditCard.py/
│   ├── investment.py/
│   ├── loan.py/
│   ├── models.py/
│   ├── transactions.py/
│   ├── utils.py/
│   ├── views.py/
├── static/
│   ├── build/
│   ├── css/
│   ├── img/
│   ├── js/
│   ├── vendors/
├── templates/
│   ├── auth.base.html
│   ├── base.html
│   ├── cashflow.html
│   ├── creditCard.html
│   ├── dashboard.html
│   ├── edit_loan.html
│   ├── edit_transaction.html
│   ├── holdings.html
│   ├── index.html
│   ├── loan.html
│   ├── login.html
│   ├── markets.html
│   ├── signup.html
│   ├── transactions.html
├── .env
├── main.py
├── populateDB.py
├── requirements.txt
├── README.md
```

Collections of database included:
- users
- cash_flow
- crypto_holdings
- loans
- repayments
- transactions
- stock_holdings
- markets

## Final Notes

Make sure to regularly update your dependencies and keep your environment secure. For any changes or improvements, feel free to contribute to the repository.

Thank you for setting up the Net Plus project. Enjoy using it!
