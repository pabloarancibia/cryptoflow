import pytest
from src.domain.market_data import MarketDataReader


# pytest automatically detects the 'tmp_path' argument and injects a temporary directory path
def test_stream_parses_csv_correctly(tmp_path):
    # --- 1. SETUP: Create a fake CSV file ---

    # Create a dummy file object inside the temporary directory
    fake_csv_file = tmp_path / "fake_market_data.csv"

    # Write some controlled test data into it
    # We use a known price (100.0) to make asserting easy
    fake_content = """symbol,price,timestamp
BTCUSD,100.0,12:00:01
ETHUSD,200.0,12:00:02
"""

    fake_csv_file.write_text(fake_content, encoding='utf-8')

    # --- 2. EXECUTION: Run your code ---

    # Pass the path of the fake file (convert to string for safety)
    loader = MarketDataReader(str(fake_csv_file))
    stream = loader.start_stream()

    row1 = next(stream)
    row2 = next(stream)

    # --- 3. ASSERTION: Check the results ---

    assert row1['symbol'] == 'BTCUSD'
    assert row1['price'] == '100.0'

    assert row2['symbol'] == 'ETHUSD'
    assert row2['price'] == '200.0'

    # Verify that the stream stops (raises StopIteration) after 2 lines
    with pytest.raises(StopIteration):
        next(stream)