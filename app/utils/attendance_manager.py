# Path: app/utils/attendance_manager.py
# Description: SRM Student Portal Attendance Manager API Interface.

from io import BytesIO, StringIO
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import pandas as pd
import pytesseract
import httpx
from typing import List

from app.logger import get_logger
from app.config import get_settings
from app.utils.models import AttendanceRecord

settings = get_settings()
logger = get_logger()

SRM_STUDENT_PORTAL_URI = "https://sp.srmist.edu.in/srmiststudentportal/students/loginManager/youLogin.jsp"
SRM_STUDENT_PORTAL_GET_CAPTCHA_URI = "https://sp.srmist.edu.in/srmiststudentportal/captchas"
ATTENDANCE_PAGE_URI = "https://sp.srmist.edu.in/srmiststudentportal/students/report/studentAttendanceDetails.jsp"

class AttendanceManager:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        }

    async def login(self) -> None:
        """Login to SRM Student Portal."""
        try:
            # Make GET request to SRM Student Portal
            await self.client.get(SRM_STUDENT_PORTAL_URI, headers=self.headers)

            # Get Captcha
            captcha_response = await self.client.get(
                SRM_STUDENT_PORTAL_GET_CAPTCHA_URI, headers=self.headers
            )
            captcha_text = pytesseract.image_to_string(
                PILImage.open(BytesIO(captcha_response.content))
            ).strip()

            # Login
            response = await self.client.post(
                SRM_STUDENT_PORTAL_URI,
                data={
                    "txtPageAction": "1",
                    "txtAN": self.username,
                    "txtSK": self.password,
                    "hdnCaptcha": captcha_text,
                }
            )
            
            # Check for Login Error
            if "Login Error : Invalid net id or password" in response.text:
                logger.error(f"Invalid Username or Password for user: {self.username}")
                raise ValueError("Invalid Username or Password")

            # Check for Captcha Error, If so then try again
            if "Invalid Captcha...." in response.text:
                logger.warning(f"Invalid Captcha for user: {self.username}, Trying Again...")
                await self.login()

            # Check status code
            # status should be `302` because after successful login it redirects to another page 
            if response.status_code != 302:
                logger.error(f"Login Failed for user: {self.username}. Status Code: {response.status_code}")
                raise ConnectionError("SRM Student Portal is Down or Login Failed")
            
            logger.info(f"Successfully logged in for user: {self.username}")
        
        except Exception as e:
            logger.error(f"Error during login for user: {self.username}. Error: {str(e)}")
            raise

    async def get_attendance_details(self) -> List[AttendanceRecord]:
        """Get main Attendance Table."""
        try:
            response = await self.client.post(ATTENDANCE_PAGE_URI, headers=self.headers)
            attendance_page = BeautifulSoup(response.text, "html.parser")

            # Get Attendance Table
            attendance_table = attendance_page.find_all("table", class_="table")[0]

            # Convert to DataFrame
            attendance_df = pd.read_html(StringIO(str(attendance_table)))[0]

            # Remove Unwanted Subject Codes
            blacklist_codes = ["Total"]
            attendance_df = attendance_df[~attendance_df["Code"].isin(blacklist_codes)]
            logger.info(f"Successfully retrieved attendance details for user: {self.username}")
            
            return [
                AttendanceRecord(
                    subject_name=row["Description"],
                    subject_code=row["Code"],
                    total_hours=int(row["Max. hours"]),
                    present_hours=int(row["Att. hours"]),
                    absent_hours=int(row["Absent hours"]),
                    percentage=float(row["Total Percentage"])
                )
                for _, row in attendance_df.iterrows()
            ]
        
        except Exception as e:
            logger.error(f"Error retrieving attendance details for user: {self.username}. Error: {str(e)}")
            raise

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
        
