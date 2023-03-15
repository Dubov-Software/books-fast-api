# books-fast-api
Sample books REST Api using FastAPI

# pip
```
pip install fastapi fastapi_users pydantic uvicorn ujson motor
```

# Create conda env
```
conda create -n dev_env python=3.9.13 anaconda
conda activate dev_env
```

# Run inside the env
```
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --log-level=debug --access-logfile=-
```