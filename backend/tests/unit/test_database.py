"""Tests for database configuration."""

import pytest
from sqlmodel import Session, SQLModel, select, create_engine

from app.models.project import Project


# Use in-memory database for tests
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)


@pytest.fixture(autouse=True)
def setup_database():
    """Set up test database before each test."""
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


def get_session():
    """Get a database session for tests."""
    with Session(test_engine) as session:
        yield session


class TestDatabaseConfiguration:
    """Tests for database setup."""

    def test_engine_is_created(self):
        """Engine should be created."""
        assert test_engine is not None

    def test_create_tables(self):
        """Tables should be created without error."""
        # If we get here, tables were created in fixture
        assert True

    def test_get_session_returns_session(self):
        """get_session should yield a session."""
        gen = get_session()
        session = next(gen)
        assert isinstance(session, Session)
        try:
            next(gen)
        except StopIteration:
            pass


class TestProjectModel:
    """Tests for Project model."""

    def test_create_project(self):
        """Should be able to create a project."""
        with Session(test_engine) as session:
            project = Project(
                name="test-project",
                description="A test project",
                github_url="https://github.com/test/test-project",
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            assert project.id is not None

    def test_read_project(self):
        """Should be able to read a project."""
        with Session(test_engine) as session:
            # Create
            project = Project(
                name="read-test-project",
                description="A test project",
            )
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_engine) as session:
            # Read
            result = session.get(Project, project_id)
            assert result is not None
            assert result.name == "read-test-project"

    def test_update_project(self):
        """Should be able to update a project."""
        with Session(test_engine) as session:
            project = Project(name="update-test-project")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_engine) as session:
            project = session.get(Project, project_id)
            project.description = "Updated description"
            session.add(project)
            session.commit()

        with Session(test_engine) as session:
            project = session.get(Project, project_id)
            assert project.description == "Updated description"

    def test_delete_project(self):
        """Should be able to delete a project."""
        with Session(test_engine) as session:
            project = Project(name="delete-test-project")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_engine) as session:
            project = session.get(Project, project_id)
            session.delete(project)
            session.commit()

        with Session(test_engine) as session:
            project = session.get(Project, project_id)
            assert project is None

    def test_list_projects(self):
        """Should be able to list all projects."""
        with Session(test_engine) as session:
            # Create multiple projects
            for i in range(3):
                project = Project(name=f"list-test-project-{i}")
                session.add(project)
            session.commit()

        with Session(test_engine) as session:
            statement = select(Project).where(
                Project.name.like("list-test-project-%")
            )
            results = session.exec(statement).all()
            assert len(results) >= 3
