"""Test suite for task_service module.

This module contains comprehensive tests for the Task and TaskService classes,
covering happy paths, edge cases, and error conditions for all methods.
"""

import pytest
from src.task_service import Task, TaskService


# Fixtures

@pytest.fixture
def task_service():
    """Provide a fresh TaskService instance for each test."""
    return TaskService()


@pytest.fixture
def sample_task():
    """Provide a sample Task instance for testing."""
    return Task(1, "Sample Task", "Sample description", "medium")


@pytest.fixture
def populated_service():
    """Provide a TaskService with several pre-created tasks."""
    service = TaskService()
    service.create_task("High priority task", "Important work", "high")
    service.create_task("Medium priority task", "Regular work", "medium")
    service.create_task("Low priority task", "Minor work", "low")
    service.complete_task(1)  # Complete the first task
    return service


# Task class tests

def test_task_initialization_with_all_parameters():
    """Test Task initialization with all parameters provided."""
    task = Task(1, "Test Task", "Test description", "high")
    assert task.task_id == 1
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.priority == "high"
    assert task.completed is False
    assert task.subtasks == []


def test_task_initialization_with_minimal_parameters():
    """Test Task initialization with only required parameters."""
    task = Task(2, "Minimal Task")
    assert task.task_id == 2
    assert task.title == "Minimal Task"
    assert task.description == ""
    assert task.priority == "medium"
    assert task.completed is False
    assert task.subtasks == []


def test_task_initialization_with_string_id():
    """Test Task initialization with string ID (for subtasks)."""
    task = Task("1.1", "Subtask")
    assert task.task_id == "1.1"
    assert task.title == "Subtask"


# TaskService initialization tests

def test_task_service_initialization(task_service):
    """Test TaskService initializes with empty task collection."""
    assert task_service.tasks == {}
    assert task_service._next_id == 1


# create_task tests

def test_create_task_with_all_parameters(task_service):
    """Test creating a task with all parameters specified."""
    task = task_service.create_task("New Task", "Description", "high")
    assert task.task_id == 1
    assert task.title == "New Task"
    assert task.description == "Description"
    assert task.priority == "high"
    assert task.completed is False
    assert 1 in task_service.tasks
    assert task_service._next_id == 2


def test_create_task_with_minimal_parameters(task_service):
    """Test creating a task with only required title parameter."""
    task = task_service.create_task("Simple Task")
    assert task.task_id == 1
    assert task.title == "Simple Task"
    assert task.description == ""
    assert task.priority == "medium"


def test_create_task_strips_whitespace(task_service):
    """Test that create_task strips leading/trailing whitespace from title."""
    task = task_service.create_task("  Whitespace Task  ")
    assert task.title == "Whitespace Task"


def test_create_task_increments_id(task_service):
    """Test that task IDs increment correctly for multiple tasks."""
    task1 = task_service.create_task("Task 1")
    task2 = task_service.create_task("Task 2")
    task3 = task_service.create_task("Task 3")
    assert task1.task_id == 1
    assert task2.task_id == 2
    assert task3.task_id == 3
    assert task_service._next_id == 4


def test_create_task_with_empty_title_raises_error(task_service):
    """Test that creating a task with empty title raises ValueError."""
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        task_service.create_task("")


def test_create_task_with_whitespace_only_title_raises_error(task_service):
    """Test that creating a task with whitespace-only title raises ValueError."""
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        task_service.create_task("   ")


def test_create_task_with_invalid_priority_raises_error(task_service):
    """Test that creating a task with invalid priority raises ValueError."""
    with pytest.raises(ValueError, match="Invalid priority: urgent"):
        task_service.create_task("Task", priority="urgent")


def test_create_task_with_each_valid_priority(task_service):
    """Test creating tasks with each valid priority level."""
    low_task = task_service.create_task("Low", priority="low")
    medium_task = task_service.create_task("Medium", priority="medium")
    high_task = task_service.create_task("High", priority="high")
    assert low_task.priority == "low"
    assert medium_task.priority == "medium"
    assert high_task.priority == "high"


