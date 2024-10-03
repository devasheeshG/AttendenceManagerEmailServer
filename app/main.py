# File: app/main.py
# Description: Main application file with scheduler and core logic.

import asyncio
import time
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.utils.database import Session as DbSessionLocal
from app.utils.db_schemas import User, Attendance, NotificationLevel
from app.utils.attendance_manager import AttendanceManager
from app.utils.email_client import EmailService
from app.config import get_settings
from app.logger import get_logger
from app.utils.models import AttendanceRecord

settings = get_settings()
logger = get_logger()

email_service = EmailService()

async def update_attendance(db: Session, user: User):
    try:
        attendance_manager = AttendanceManager(user.username, user.password)
        await attendance_manager.login()
        new_attendance_data: List[AttendanceRecord] = await attendance_manager.get_attendance_details()
        await attendance_manager.close()

        for new_data in new_attendance_data:
            old_attendance = db.query(Attendance).filter(
                Attendance.user_id == user.id,
                Attendance.subject_code == new_data.subject_code
            ).first()

            if old_attendance:
                # Calculate differences
                new_attended = new_data.present_hours - old_attendance.attended_hours
                new_absent = new_data.absent_hours - old_attendance.absent_hours

                # Update database
                old_attendance.max_hours = new_data.total_hours
                old_attendance.attended_hours = new_data.present_hours
                old_attendance.absent_hours = new_data.absent_hours
                old_attendance.total_percentage = new_data.percentage
                db.commit()

                # Send notifications based on changes and user preferences
                if new_attended > 0 and (user.notification_level == NotificationLevel.ALL or user.notification_level == NotificationLevel.PRESENT_ONLY):
                    email_service.send_attendance_notification(
                        email=user.email,
                        name=user.name,
                        notification_type='present',
                        attendance_data=new_data,
                        change=new_attended
                    )
                if new_absent > 0 and (user.notification_level == NotificationLevel.ALL or user.notification_level == NotificationLevel.ABSENT_ONLY):
                    email_service.send_attendance_notification(
                        email=user.email,
                        name=user.name,
                        notification_type='absent',
                        attendance_data=new_data,
                        change=new_absent
                    )
            else:
                # New subject, add to database
                new_attendance = Attendance(
                    user_id=user.id,
                    subject_code=new_data.subject_code,
                    subject_name=new_data.subject_name,
                    max_hours=new_data.total_hours,
                    attended_hours=new_data.present_hours,
                    absent_hours=new_data.absent_hours,
                    total_percentage=new_data.percentage
                )
                db.add(new_attendance)
                db.commit()

                # Send notifications based on changes and user preferences
                if new_data.absent_hours > 0 and (user.notification_level == NotificationLevel.ALL or user.notification_level == NotificationLevel.PRESENT_ONLY):
                    email_service.send_attendance_notification(
                        email=user.email,
                        name=user.name,
                        notification_type='present',
                        attendance_data=new_data,
                        change=new_data.absent_hours
                    )
                if new_data.absent_hours > 0 and (user.notification_level == NotificationLevel.ALL or user.notification_level == NotificationLevel.ABSENT_ONLY):
                    email_service.send_attendance_notification(
                        email=user.email,
                        name=user.name,
                        notification_type='absent',
                        attendance_data=new_data,
                        change=new_data.absent_hours
                    )

        logger.info(f"Successfully updated attendance for user: {user.username}")
    
    except Exception as e:
        logger.error(f"Error updating attendance for user: {user.username}. Error: {str(e)}")

async def update_all_users():
    logger.info("Updating attendance for all users")
    db = DbSessionLocal()
    try:
        users = db.query(User).all()
        logger.debug(f"Updating attendance for {len(users)} users")
        tasks = [update_attendance(db, user) for user in users]
        await asyncio.gather(*tasks)
    finally:
        db.close()

async def start_scheduler():
    # Send debug email to me to check if email service is working
    test_emails = ["devasheeshmishra4@gmail.com", "sharmayank1608@gmail.com"]
    for email in test_emails:
        email_service.send_boot_notification(email)
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_all_users, 'interval', minutes=settings.UPDATE_INTERVAL // 60)
    scheduler.start()
    logger.info("Scheduler started")
    
    # Run the first update immediately
    # await update_all_users()

    # Keep the scheduler running
    while True:
        await asyncio.sleep(1)

async def main():
    try:
        # Initialize and start the scheduler
        await start_scheduler()
        # await update_all_users()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    finally:
        # Clean up any resources if needed
        pass

if __name__ == "__main__":
    asyncio.run(main())
