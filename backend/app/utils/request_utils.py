import logging
from flask import Request
from typing import Dict, Any

# Set up logger
logger = logging.getLogger(__name__)

def get_request_data(request: Request) -> Dict[str, Any]:
    """
    Extract data from a Flask request object.

    Args:
        request: Flask request object

    Returns:
        Dict containing the request data
    """
    logger.info(f"Processing request: {request.method} {request.path}")
    logger.info(f"Content-Type: {request.headers.get('Content-Type')}")

    try:
        if request.is_json:
            data = request.get_json()
            logger.info(f"JSON data received: {data}")
            return data
        elif request.form:
            data = request.form.to_dict()
            logger.info(f"Form data received: {data}")
            return data
        elif request.data:
            # Try to parse raw data if present
            import json
            try:
                data = json.loads(request.data.decode('utf-8'))
                logger.info(f"Raw data parsed as JSON: {data}")
                return data
            except json.JSONDecodeError:
                logger.warning(f"Could not parse raw data as JSON: {request.data}")
                return {}
        else:
            logger.warning("No data found in request")
            return {}
    except Exception as e:
        logger.error(f"Error extracting request data: {str(e)}", exc_info=True)
        return {}
