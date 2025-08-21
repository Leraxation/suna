#!/usr/bin/env python3
"""
Test script to check configuration values
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Environment Variables ===")
print(f"ENV_MODE: {os.getenv('ENV_MODE')}")
print(f"DISABLE_SANDBOX_IN_DEV: {os.getenv('DISABLE_SANDBOX_IN_DEV')}")

print("\n=== Configuration Object ===")
from utils.config import config

print(f"config.ENV_MODE: {config.ENV_MODE}")
print(f"config.ENV_MODE.value: {config.ENV_MODE.value}")
print(f"config.DISABLE_SANDBOX_IN_DEV: {config.DISABLE_SANDBOX_IN_DEV}")

print("\n=== Condition Check ===")
condition1 = config.ENV_MODE.value == "local"
condition2 = config.DISABLE_SANDBOX_IN_DEV
print(f"config.ENV_MODE.value == 'local': {condition1}")
print(f"config.DISABLE_SANDBOX_IN_DEV: {condition2}")
print(f"Both conditions: {condition1 and condition2}")