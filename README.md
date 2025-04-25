# 🗺️ NYC Transit Info Web App

A web application providing real-time updates, schedules, and transit information for New York City’s public transportation system.

## 🔧 Key Features

- **Interactive Map**  
  Real-time display of subway and bus routes using Google Maps API and React.

- **Favorites & Alerts**  
  Users can save favorite routes/stations and receive alerts for delays or service changes.

- **Accessibility Info**  
  Station-specific details on elevator and escalator availability.

- **Service Status Dashboard**  
  Overview of current service status across all MTA transit lines.

- **Multilingual Support**  
  Interface available in multiple languages for diverse user access.

- **User Accounts**  
  Account creation and login system with Firebase Authentication and SQLite for user preferences.

## 🛠️ Tech Stack

- **Frontend**: React, Google Maps API  
- **Backend**: Flask  
- **Authentication**: Firebase  
- **Database**: SQLite

## How to Run
### make sure you have the right env
open terminal at the front-end pkg  
npm install  
npm install @vis.gl/react-google-maps  
### Run the backend (make sure all pkgs installed)
python app.py  
### Run the front-end (in front-end pkg)
npm start  
