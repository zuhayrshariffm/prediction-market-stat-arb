from prefect import flow, task

from src.predict_stat_arb.analysis.build_house_2026_spread import main as build_spread
from src.predict_stat_arb.database.load_spread_to_postgres import main as load_spread


@task
def build_spread_dataset():
    build_spread()


@task
def load_spread_dataset_to_postgres():
    load_spread()


@flow(name="house-2026-spread-pipeline")
def house_2026_spread_pipeline():
    build_spread_dataset()
    load_spread_dataset_to_postgres()


if __name__ == "__main__":
    house_2026_spread_pipeline()
