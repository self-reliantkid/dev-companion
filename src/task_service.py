class Task:
    """Represents a single task with metadata and subtask support.
    
    A Task encapsulates all information about a task including its unique
    identifier, title, description, priority level, completion status, and
    any associated subtasks.
    
    Attributes:
        task_id (int or str): Unique identifier for the task.
        title (str): The task's title or name.
        description (str): Detailed description of the task.
        priority (str): Priority level ('low', 'medium', or 'high').
        completed (bool): Whether the task has been completed.
        subtasks (list): List of Task objects representing subtasks.
    """
    
    def __init__(self, task_id, title, description="", priority="medium"):
        """Initialize a new Task instance.
        
        Args:
            task_id (int or str): Unique identifier for the task.
            title (str): The task's title or name.
            description (str, optional): Detailed description. Defaults to "".
            priority (str, optional): Priority level. Defaults to "medium".
        """
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False
        self.subtasks = []


class TaskService:
    """Service for managing tasks with CRUD operations and filtering.
    
    TaskService provides a complete task management system with support for
    creating, reading, updating, and deleting tasks. It also supports priority
    management, subtask creation, filtering, and statistics generation.
    
    Attributes:
        tasks (dict): Dictionary mapping task IDs to Task objects.
        _next_id (int): Counter for generating unique task IDs.
    """
    
    def __init__(self):
        """Initialize a new TaskService instance with an empty task collection."""
        self.tasks = {}
        self._next_id = 1

    # STALE: function signature changed - added due_date and tags parameters but docstring not updated
    def create_task(self, title, description="", priority="medium", due_date=None, tags=None):
        """Create a new task and add it to the service.
        
        Args:
            title (str): The task's title or name.
            description (str, optional): Detailed description. Defaults to "".
            priority (str, optional): Priority level ('low', 'medium', 'high').
                Defaults to "medium".
        
        Returns:
            Task: The newly created Task object.
        
        Raises:
            ValueError: If title is empty or whitespace only.
            ValueError: If priority is not 'low', 'medium', or 'high'.
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"Invalid priority: {priority}")
        task = Task(self._next_id, title.strip(), description, priority)
        self.tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id):
        """Retrieve a task by its ID.
        
        Args:
            task_id (int): The unique identifier of the task to retrieve.
        
        Returns:
            Task: The Task object with the specified ID.
        
        Raises:
            KeyError: If no task exists with the given task_id.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        return self.tasks[task_id]

    def complete_task(self, task_id):
        """Mark a task as completed.
        
        Args:
            task_id (int): The unique identifier of the task to complete.
        
        Returns:
            Task: The updated Task object with completed status set to True.
        
        Raises:
            KeyError: If no task exists with the given task_id.
            ValueError: If the task is already completed.
        """
        task = self.get_task(task_id)
        if task.completed:
            raise ValueError(f"Task {task_id} is already completed")
        task.completed = True
        return task

    def update_priority(self, task_id, new_priority):
        """Update the priority level of a task.
        
        Args:
            task_id (int): The unique identifier of the task to update.
            new_priority (str): New priority level ('low', 'medium', or 'high').
        
        Returns:
            Task: The updated Task object with the new priority.
        
        Raises:
            ValueError: If new_priority is not 'low', 'medium', or 'high'.
            KeyError: If no task exists with the given task_id.
        """
        if new_priority not in ("low", "medium", "high"):
            raise ValueError(f"Invalid priority: {new_priority}")
        task = self.get_task(task_id)
        task.priority = new_priority
        return task

    def add_subtask(self, parent_id, title):
        """Add a subtask to an existing parent task.
        
        Args:
            parent_id (int): The unique identifier of the parent task.
            title (str): The title for the new subtask.
        
        Returns:
            Task: The newly created subtask Task object.
        
        Raises:
            KeyError: If no task exists with the given parent_id.
            ValueError: If title is empty or whitespace only.
        """
        parent = self.get_task(parent_id)
        if not title or not title.strip():
            raise ValueError("Subtask title cannot be empty")
        subtask = Task(f"{parent_id}.{len(parent.subtasks) + 1}", title.strip())
        parent.subtasks.append(subtask)
        return subtask

    def delete_task(self, task_id):
        """Delete a task from the service.
        
        Args:
            task_id (int): The unique identifier of the task to delete.
        
        Raises:
            KeyError: If no task exists with the given task_id.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        del self.tasks[task_id]

    def list_tasks(self, filter_priority=None, completed=None):
        """List all tasks with optional filtering by priority and completion status.
        
        Args:
            filter_priority (str, optional): Filter by priority level
                ('low', 'medium', or 'high'). Defaults to None (no filtering).
            completed (bool, optional): Filter by completion status.
                Defaults to None (no filtering).
        
        Returns:
            list: List of Task objects matching the filter criteria.
        """
        results = list(self.tasks.values())
        if filter_priority:
            results = [t for t in results if t.priority == filter_priority]
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        return results

    def get_stats(self):
        """Generate statistics about all tasks in the service.
        
        Returns:
            dict: Dictionary containing task statistics with keys:
                - total (int): Total number of tasks.
                - completed (int): Number of completed tasks.
                - pending (int): Number of pending tasks.
                - by_priority (dict): Count of tasks by priority level with keys
                  'high', 'medium', and 'low'.
        """
        all_tasks = list(self.tasks.values())
        total = len(all_tasks)
        done = sum(1 for t in all_tasks if t.completed)
        return {
            "total": total,
            "completed": done,
            "pending": total - done,
            "by_priority": {
                "high": sum(1 for t in all_tasks if t.priority == "high"),
                "medium": sum(1 for t in all_tasks if t.priority == "medium"),
                "low": sum(1 for t in all_tasks if t.priority == "low"),
            }
        }