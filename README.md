# ClinicConnect API

This is a FastAPI-based backend for the ClinicConnect application. It provides authentication functionality, including user registration and login using JWT tokens.

## Setup Instructions

1. Clone the Repository:

```
git clone https://github.com/yourusername/clinicconnect-api.git
cd clinicconnect-api
```


2. Set Up a Virtual Environment:

```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

```

3. Install Dependencies:

```
pip install -r requirements.txt

```

4. Run the Application:

```
uvicorn main:app --reload
```


## Access the Swagger UI

- Once the application is running, you can access the interactive API documentation (Swagger UI) at:

```
http://127.0.0.1:8000/docs
```

Use this interface to explore and test the available APIs.
