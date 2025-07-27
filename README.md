# wurdo
<img width="815" height="231" alt="image" src="https://github.com/user-attachments/assets/48e5cf77-5bda-41cd-9fd7-7640dba34efe" />
A relaxing and engaging word puzzle game inspired by Balatro and Wordle, where players chain words together by finding homophones, rhymes, or adding a single letter.

## Table of Contents

- [Project Goal](#project-goal)
- [Technologies Used](#technologies-used)
- [Installation and Setup](#installation-and-setup)
- [Game Logic](#game-logic)
- [Project Status](#project-status)

## Project Goal
The primary objective of this project was to build a fun, low-stress word game for anyone to enjoy. We wanted to build a kind of game that we would enjoy that we could share with others. It was inspired by the NYTimes Wordle. The unique combination of linguistic puzzles aims to provide a fresh and replayable experience. The game's core loop is designed to be intuitive and accessible, with a strategic layer introduced through the "energy" mechanic.

## Technologies Used
- **Frontend:**
  - `React`: A JavaScript library for building the user interface.
  - `Tailwind CSS`: A utility-first CSS framework for rapid and responsive styling.

- **Backend & Data:**
  - `Python`: The backend language.
  - `Redis`: Used as a high-performance in-memory data store.

## Installation and Setup

To get a local copy of this project up and running for development, follow these steps.

### Prerequisites

* `Python 3.x`: ...
* `Node.js` & `npm`: ...
* `Redis Server`: ...

### Backend Setup

1.  Clone the repository:
    ```bash
    git clone ...
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run preprocessing scripts:
    ```bash
    python preprocess_words.py
    ```

## Usage

To run the full application:

1.  Ensure your Redis server is running.
2.  In the `backend` directory, start the API server:
    ```bash
    python app.py
    ```
3.  In a separate terminal in the project's root, start the React app:
    ```bash
    npm start
    ```
## Project Status
We will add this part later.
