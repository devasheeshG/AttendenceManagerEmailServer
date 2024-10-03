# Path: app/utils/attendance_manager.py
# Description: SRM Student Portal Attendance Manager API Interface.

from io import BytesIO, StringIO
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import pandas as pd
import pytesseract
import httpx

from app.logger import logger
from app.config import get_settings

settings = get_settings()

SRM_STUDENT_PORTAL_URI = "https://sp.srmist.edu.in/srmiststudentportal/students/loginManager/youLogin.jsp"
SRM_STUDENT_PORTAL_GET_CAPTCHA_URI = "https://sp.srmist.edu.in/srmiststudentportal/captchas"
ATTENDANCE_PAGE_URI = "https://sp.srmist.edu.in/srmiststudentportal/students/report/studentAttendanceDetails.jsp"

class AttendanceManager:
    """SRM Student Portal Attendance Manager API Interface."""
    def __init__(self, username: str = settings.SRM_PORTAL_USERNAME, password: str = settings.SRM_PORTAL_PASSWORD) -> None:
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        }

    async def login(self) -> bool:
        """Login to SRM Student Portal."""
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
            logger.warning(f"Invalid Username or Password")
            return False

        # Check for Captcha Error, If so then try again
        if "Invalid Captcha...." in response.text:
            logger.warning(f"Invalid Captcha, Trying Again...")
            await self.login()

        # Check status code
        # status should be `302` because after successful login it redirects to another page 
        if response.status_code != 302:
            logger.error(f"SRM Student Portal is Down or Login Failed. Status Code: {response.status_code}")
            return False
        
    async def attendance_page(self) -> BeautifulSoup:
        """Get Attendance Page."""
        # Make GET request to Attendance Page
        response = await self.client.post(ATTENDANCE_PAGE_URI, headers=self.headers)

        # Parse HTML
        attendance_page = BeautifulSoup(response.text, "html.parser")

        return attendance_page

    async def get_attendance_details(self) -> pd.DataFrame:
        """Get main Attendance Table."""
        attendance_page = await self.attendance_page()

        # Get Attendance Table
        attendance_table = attendance_page.find_all("table", class_="table")[0]

        # Convert to DataFrame
        attendance_df = pd.read_html(StringIO(str(attendance_table)))[0]

        # Remove Unwanted Subject Codes
        blacklist_codes = ["Total"]
        attendance_df = attendance_df[~attendance_df["Code"].isin(blacklist_codes)]

        return attendance_df
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
