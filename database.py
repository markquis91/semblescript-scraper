from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import *

base = declarative_base()


class Account(base):
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    name = Column(String)


class Prospect(base):
    __tablename__ = "prospects"
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    data_crawled = Column(Boolean, default=False)
    account_id = Column(BigInteger)


class LinkedinProfile(base):
    __tablename__ = "linkedin_profiles"
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    title = Column(String)
    about = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    prospect_id = Column(BigInteger, ForeignKey('prospects.id'))
    experiences = relationship("LinkedinExperience")
    educations = relationship("LinkedinEducation")
    skills = relationship("LinkedinSkill")
    posts = relationship("LinkedinPost")


class LinkedinExperience(base):
    __tablename__ = "linkedin_experiences"
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    company = Column(String, nullable=True)
    position = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    linkedin_data_id = Column(BigInteger, ForeignKey('linkedin_profiles.id'))


class LinkedinEducation(base):
    __tablename__ = "linkedin_educations"
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    school = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    linkedin_data_id = Column(BigInteger, ForeignKey('linkedin_profiles.id'))


class LinkedinSkill(base):
    __tablename__ = "linkedin_skills"
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=True)
    endorsed = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    linkedin_data_id = Column(BigInteger, ForeignKey('linkedin_profiles.id'))


class LinkedinPost(base):
    __tablename__ = "linkedin_posts"
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    post_id = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    linkedin_data_id = Column(BigInteger, ForeignKey('linkedin_profiles.id'))


class SembleSchema:
    def __init__(self, host, port, username, password, database):
        connection_str = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(connection_str)

    def get_crawl_tasks(self):
        with Session(self.engine) as se:
            prospects = se.query(Prospect).order_by(Prospect.data_crawled, desc(Prospect.created_at)).all()
            tasks = []
            for prospect in prospects:
                account_id = prospect.account_id
                account = se.query(Account).where(Account.id == account_id).first()
                company = account.name
                tasks.append({
                    'prospect_id': prospect.id,
                    'first_name': prospect.first_name,
                    'last_name': prospect.last_name,
                    'company': company
                })
            return tasks

    def get_last_post_id(self, prospect_id):
        with Session(self.engine) as se:
            profile = se.query(LinkedinProfile).where(LinkedinProfile.prospect_id == prospect_id).first()
            if profile:
                profile_id = profile.id
                last_post = se.query(LinkedinPost).where(LinkedinPost.linkedin_data_id == profile_id)\
                    .order_by(desc(LinkedinPost.created_at)).first()
                if last_post:
                    return last_post.post_id
                return None
            return None

    def insert_profile(self, title, about, prospect_id):
        with Session(self.engine) as se:
            profile = se.query(LinkedinProfile).where(LinkedinProfile.prospect_id == prospect_id).first()
            if profile:
                profile.title = title
                profile.about = about
                se.commit()
                return profile.id

            profile = LinkedinProfile(prospect_id=prospect_id, title=title, about=about)
            se.add(profile)
            # se.flush()
            se.commit()
            return profile.id

    def insert_experiences(self, profile_id, experiences):
        with Session(self.engine) as se:
            se.query(LinkedinExperience).filter(LinkedinExperience.linkedin_data_id == profile_id).delete()
            se.commit()
            experience_instances = []
            for experience in experiences:
                experience_instances.append(
                    LinkedinExperience(
                        linkedin_data_id=profile_id,
                        company=experience['company'],
                        position=experience['position'],
                        duration=experience['duration'],
                        location=experience['location'],
                        description=experience['description'],
                        created_at=datetime.now()
                    )
                )
            se.add_all(experience_instances)
            se.commit()

    def insert_educations(self, profile_id, educations):
        with Session(self.engine) as se:
            se.query(LinkedinEducation).filter(LinkedinEducation.linkedin_data_id == profile_id).delete()
            education_instances = []
            for education in educations:
                education_instances.append(
                    LinkedinEducation(
                        linkedin_data_id=profile_id,
                        school=education['school'],
                        degree=education['degree'],
                        duration=education['duration'],
                        created_at=datetime.now()
                    )
                )
            se.add_all(education_instances)
            se.commit()

    def insert_skills(self, profile_id, skills):
        with Session(self.engine) as se:
            se.query(LinkedinSkill).filter(LinkedinSkill.linkedin_data_id == profile_id).delete()
            se.commit()
            skill_instances = []
            for skill in skills:
                skill_instances.append(
                    LinkedinSkill(
                        linkedin_data_id=profile_id,
                        name=skill['name'],
                        endorsed=skill['endorsed'],
                        created_at=datetime.now()
                    )
                )
            se.add_all(skill_instances)
            se.commit()

    def insert_posts(self, profile_id, posts):
        with Session(self.engine) as se:
            post_instances = []
            for post in posts:
                post_instances.append(
                    LinkedinPost(
                        linkedin_data_id=profile_id,
                        post_id=post['post_id'],
                        content=post['content'],
                        created_at=datetime.now()
                    )
                )
            se.add_all(post_instances)
            se.commit()