# get_task tests

def test_get_task_returns_correct_task(task_service):
    """Test that get_task returns the correct task by ID."""
    created_task = task_service.create_task("Test Task")
    retrieved_task = task_service.get_task(1)
    assert retrieved_task is created_task
    assert retrieved_task.task_id == 1


def test_get_task_with_nonexistent_id_raises_error(task_service):
    """Test that getting a nonexistent task raises KeyError."""
    with pytest.raises(KeyError, match="Task 999 not found"):
        task_service.get_task(999)


def test_get_task_from_empty_service_raises_error(task_service):
    """Test that getting a task from empty service raises KeyError."""
    with pytest.raises(KeyError, match="Task 1 not found"):
        task_service.get_task(1)


# complete_task tests

def test_complete_task_marks_task_as_completed(task_service):
    """Test that complete_task sets completed status to True."""
    task_service.create_task("Task to complete")
    completed_task = task_service.complete_task(1)
    assert completed_task.completed is True
    assert task_service.tasks[1].completed is True


def test_complete_task_returns_updated_task(task_service):
    """Test that complete_task returns the updated Task object."""
    original_task = task_service.create_task("Task")
    completed_task = task_service.complete_task(1)
    assert completed_task is original_task
    assert completed_task.completed is True


def test_complete_already_completed_task_raises_error(task_service):
    """Test that completing an already completed task raises ValueError."""
    task_service.create_task("Task")
    task_service.complete_task(1)
    with pytest.raises(ValueError, match="Task 1 is already completed"):
        task_service.complete_task(1)


def test_complete_nonexistent_task_raises_error(task_service):
    """Test that completing a nonexistent task raises KeyError."""
    with pytest.raises(KeyError, match="Task 999 not found"):
        task_service.complete_task(999)


# update_priority tests

def test_update_priority_changes_task_priority(task_service):
    """Test that update_priority successfully changes task priority."""
    task_service.create_task("Task", priority="low")
    updated_task = task_service.update_priority(1, "high")
    assert updated_task.priority == "high"
    assert task_service.tasks[1].priority == "high"


def test_update_priority_returns_updated_task(task_service):
    """Test that update_priority returns the updated Task object."""
    original_task = task_service.create_task("Task")
    updated_task = task_service.update_priority(1, "high")
    assert updated_task is original_task


def test_update_priority_to_each_valid_level(task_service):
    """Test updating priority to each valid level."""
    task_service.create_task("Task")
    task_service.update_priority(1, "low")
    assert task_service.tasks[1].priority == "low"
    task_service.update_priority(1, "medium")
    assert task_service.tasks[1].priority == "medium"
    task_service.update_priority(1, "high")
    assert task_service.tasks[1].priority == "high"


def test_update_priority_with_invalid_priority_raises_error(task_service):
    """Test that updating to invalid priority raises ValueError."""
    task_service.create_task("Task")
    with pytest.raises(ValueError, match="Invalid priority: critical"):
        task_service.update_priority(1, "critical")


def test_update_priority_of_nonexistent_task_raises_error(task_service):
    """Test that updating priority of nonexistent task raises KeyError."""
    with pytest.raises(KeyError, match="Task 999 not found"):
        task_service.update_priority(999, "high")


# add_subtask tests

def test_add_subtask_creates_subtask_with_correct_id(task_service):
    """Test that add_subtask creates a subtask with hierarchical ID."""
    task_service.create_task("Parent Task")
    subtask = task_service.add_subtask(1, "Subtask 1")
    assert subtask.task_id == "1.1"
    assert subtask.title == "Subtask 1"


