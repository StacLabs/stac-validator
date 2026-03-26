"""Test schema caching behavior."""

from stac_validator.validate import StacValidate
from stac_validator.utilities import fetch_and_parse_schema


def test_schema_cache_with_extensions():
    """Test that extension schemas are cached across validations."""
    fetch_and_parse_schema.cache_clear()
    
    stac_file = "tests/test_data/v100/extended-item.json"
    
    # First validation
    stac1 = StacValidate(stac_file)
    stac1.run()
    cache_info_1 = fetch_and_parse_schema.cache_info()
    hits_after_first = cache_info_1.hits
    misses_after_first = cache_info_1.misses
    size_after_first = cache_info_1.currsize
    
    # Second validation with same file
    stac2 = StacValidate(stac_file)
    stac2.run()
    cache_info_2 = fetch_and_parse_schema.cache_info()
    hits_after_second = cache_info_2.hits
    misses_after_second = cache_info_2.misses
    size_after_second = cache_info_2.currsize
    
    # Verify cache is working
    assert size_after_first > 0, "Cache should contain schemas after first validation"
    assert size_after_second == size_after_first, "Cache size should not grow on second validation"
    assert hits_after_second > hits_after_first, "Cache hits should increase on second validation"
    assert misses_after_second == misses_after_first, "No new misses on second validation"
    
    fetch_and_parse_schema.cache_clear()
