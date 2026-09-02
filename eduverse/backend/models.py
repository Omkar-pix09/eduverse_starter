from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="student")  # student | recruiter | tpo
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    github_username = Column(String, nullable=True)
    leetcode_username = Column(String, nullable=True)
    cgpa = Column(Float, nullable=True)
    branch = Column(String, nullable=True)
    grad_year = Column(Integer, nullable=True)
    skills = Column(JSON, nullable=True)          # list of strings
    certifications = Column(JSON, nullable=True)  # list of strings

    user = relationship("User", back_populates="profile")


class GitHubData(Base):
    __tablename__ = "github_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    repo_count = Column(Integer, default=0)
    total_stars = Column(Integer, default=0)
    languages = Column(JSON, nullable=True)
    top_repos = Column(JSON, nullable=True)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())


class ReadinessScore(Base):
    __tablename__ = "readiness_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float)
    skill_gaps = Column(JSON, nullable=True)      # list of missing skills vs target role
    shap_explanation = Column(JSON, nullable=True)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DatasetRecord(Base):
    """Bulk-imported rows from the admin-uploaded dataset (100-3k people).
    Kept separate from Profile so uploaded institutional data never collides
    with individually self-registered users, but both feed the same ML model.
    """
    __tablename__ = "dataset_records"

    id = Column(Integer, primary_key=True, index=True)
    source_batch = Column(String)  # e.g. filename of the uploaded CSV
    cgpa = Column(Float, nullable=True)
    internships = Column(Integer, nullable=True)
    projects_count = Column(Integer, nullable=True)
    certifications_count = Column(Integer, nullable=True)
    dsa_problems_solved = Column(Integer, nullable=True)
    communication_score = Column(Float, nullable=True)
    placed = Column(Integer, nullable=True)  # 1/0 label used for training
    raw_row = Column(JSON, nullable=True)    # full original row, for traceability
    imported_at = Column(DateTime(timezone=True), server_default=func.now())


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_role = Column(String, nullable=True)
    content_json = Column(JSON, nullable=True)   # structured resume sections
    ats_score = Column(Float, nullable=True)
    matched_keywords = Column(JSON, nullable=True)
    missing_keywords = Column(JSON, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
