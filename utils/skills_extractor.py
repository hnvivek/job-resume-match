import requests
import time
import os
import logging
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

                if skill_type == 'Specialized Skill':
                    hard_skills.append(skill_name)
                elif skill_type == 'Common Skill':
                    soft_skills.append(skill_name)

            keywords_model = KeywordsModel(
                hard_skills=hard_skills,
                soft_skills=soft_skills
            )

            return keywords_model.dict()


        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}")
            return []



#
# if __name__ == '__main__':
#
#     extractor = SkillsExtractor()
#
#     description = """Qualifications
# An active Secret security clearance is required in order to qualify for this role
# 2 years relevant experience with Bachelors in related field; 0 years experience with Masters in related field; or High School Diploma or equivalent and 6 years relevant experience
# Client requirements: Bachelor’s degree and 2-4 years of experience OR a Master’s degree with 0-2 years of experience
# In some cases, educational requirements may be adjusted or waived for more than 8 years of applicable work experience
# Work experience may be adjusted for highly specialized knowledge or uniquely applicable experience
# An active Secret security clearance is required
# Interest in data and data analytics
# Experience with MS Excel functions for data analysis
# Experience with SQL for data queries
# Knowledge or interest in Data Dashboards (Tableau, PowerBI, Looker, etc.)
# Knowledge of scripting (Python)
# Knowledge of database/technology/processes (PostgreSQL, Apache Kafka, ETL, noSQL databases, etc.)
# Ability to communicate in person, over virtual platforms, and in writing with teammates, technical Subject Matter Experts (SME), and senior leaders
# Ability to work in a team environment
# On-site support required (Must Interface with customers on a daily basis)
# Benefits
# Anticipated Salary Range: $70,561.00 - $100,802.00
# We offer competitive benefits such as best-in-class medical, dental and vision plan choices; wellness resources; employee assistance programs; Savings Plan Options (401(k)); financial planning tools, life insurance; employee discounts; paid holidays and paid time off; tuition reimbursement; as well as early childhood and post-secondary education scholarships
# Bonus/other non-recurrent compensation is occasionally offered for qualified positions, and if applicable to this role will be addressed by the recruiter at the screening phase of application
# Responsibilities
# With advanced technologies to enable mission readiness, HII understands that preparation requires full coordination—not readiness in piece-parts
# For more than 40 years, the U.S. Navy has entrusted HII to maintain and modernize the vast majority of its fleet
# With a holistic approach to life-cycle maritime defense systems—from small watercraft to submarines, surface combatants and aircraft carriers—HII ensures a high state of readiness
# HII Mission Technologies is seeking a Data Engineer with skilled talent to join a team that identifies, develops, manages, and analyzes data (geospatial, force structure, and system characteristic), digital applications, and policy to support virtual, constructive, and gaming simulation-enabled Joint and Combatant Command training
# This Data Engineer position will assist in improving the processes in which data is collected, managed, and converted for the purposes of the Joint Staff (JS) J7, Deputy Director of Joint Training (DDJT) data initiatives
# Curation of data from various authoritative sources into schemas and formats that can be consumed by applications of the DDJT’s Joint Training Synthetic Environment (JTSE)
# Assist in the development of Data Pipelines for data cleaning, transformation, and aggregation
# Reduce amount of manual touch labor required to transform data into useable formats by enhancing data quality and efficiency
# Assist in management of DDJT’s data and analytics operations including architecture, user requirements, software development, report development, and Artificial Intelligence (AI)/Machine Learning (ML) integration
#      """
#     print(extractor.extract_skills(description))
#
#     # Transform the data
#     result = extractor.extract_skills(description)
#
#     # Print the result
#     print(result.json(indent=2))

