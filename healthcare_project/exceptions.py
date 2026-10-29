from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize error responses across all APIs.
    """
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data

        # Determine a human-readable message
        message = "An error occurred while processing your request."
        errors = data

        if isinstance(data, dict):
            if 'detail' in data:
                message = str(data['detail'])
            elif 'non_field_errors' in data:
                message = "; ".join([str(e) for e in data['non_field_errors']])
            else:
                first_key = next(iter(data))
                first_val = data[first_key]
                if isinstance(first_val, list) and len(first_val) > 0:
                    message = f"{first_key}: {first_val[0]}"
                else:
                    message = f"{first_key}: {first_val}"

        elif isinstance(data, list):
            message = "; ".join([str(e) for e in data])

        response.data = {
            "status": "error",
            "status_code": response.status_code,
            "message": message,
            "details": errors
        }

    return response
