# PharmaQ-dataservice
# We Against Virus - TJ, DG, FT

Pharmacy queues prototype:
A simple portal where the local people can visualize the number of customers in the waiting line at a pharmacy


# Requirements:

Python3.6+ (Python3.7 works as well)

# Installation:
Install the requirements:
```bash
pip install -r requirements.txt
```

The database has to be moved into the `tmp` folder:
```bash
cp db_backend/test.db /tmp/test.db
```


# Running:

## 1. Run the DB application
```bash
cd db_backend
flask run --port 5001
```

## 2. Run the Google Map application
```bash
cd map_frontend
flask run --port 5000
```