def test_add_subtask_appends_to_parent_subtasks_list(task_service):
    """Test that add_subtask appends subtask to parent's subtasks list."""
    task_service.create_task("Parent Task")
    subtask = task_service.add_subtask(1, "Subtask")
    parent = task_service.get_task(1)
    assert len(parent.subtasks) == 1
    assert parent.subtasks[0] is subtask


def test_add_multiple_subtasks_increments_id(task_service):
    """Test that multiple subtasks get incrementing IDs."""
    task_service.create_task("Parent Task")
    subtask1 = task_service.add_subtask(1, "Subtask 1")
    subtask2 = task_service.add_subtask(1, "Subtask 2")
    subtask3 = task_service.add_subtask(1, "Subtask 3")
    assert subtask1.task_id == "1.1"
    assert subtask2.task_id == "1.2"
    assert subtask3.task_id == "1.3"


def test_add_subtask_strips_whitespace(task_service):
    """Test that add_subtask strips leading/trailing whitespace from title."""
    task_service.create_task("Parent Task")
    subtask = task_service.add_subtask(1, "  Whitespace Subtask  ")
    assert subtask.title == "Whitespace Subtask"


def test_add_subtask_with_empty_title_raises_error(task_service):
    """Test that adding subtask with empty title raises ValueError."""
    task_service.create_task("Parent Task")
    with pytest.raises(ValueError, match="Subtask title cannot be empty"):
        task_service.add_subtask(1, "")


def test_add_subtask_with_whitespace_only_title_raises_error(task_service):
    """Test that adding subtask with whitespace-only title raises ValueError."""
    task_service.create_task("Parent Task")
    with pytest.raises(ValueError, match="Subtask title cannot be empty"):
        task_service.add_subtask(1, "   ")


def test_add_subtask_to_nonexistent_parent_raises_error(task_service):
    """Test that adding subtask to nonexistent parent raises KeyError."""
    with pytest.raises(KeyError, match="Task 999 not found"):
        task_service.add_subtask(999, "Subtask")


# delete_task tests

def test_delete_task_removes_task_from_service(task_service):
    """Test that delete_task removes the task from the service."""
    task_service.create_task("Task to delete")
    assert 1 in task_service.tasks
    task_service.delete_task(1)
    assert 1 not in task_service.tasks


def test_delete_task_with_nonexistent_id_raises_error(task_service):
    """Test that deleting a nonexistent task raises KeyError."""
    with pytest.raises(KeyError, match="Task 999 not found"):
        task_service.delete_task(999)


def test_delete_task_from_empty_service_raises_error(task_service):
    """Test that deleting from empty service raises KeyError."""
    with pytest.raises(KeyError, match="Task 1 not found"):
        task_service.delete_task(1)


def test_delete_multiple_tasks(task_service):
    """Test deleting multiple tasks in sequence."""
    task_service.create_task("Task 1")
    task_service.create_task("Task 2")
    task_service.create_task("Task 3")
    task_service.delete_task(2)
    assert 1 in task_service.tasks
    assert 2 not in task_service.tasks
    assert 3 in task_service.tasks


# list_tasks tests

def test_list_tasks_returns_all_tasks_without_filters(populated_service):
    """Test that list_tasks returns all tasks when no filters applied."""
    tasks = populated_service.list_tasks()
    assert len(tasks) == 3


def test_list_tasks_returns_empty_list_for_empty_service(task_service):
    """Test that list_tasks returns empty list when service has no tasks."""
    tasks = task_service.list_tasks()
    assert tasks == []


def test_list_tasks_filter_by_priority_high(populated_service):
    """Test filtering tasks by high priority."""
    tasks = populated_service.list_tasks(filter_priority="high")
    assert len(tasks) == 1
    assert all(t.priority == "high" for t in tasks)


def test_list_tasks_filter_by_priority_medium(populated_service):
    """Test filtering tasks by medium priority."""
    tasks = populated_service.list_tasks(filter_priority="medium")
    assert len(tasks) == 1
    assert all(t.priority == "medium" for t in tasks)


