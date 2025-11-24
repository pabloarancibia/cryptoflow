import csv
import time
from typing import Generator, Dict


class MarketDataReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def start_stream(self) -> Generator[Dict, None, None]:
        """
        Yields market data row by row.
        This acts as a 'Lazy Loading' engine.
        """
        with open(self.file_path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # Simulate network latency or processing time if needed
                # time.sleep(0.01)

                # Yield pauses execution here and returns the row
                # Next time we call next(), it resumes right here
                yield row