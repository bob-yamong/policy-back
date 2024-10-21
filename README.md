# policy-back
## requirements
### Using venv
if you don't have a venv, you can install it.
```sh
sudo apt install python3.10-venv -y
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

### Using Conda
if you don't have a miniconda(or anaconda), you can install it on this url.
https://docs.anaconda.com/free/miniconda/index.html

```sh
conda create -n policy_back python=3.9
conda activate policy_back
pip install -r requirements.txt
```

## usage
```sh
uvicorn main:app --reload
```

or 

```sh
python main.py
```

## Structure

```sh
policy_back
├── core
├── crud
├── database
├── README.md
├── requirements.txt
├── routes
│   └── __init__.py
├── schema
├── utils
└── main.py
```
- `core`: Files related to settings, etc.
- `database`: database related files
- `crud`: CRUD operations for each table
- `routes`: API routes
- `schema`: Pydantic models for request and response
- `utils`: utility functions