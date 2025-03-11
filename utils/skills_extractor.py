import requests
import time
import random
import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv
from data_models.keywords_model import KeywordsModel
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


def transform_skills_data(input_data: List[Dict[Any, Any]]) -> KeywordsModel:
    """
    Transform the input skills data into KeywordsModel format.

    Args:
        input_data: List of dictionaries containing skill information

    Returns:
        KeywordsModel object with specialized and common skills
    """
    hard_skills = []
    soft_skills = []

    for skill in input_data:
        skill_name = skill['Name']
        skill_type = skill['Skill Type']

        if skill_type == 'Specialized Skill':
            hard_skills.append(skill_name)
        elif skill_type == 'Common Skill':
            soft_skills.append(skill_name)

    return KeywordsModel(
        hard_skills=hard_skills,
        soft_skills=soft_skills
    )

class SkillsExtractor:
    def __init__(self, confidence_threshold=0.99):
        """
        Initialize SkillsExtractor with credentials and settings.
        """
        self.client_id = os.getenv("LIGHTCAST_CLIENT_ID")
        self.client_secret = os.getenv("LIGHTCAST_CLIENT_SECRET")
        self.confidence_threshold = confidence_threshold
        self.token = None
        self.token_expiry = None
        self.auth_url = "https://auth.emsicloud.com/connect/token"
        self.skills_url = "https://emsiservices.com/skills/versions/latest/extract"
        self.logger = logging.getLogger(__name__)

    def get_access_token(self):
        """Get access token from Lightcast API."""
        try:
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": "emsi_open"
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.post(self.auth_url, data=payload, headers=headers)
            response.raise_for_status()

            token_data = response.json()
            self.token = token_data['access_token']
            # Set token expiry time (considering a 60-second buffer)
            self.token_expiry = time.time() + token_data['expires_in'] - 60

            return self.token

        except Exception as e:
            self.logger.error(f"Error getting access token: {e}")
            raise

    def is_token_valid(self):
        """Check if current token is valid."""
        return (self.token is not None and
                self.token_expiry is not None and
                time.time() < self.token_expiry)

    def ensure_valid_token(self):
        """Ensure we have a valid token, refresh if needed."""
        if not self.is_token_valid():
            self.get_access_token()

    def extract_skills(self, job_desc):
        """
        Extract skills from job description.
        """
        try:
            hard_skills = []
            soft_skills = []

            # Ensure we have a valid token
            self.ensure_valid_token()

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": job_desc,
                "confidenceThreshold": self.confidence_threshold
            }

            # Generate a random sleep duration between 3 and 10 seconds
            sleep_duration = random.randint(3, 10)
            time.sleep(sleep_duration) 
            
            response = requests.post(self.skills_url, json=payload, headers=headers)

            # If we get a 400/401, token might be expired despite our checks
            if response.status_code == 401 or response.status_code == 400:
                self.token = None
                self.token_expiry = None
                self.ensure_valid_token()
                # Retry the request with new token
                headers["Authorization"] = f"Bearer {self.token}"
                response = requests.post(self.skills_url, json=payload, headers=headers)

            response.raise_for_status()
            data = response.json()

            # Extract and transform skills data
            skills = []
            if 'data' in data:
                for item in data['data']:
                    if item.get('confidence', 0) >= self.confidence_threshold:
                        skill_info = item['skill']
                        skills.append({
                            'ID': skill_info['id'],
                            'Name': skill_info['name'],
                            'Skill Type': skill_info['type']['name'],
                            'Confidence': item['confidence']
                        })


            for skill in skills:
                skill_name = skill['Name']
                skill_type = skill['Skill Type']

                cleaned_skill_name = re.sub(r'\(.*?\)', '', skill_name)

                # Strip any extra whitespace
                cleaned_skill_name = cleaned_skill_name.strip()

                if skill_type == 'Specialized Skill':
                    hard_skills.append(cleaned_skill_name)
                elif skill_type == 'Common Skill':
                    soft_skills.append(cleaned_skill_name)

            keywords_model = KeywordsModel(
                hard_skills=hard_skills,
                soft_skills=soft_skills
            )

            return keywords_model.dict()


        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}")
            return []


# if __name__ == '__main__':
#
#     extractor = SkillsExtractor()
#
#     description = """
#     Qualifications Expertise with ETL, SQL and data modelingExperience and appreciation
#     for robust validation and documentation Strong communication skills to collaborate with technical and non-technical stakeholders Ability to explain complex technical concepts in simple terms A passion for data and its potential to drive business value Ability to work in a fast-paced environment and adapt to evolving business needs Ability to understand and adhere to the Professional Code of Conduct 3+ years of experience in data engineering, with a focus on building data pipelines and data transformations Demonstrated proficiency with dbt, including experience in creating, maintaining, and optimizing dbt models Expertise in Snowflake data warehouse development, including schema design, query optimization, and storage managementStrong knowledge of SQL and experience working with large datasets Strong problem-solving skills and attention to detail, with the ability to work independently and as part of a team Responsibilities At Groups, Data Engineer will work closely with other data engineers, analysts, and software developers As a Data Engineer focusing on dbt development in Snowflake, you will play a pivotal role in supporting care delivery and operations by transforming raw data into meaningful, business-ready datasets This role requires strong experience with SQL query writing, data modeling, dbt, and Snowflake Design, develop, and maintain scalable and optimized data models in dbt and Snowflake Collaborate with business stakeholders, data analysts, and data scientists to understand data requirements and ensure robust data models that meet business needs Implement and maintain dbt best practices, including version control, testing, and documentation to ensure quality and reliability in data pipelinesOptimize Snowflake queries, storage, and performance to ensure efficient data processing and retrieval Continuously monitor and improve the performance of data pipelines and the overall health of the data infrastructureWork with cross-functional teams to resolve data quality issues, implement data governance practices, and ensure data consistency and accuracy Maintain clear and organized documentation for dbt models, transformations, and data workflows
#
#      """
#     print(extractor.extract_skills(description))