def test_list_tasks_filter_by_priority_low(populated_service):
    """Test filtering tasks by low priority."""
    tasks = populated_service.list_tasks(filter_priority="low")
    assert len(tasks) == 1
    assert all(t.priority == "low" for t in tasks)


def test_list_tasks_filter_by_completed_true(populated_service):
    """Test filtering tasks by completed status (True)."""
    tasks = populated_service.list_tasks(completed=True)
    assert len(tasks) == 1
    assert all(t.completed is True for t in tasks)


def test_list_tasks_filter_by_completed_false(populated_service):
    """Test filtering tasks by completed status (False)."""
    tasks = populated_service.list_tasks(completed=False)
    assert len(tasks) == 2
    assert all(t.completed is False for t in tasks)


def test_list_tasks_filter_by_priority_and_completed(populated_service):
    """Test filtering tasks by both priority and completion status."""
    tasks = populated_service.list_tasks(filter_priority="high", completed=True)
    assert len(tasks) == 1
    assert tasks[0].priority == "high"
    assert tasks[0].completed is True


def test_list_tasks_filter_returns_empty_when_no_matches(populated_service):
    """Test that filtering returns empty list when no tasks match."""
    tasks = populated_service.list_tasks(filter_priority="high", completed=False)
    assert tasks == []


# get_stats tests

def test_get_stats_returns_correct_structure(task_service):
    """Test that get_stats returns dictionary with correct keys."""
    stats = task_service.get_stats()
    assert "total" in stats
    assert "completed" in stats
    assert "pending" in stats
    assert "by_priority" in stats
    assert "high" in stats["by_priority"]
    assert "medium" in stats["by_priority"]
    assert "low" in stats["by_priority"]


def test_get_stats_for_empty_service(task_service):
    """Test get_stats returns zeros for empty service."""
    stats = task_service.get_stats()
    assert stats["total"] == 0
    assert stats["completed"] == 0
    assert stats["pending"] == 0
    assert stats["by_priority"]["high"] == 0
    assert stats["by_priority"]["medium"] == 0
    assert stats["by_priority"]["low"] == 0


def test_get_stats_with_populated_service(populated_service):
    """Test get_stats returns correct counts for populated service."""
    stats = populated_service.get_stats()
    assert stats["total"] == 3
    assert stats["completed"] == 1
    assert stats["pending"] == 2
    assert stats["by_priority"]["high"] == 1
    assert stats["by_priority"]["medium"] == 1
    assert stats["by_priority"]["low"] == 1


def test_get_stats_after_completing_tasks(task_service):
    """Test get_stats updates correctly after completing tasks."""
    task_service.create_task("Task 1")
    task_service.create_task("Task 2")
    task_service.complete_task(1)
    stats = task_service.get_stats()
    assert stats["total"] == 2
    assert stats["completed"] == 1
    assert stats["pending"] == 1


def test_get_stats_after_deleting_tasks(task_service):
    """Test get_stats updates correctly after deleting tasks."""
    task_service.create_task("Task 1", priority="high")
    task_service.create_task("Task 2", priority="high")
    task_service.delete_task(1)
    stats = task_service.get_stats()
    assert stats["total"] == 1
    assert stats["by_priority"]["high"] == 1


def test_get_stats_priority_distribution(task_service):
    """Test get_stats correctly counts tasks by priority."""
    task_service.create_task("High 1", priority="high")
    task_service.create_task("High 2", priority="high")
    task_service.create_task("Medium 1", priority="medium")
    task_service.create_task("Low 1", priority="low")
    task_service.create_task("Low 2", priority="low")
    task_service.create_task("Low 3", priority="low")
    stats = task_service.get_stats()
    assert stats["by_priority"]["high"] == 2
    assert stats["by_priority"]["medium"] == 1
    assert stats["by_priority"]["low"] == 3

# Made with Bob
