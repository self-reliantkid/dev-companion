class Task:
    def __init__(self, task_id, title, description="", priority="medium"):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False
        self.subtasks = []


class TaskService:
    def __init__(self):
        self.tasks = {}
        self._next_id = 1

    def create_task(self, title, description="", priority="medium"):
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"Invalid priority: {priority}")
        task = Task(self._next_id, title.strip(), description, priority)
        self.tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id):
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        return self.tasks[task_id]

    def complete_task(self, task_id):
        task = self.get_task(task_id)
        if task.completed:
            raise ValueError(f"Task {task_id} is already completed")
        task.completed = True
        return task

    def update_priority(self, task_id, new_priority):
        if new_priority not in ("low", "medium", "high"):
            raise ValueError(f"Invalid priority: {new_priority}")
        task = self.get_task(task_id)
        task.priority = new_priority
        return task

    def add_subtask(self, parent_id, title):
        parent = self.get_task(parent_id)
        if not title or not title.strip():
            raise ValueError("Subtask title cannot be empty")
        subtask = Task(f"{parent_id}.{len(parent.subtasks) + 1}", title.strip())
        parent.subtasks.append(subtask)
        return subtask

    def delete_task(self, task_id):
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        del self.tasks[task_id]

    def list_tasks(self, filter_priority=None, completed=None):
        results = list(self.tasks.values())
        if filter_priority:
            results = [t for t in results if t.priority == filter_priority]
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        return results

    def get_stats(self):
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