import yaml
import pandas as pd
from faker import Faker
import numpy as np
from datetime import date
from typing import List, Dict, Any

def main():
    # Load configuration
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Access the schema as a list of key-value pairs for each attribute
    yaml_schema = config['schema']

    # Users defined number of rows to populate DataFrame
    yaml_rows = config['num_rows']

    # Initialise Faker
    random_generator = Faker()

    # Generate DataFrame
    df = generate_dataframe(yaml_schema, yaml_rows, random_generator)

    print(df.head())

def generate_dataframe(schema: List[Dict[str, Any]], num_rows: int, fake: Faker) -> pd.DataFrame:
    # Store data for DataFrame
    data = {}
    # Iterate through schema
    for column in schema:
        # Extract data from YAML config
        name = column['name']
        dtype = column['type']
        gen_config = column['generation']
        # Transform data according to its data type
        if dtype == 'integer':
            data[name] = generate_integer(gen_config, num_rows)
        elif dtype == 'string':
            data[name] = generate_string(gen_config, num_rows, fake)
        elif dtype == 'date':
            data[name] = generate_date(gen_config, num_rows, fake)
        elif dtype == 'boolean':
            data[name] = generate_boolean(gen_config, num_rows)
        elif dtype == 'categorical':
            data[name] = generate_categorical(gen_config, num_rows)
        else:
            raise ValueError(f"Unsupported data type: {dtype}")
    
    return pd.DataFrame(data)

def generate_integer(gen_config: List[Dict[str, Any]], num_rows: int) -> List[int]:
    if 'faker' in gen_config:
        # Implement faker-based integer generation if needed: faker.random_int()
        pass
    # Convert the ID to one-based indexing from 0-based
    elif 'start' in gen_config and 'step' in gen_config:
        start = gen_config['start']
        step = gen_config['step']
        return [start + step * i for i in range(num_rows)]  # Conversion using BODMAS
    elif 'min' in gen_config and 'max' in gen_config:
        return np.random.randint(gen_config['min'], gen_config['max'] + 1, size=num_rows)  # Makes max inclusive
    else:
        raise ValueError("Invalid integer generation configuration.")

def generate_string(gen_config: List[Dict[str, Any]], num_rows: int, fake: Faker) -> List[str]:
    # Returns a string or None
    faker_method = gen_config.get('faker')
    if faker_method:
        # Check if the method call is a legitimate faker attribute
        try:
            return [getattr(fake, faker_method)() for _ in range(num_rows)] # Gets attribute name and makes method call with ()
        except Exception as e:
            print(f"{type(e).__name__}. The 'faker' method: '{faker_method}' doesn't exist.")
    else:
        raise ValueError("String generation requires a 'faker' method.")

def generate_date(gen_config: List[Dict[str, Any]], num_rows: int, fake: Faker) -> List[date]:
    start_date = gen_config['start_date']
    end_date = gen_config['end_date']
    # Check if correct date format is given
    if isinstance(start_date, date) and isinstance(end_date, date):
        # Use faker to generate data between date range in config
        return [fake.date_between(start_date=start_date, end_date=end_date) for _ in range(num_rows)]
    else:
        raise TypeError("Invalid date format. Please enter format: YYYY-MM-DD")

def generate_boolean(gen_config: List[Dict[str, Any]], num_rows: int) -> List[bool]:
    prob = gen_config.get('probability', 0.5)
    # Check if value of probability is <= 1
    if 0 <= prob <= 1:
        return np.random.choice([True, False], size=num_rows, p=[prob, 1 - prob])
    else:
        raise ValueError("Please enter a probability value between 0 and 1")

def generate_categorical(gen_config: List[Dict[str, Any]], num_rows: int) -> List[str]:
    categories = gen_config['categories']
    probabilities = gen_config.get('probabilities', None)
    # Check if correct values are provided 
    if probabilities is None or sum(probabilities) != 1:
        raise ValueError("Please ensure the sum of probabilities is equal to 1 and provide valid categories.")
    else:
        return np.random.choice(categories, size=num_rows, p=probabilities)

if __name__ == "__main__":
    main()