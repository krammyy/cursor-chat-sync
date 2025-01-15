# OpenAI API Key Generator

This tool automates the process of generating OpenAI API keys for multiple students using Selenium web automation.

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Linux/Mac
   .\env\Scripts\activate  # On Windows
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.sample`:
   ```bash
   cp .env.sample .env
   ```
   Then edit `.env` to add your OpenAI credentials:
   ```
   OPENAI_USERNAME=your_email@example.com
   OPENAI_PASSWORD=your_password
   OPENAI_PROJECT_ID=your_project_id
   ```

4. Set up students.csv file with the following format:
   ```csv
   firstname,lastname,email
   John,Doe,john.doe@example.com
   Jane,Smith,jane.smith@example.com
   ```

5. Run the script:
   ```bash
   python main.py
   ```
   The generated API keys will be saved back to students.csv under a new 'api_key' column.
