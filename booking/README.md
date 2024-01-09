# Bookify: A booking app
#### Video Demo: https://www.youtube.com/watch?v=PYIxCrP7pyY
#### Description:

# Boookify README

This web application is designed to manage bookings. It provides a user interface for selecting dates and times, making reservations, and viewing and canceling existing bookings.

## Table of Contents

- [Getting Started](#getting-started)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3
- Flask
- SQLite

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo.git
   ```

2. Change into the project directory:

   ```bash
   cd your-repo
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Features

- **Date and Time Selection:** Users can select dates and times for making reservations.
- **User Registration:** Users can register accounts to manage their bookings.
- **Secure Login:** Secure user authentication with hashed passwords.
- **View and Cancel Bookings:** Admins can view and cancel existing bookings.

## Technologies Used

- **Frontend:**
  - HTML
  - CSS
  - JavaScript

- **Backend:**
  - Python
  - Flask (Web Framework)
  - SQLite (Database)

## Files
- Static/styles:
This file stores the CSS files with all the different styles for the page

- templates/apology:
Renders an "error"-page if wrong userinfo is inputted to the login or an existing username is inputted to the registration form.
- Templates/booking:
Here I handle the HTML and JavaScript logic for dynamically showcasing different options related to the booking
- Templates/current_bookings:
Displays all bookings from the booking form and has an option to cancel/delete bookings
- Templates/index:
Frontpage with a button thats routes to the booking.html and a short description of the webapplication
- Templates/layout:
Layout for the pages
- Templates/login:
Login page for admins
- Templates/register:
Registration page for admins

- app.py
Handles the different routes, the management of SQL statements, genereates hashes for the password for safety, generates the calendar

- bookings.db
database to store the inputs from the booking.html-page.
includes name, phone, date, time and id

- helpers.py
An apology Function which renders apology messages with escaped characters.
A login_required Decorator which enforces user authentication on routes.


## Background and reason for creating this kind of web application
- Aroudn 10 years ago I used to work at a pizza restaurant. This restaurant is still in business and it is one of the most popular places for takeaway.
- This restaurant has never had any booking sysem in order. Neither when it comes to incomning orders nor does it have any booking system for customers who'd like to dine inside.
- I wanted to start working on an application that potentially can handle the logistics of the booking by customers who'd like to order takeaway and to eat at the restaurant.

## Design choice
- I wanted to make an application with a minimalistic and modern style.
- I wanted to make it really simple and intuitive.
- I debated on making the colors of the page more italian-themed for the association of pizza, but
I concluded with a more modern approach so that the application can be more universal, not for just pizza restaurants, but for any kind of business in need of a booking tool.

