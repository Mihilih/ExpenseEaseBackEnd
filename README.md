## ExpenseEase

![logo](https://github.com/Mihilih/ExpenseEaseBackEnd/assets/72967681/c98f96b6-2058-475d-82ae-cf99c59ecde6)

An expense tracking app that allows user to add, edit, and delete their income and expenses and track which categories of expenses occur the most.

## Description
This app was developed as a personal project after learning Android development during the fall semester and backend development during the winter break of 2023. As I was getting into personal finance I noticed that most expense-tracking apps are too complicated and have too many features. My intention was to develop an app that is simple and has the basic features but is also user-friendly.

Frontend repository: https://github.com/Mihilih/ExpenseEaseFrontEnd.git
Backend deployed URL: http://34.29.154.243/

## Features 
- The backend of this app consists of 4 databases and 20 routes to manage Users, Expenses, Incomes, and Categories.
- The tables have one-to-many(Expenses/Incomes and Users) and many-to-many(Categories and Users) relationships between them and are managed using SQLAlchemy.
- The routes include GET, POST, and DELETE requests and are completed using Python and the Flask framework.
- Using the SendGrid API, an emailing function is integrated for the user to receive an email repost of their expenses.
- User Authentication is done using a session token system. User passwords are hashed using bcrypt.
- The backend was deployed into Google Cloud Computing services using Docker.

  ## App

<img width="222" alt="image" src="https://github.com/Mihilih/ExpenseEaseFrontEnd/assets/72967681/33e7fa94-7179-46ad-a98d-2fee3ac15ae8"> 
<img width="222" alt="image" src="https://github.com/Mihilih/ExpenseEaseFrontEnd/assets/72967681/52a0124f-0a94-4944-a292-7b311ff5f819">
<img width="222" alt="image" src="https://github.com/Mihilih/ExpenseEaseFrontEnd/assets/72967681/c2ec4d2e-989e-44de-9f7e-530a64bb633a">
<img width="222" alt="image" src="https://github.com/Mihilih/ExpenseEaseFrontEnd/assets/72967681/75f40d5b-940d-4194-a571-911a49ed62d6">
<img width="222" alt="image" src="https://github.com/Mihilih/ExpenseEaseFrontEnd/assets/72967681/601d9506-93c7-4a43-b5a4-d6d876d4d314">
<img width="222" alt="image" src="https://github.com/Mihilih/ExpenseEaseFrontEnd/assets/72967681/cc4257a6-ef9c-4dc6-a46a-54b42fac1d06">
<img width="222" alt="image" src="https://github.com/Mihilih/ExpenseEaseFrontEnd/assets/72967681/086f9250-7504-44a6-83ce-480b9738cc4b">
