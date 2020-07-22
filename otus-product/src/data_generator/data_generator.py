from models import Product

from faker import Faker

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from db import construct_db_url
from config import load_config

import logging

log = logging.getLogger(__name__)


def generate_products(session: Session, count: int) -> list:
    faker = Faker('ru_RU')
    result = []
    for i in range(count):
        name = " ".join(faker.words(nb=3))
        description = faker.texts(nb_texts=1, max_nb_chars=200)[0]
        product = Product(name=name, description=description)
        result.append(product)
        session.add(product)
        log.debug(f"Generate product: {product}")
    session.commit()
    for i in result:
        session.refresh(i)
    return result


def main(config_path: str):
    config = load_config(config_path)
    config_app = config['app']
    config_db = config['database']
    log_level = logging.getLevelName(config_app.get('loglevel', 'DEBUG'))
    logging.basicConfig(level=log_level)
    db_url = construct_db_url(config_db)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    products_count = int(float(config_app.get('products_count', 100)))
    generate_products(session, products_count)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Provide path to config file")
    args = parser.parse_args()

    if args.config:
        main(args.config)
    else:
        parser.print_help()
