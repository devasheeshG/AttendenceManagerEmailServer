# Path: app/utils/models.py
# Description: This file contains pydantic models for the application.

from pydantic import BaseModel

class AttendanceRecord(BaseModel):
    subject_name: str
    subject_code: str
    total_hours: int
    present_hours: int
    absent_hours: int
    percentage: float
