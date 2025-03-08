from datetime import datetime, timedelta

def is_dst_in_eastern_time(dt):
    """
    Determine if a given datetime is in Daylight Saving Time for US Eastern Time.
    
    For US Eastern Time, DST starts on the second Sunday in March and ends on the first Sunday in November.
    
    Args:
        dt (datetime): The datetime to check
        
    Returns:
        bool: True if the datetime is in DST, False otherwise
    """
    # Get year from the date
    year = dt.year
    
    # DST starts on the second Sunday in March at 2 AM
    march_date = datetime(year, 3, 1)
    # Find the first Sunday in March
    while march_date.weekday() != 6:  # 6 is Sunday
        march_date += timedelta(days=1)
    # Find the second Sunday in March
    dst_start = march_date + timedelta(days=7)
    dst_start = dst_start.replace(hour=2)
    
    # DST ends on the first Sunday in November at 2 AM
    november_date = datetime(year, 11, 1)
    # Find the first Sunday in November
    while november_date.weekday() != 6:  # 6 is Sunday
        november_date += timedelta(days=1)
    dst_end = november_date.replace(hour=2)
    
    # Check if the date is within DST period
    return dst_start <= dt < dst_end

def ny_to_utc(dt):
    """
    Convert New York time to UTC.
    
    Args:
        dt (datetime): The datetime in New York time
        
    Returns:
        datetime: The datetime in UTC
    """
    # Check if the datetime is in DST
    is_dst = is_dst_in_eastern_time(dt)
    
    # Apply the offset
    if is_dst:
        # During DST, New York is UTC-4
        utc_offset = timedelta(hours=4)
    else:
        # During standard time, New York is UTC-5
        utc_offset = timedelta(hours=5)
    
    # Convert to UTC
    return dt + utc_offset

def utc_to_ny(dt):
    """
    Convert UTC to New York time.
    
    Args:
        dt (datetime): The datetime in UTC
        
    Returns:
        datetime: The datetime in New York time
    """
    # First, create a copy of the datetime to avoid modifying the original
    dt_copy = dt.replace()
    
    # Try both DST and non-DST offsets to find the correct one
    # This is necessary because we don't know if the UTC time corresponds to DST or not in NY
    
    # Try non-DST first (UTC-5)
    ny_time_non_dst = dt_copy - timedelta(hours=5)
    
    # Check if this NY time would be in DST
    if is_dst_in_eastern_time(ny_time_non_dst):
        # If it would be in DST, then we used the wrong offset
        # During DST, New York is UTC-4
        return dt_copy - timedelta(hours=4)
    else:
        # If it would not be in DST, then we used the correct offset
        return ny_time_non_dst

def format_datetime(dt, include_timezone=False):
    """
    Format a datetime object as a string.
    
    Args:
        dt (datetime): The datetime to format
        include_timezone (bool): Whether to include the timezone in the output
        
    Returns:
        str: The formatted datetime string
    """
    formatted = dt.strftime("%Y-%m-%d %H:%M")
    if include_timezone:
        is_dst = is_dst_in_eastern_time(dt)
        tz = "EDT" if is_dst else "EST"
        formatted += f" {tz}"
    return formatted 