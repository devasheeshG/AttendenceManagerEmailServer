# Path: app/utils/db_schemas.py
# Description: This file contains the database schema for the application.

import enum
from app.utils.database import DatabaseBase
from sqlalchemy import Column, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Float, CheckConstraint, Enum, UUID, text
from sqlalchemy.orm import relationship

class NotificationLevel(enum.Enum):
    PRESENT_ONLY = "present_only"
    ABSENT_ONLY = "absent_only"
    ALL = "all"

class User(DatabaseBase):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    notification_level = Column(Enum(NotificationLevel), nullable=False)
    
    __table_args__ = (
        CheckConstraint("email ~ '^[^@]+@[^@]+\\.[^@]+$'", name='check_email_format'),
        CheckConstraint("length(username) == 6", name='check_username_length'),
    )

# class Subject(DatabaseBase):
#     __tablename__ = "subjects"

#     id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), nullable=False)
#     subject_code = Column(String, unique=True, index=True)
#     subject_name = Column(String, nullable=False)
#     alias = Column(String)

class Attendance(DatabaseBase):
    __tablename__ = "attendance"

    user_id = Column(UUID(as_uuid=True), nullable=False)
    subject_code = Column(String, nullable=False)
    subject_name = Column(String, nullable=False)
    max_hours = Column(Integer, nullable=False)
    attended_hours = Column(Integer, nullable=False)
    absent_hours = Column(Integer, nullable=False)
    total_percentage = Column(Float, nullable=False)

    # subject = relationship("Subject", backref="attendance")
    user = relationship("User", backref="attendance")

    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        # ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        PrimaryKeyConstraint('user_id', 'subject_code', name='attendance_pk'),
    )
