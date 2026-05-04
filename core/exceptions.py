from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def global_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "status": "error",
            "code": getattr(exc, 'default_code', 'error'),
            "message": "",
            "details": response.data
        }

        # Try to extract a clean message
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_data["message"] = response.data['detail']
            elif 'non_field_errors' in response.data:
                custom_data["message"] = response.data['non_field_errors'][0]
            else:
                # Use the first key's error as the message
                first_key = list(response.data.keys())[0]
                custom_data["message"] = f"{first_key}: {response.data[first_key]}"
        elif isinstance(response.data, list):
            custom_data["message"] = response.data[0]

        response.data = custom_data

    return response
