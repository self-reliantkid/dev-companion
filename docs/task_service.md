# Task Service Documentation

## Overview

The Task Service module provides a comprehensive task management system with support for creating, organizing, and tracking tasks. It includes two main classes: `Task` for representing individual tasks with metadata, and `TaskService` for managing collections of tasks with CRUD operations, priority management, subtask support, filtering capabilities, and statistics generation.

---

## Classes

### Task

Represents a single task with metadata and subtask support.

A Task encapsulates all information about a task including its unique identifier, title, description, priority level, completion status, and any associated subtasks.

**Attributes:**
- `task_id` (int or str): Unique identifier for the task.
- `title` (str): The task's title or name.
- `description` (str): Detailed description of the task.
- `priority` (str): Priority level ('low', 'medium', or 'high').
- `completed` (bool): Whether the task has been completed.
- `subtasks` (list): List of Task objects representing subtasks.

#### Methods

##### `__init__(task_id, title, description="", priority="medium")`

Initialize a new Task instance.

**Args:**
- `task_id` (int or str): Unique identifier for the task.
- `title` (str): The task's title or name.
- `description` (str, optional): Detailed description. Defaults to "".
- `priority` (str, optional): Priority level. Defaults to "medium".

---

### TaskService

Service for managing tasks with CRUD operations and filtering.

TaskService provides a complete task management system with support for creating, reading, updating, and deleting tasks. It also supports priority management, subtask creation, filtering, and statistics generation.

**Attributes:**
- `tasks` (dict): Dictionary mapping task IDs to Task objects.
- `_next_id` (int): Counter for generating unique task IDs.

#### Methods

##### `__init__()`

Initialize a new TaskService instance with an empty task collection.

---

##### `create_task(title, description="", priority="medium")`

Create a new task and add it to the service.

**Args:**
- `title` (str): The task's title or name.
- `description` (str, optional): Detailed description. Defaults to "".
- `priority` (str, optional): Priority level ('low', 'medium', 'high'). Defaults to "medium".

**Returns:**
- `Task`: The newly created Task object.

**Raises:**
- `ValueError`: If title is empty or whitespace only.
- `ValueError`: If priority is not 'low', 'medium', or 'high'.

---

##### `get_task(task_id)`

Retrieve a task by its ID.

**Args:**
- `task_id` (int): The unique identifier of the task to retrieve.

**Returns:**
- `Task`: The Task object with the specified ID.

**Raises:**
- `KeyError`: If no task exists with the given task_id.

---

##### `complete_task(task_id)`

Mark a task as completed.

**Args:**
- `task_id` (int): The unique identifier of the task to complete.

**Returns:**
- `Task`: The updated Task object with completed status set to True.

**Raises:**
- `KeyError`: If no task exists with the given task_id.
- `ValueError`: If the task is already completed.

---

##### `update_priority(task_id, new_priority)`

Update the priority level of a task.

**Args:**
- `task_id` (int): The unique identifier of the task to update.
- `new_priority` (str): New priority level ('low', 'medium', or 'high').

**Returns:**
- `Task`: The updated Task object with the new priority.

**Raises:**
- `ValueError`: If new_priority is not 'low', 'medium', or 'high'.
- `KeyError`: If no task exists with the given task_id.

---

##### `add_subtask(parent_id, title)`

Add a subtask to an existing parent task.

**Args:**
- `parent_id` (int): The unique identifier of the parent task.
- `title` (str): The title for the new subtask.

**Returns:**
- `Task`: The newly created subtask Task object.

**Raises:**
- `KeyError`: If no task exists with the given parent_id.
- `ValueError`: If title is empty or whitespace only.

---

##### `delete_task(task_id)`

Delete a task from the service.

**Args:**
- `task_id` (int): The unique identifier of the task to delete.

**Raises:**
- `KeyError`: If no task exists with the given task_id.

---

##### `list_tasks(filter_priority=None, completed=None)`

List all tasks with optional filtering by priority and completion status.

**Args:**
- `filter_priority` (str, optional): Filter by priority level ('low', 'medium', or 'high'). Defaults to None (no filtering).
- `completed` (bool, optional): Filter by completion status. Defaults to None (no filtering).

**Returns:**
- `list`: List of Task objects matching the filter criteria.

---

##### `get_stats()`

Generate statistics about all tasks in the service.

**Returns:**
- `dict`: Dictionary containing task statistics with keys:
  - `total` (int): Total number of tasks.
  - `completed` (int): Number of completed tasks.
  - `pending` (int): Number of pending tasks.
  - `by_priority` (dict): Count of tasks by priority level with keys 'high', 'medium', and 'low'.

---

## Usage Examples

### Basic Task Management

```python
from task_service import TaskService

# Initialize the service
service = TaskService()

# Create tasks
task1 = service.create_task(
    title="Implement user authentication",
    description="Add login and registration functionality",
    priority="high"
)

task2 = service.create_task(
    title="Write unit tests",
    description="Add test coverage for auth module",
    priority="medium"
)

# Retrieve a task
task = service.get_task(1)
print(f"Task: {task.title}, Priority: {task.priority}")

# Complete a task
service.complete_task(1)

# Update task priority
service.update_priority(2, "high")
```

### Working with Subtasks

```python
# Add subtasks to a parent task
subtask1 = service.add_subtask(1, "Design login form")
subtask2 = service.add_subtask(1, "Implement password hashing")
subtask3 = service.add_subtask(1, "Add session management")

print(f"Parent task has {len(task1.subtasks)} subtasks")
```

### Filtering and Statistics

```python
# List all high-priority tasks
high_priority_tasks = service.list_tasks(filter_priority="high")
print(f"High priority tasks: {len(high_priority_tasks)}")

# List all pending tasks
pending_tasks = service.list_tasks(completed=False)
print(f"Pending tasks: {len(pending_tasks)}")

# Get task statistics
stats = service.get_stats()
print(f"Total: {stats['total']}, Completed: {stats['completed']}, Pending: {stats['pending']}")
print(f"By priority: High={stats['by_priority']['high']}, Medium={stats['by_priority']['medium']}, Low={stats['by_priority']['low']}")
```

### Error Handling

```python
try:
    # Attempt to create a task with invalid priority
    service.create_task("Invalid task", priority="urgent")
except ValueError as e:
    print(f"Error: {e}")

try:
    # Attempt to retrieve a non-existent task
    task = service.get_task(999)
except KeyError as e:
    print(f"Error: {e}")

try:
    # Attempt to complete an already completed task
    service.complete_task(1)
    service.complete_task(1)  # This will raise ValueError
except ValueError as e:
    print(f"Error: {e}")
```

---

## Notes

- Task IDs are automatically generated and incremented starting from 1.
- Subtask IDs follow the format `{parent_id}.{subtask_number}` (e.g., "1.1", "1.2").
- Valid priority levels are: 'low', 'medium', and 'high'.
- Task titles cannot be empty or contain only whitespace.
- Deleting a parent task does not automatically delete its subtasks from the parent's subtasks list.