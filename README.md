# News API ETL data pipeline

This repo contains a simple data pipeline ingesting data from News API ([API docs](https://newsapi.org/docs)).

## Pipeline overview

High level architecture of the pipeline:

![News API ETL architecture](static/News%20API%20ETL.png)

## Running pipeline
You can either create a virtual environment and install all the requirements with `pip install -r requirements.txt` or use `Docker` & `docker-compose`.

All secrets - such as News API key & AWS keys - are kept in `.env` file located at the root of the repository (use `.env.example` as a guide to fill in appropriate variables).

To run the pipeline from virtual environment, type:
```
python main.py
```

To run the pipeline when using Docker, type:
```
docker-compose build
docker-compose run news_api_etl python main.py
```

### Setting up transformed data destination
#### S3 Bucket
By default, pipeline is configured to use AWS S3 bucket as its target (`news_api_etl.loaders.S3CSVLoader` class handles upload to S3). When using S3 as a destination, make sure that you fill in appropriate env variables in `.env` file and that your IAM user is configured properly (it has sufficient permissions to put objects into `s3://<your_bucket_name/*` keys).
```python
data_loader = S3CSVLoader(
    bucket_name=os.getenv("TARGET_BUCKET_NAME"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
```

#### Local disk
If you'd like to ingest the data into your local disk instead of S3, then use `news_api_etl.loaders.LocalDiskCSVLoader`.

Just instantiate it inside `main.py` file and pass as an argument when creating pipeline object, for example:

```python
data_loader = LocalDiskCSVLoader(pathlib.Path(__file__).parent / "extracted_data")
```

Above snippet would instantiate a loader object that would save CSVs to `extracted_data` directory on your hard drive.

## Running tests
To execute project's tests, please run below command:
```
docker-compose build
docker-compose run news_api_etl python -m unittest
```

S3 dependency is mocked with `moto` library.

## Other considerations
### News API Developer account limitations
I used News API developer account for this project and it comes with a limitation of fetching 100 results at maximum (if you try to paginate to any page that has an offset greater than 100, you'd get a `426` status code in response).

Exemplary payload of such response:
```python
{'status': 'error',
 'code': 'maximumResultsReached',
 'message': 'You have requested too many results. Developer accounts are limited to a max of 100 results. You are trying to request results 700 to 800. Please upgrade to a paid plan if you need more results.'
```

I haven't implemented any pagination mechanism in HTTP API client. Query param `&pageSize=100` is added when fetching top headlines to get the biggest amount of results possible for this type of account.
