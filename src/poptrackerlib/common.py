#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Common classes and functions.

import json


class PopTrackerEncoder(json.JSONEncoder):
    def default(self, obj):
        # Define generic dunder JSON function to use for JSON encoding.
        if hasattr(obj, '__json__'):
            return obj.__json__()
        # Fall back to attribute dict for regular objects.
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        # Otherwise fall back to the default JSON encoder.
        return super().default(obj)


def dumps(obj, **kwargs):
    # Define a custom JSON dump function to use the custom encoder.
    return json.dumps(obj, cls=PopTrackerEncoder, **kwargs)
