import argparse
import subprocess
import sys
from src.task_service import TaskService


def run_tests():
    print("\n Running tests...\n")
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short"],
        capture_output=False
    )
    return result.returncode


def show_sync_instructions():
    print("\n To run /sync, open Bob IDE and type:")
    print("   /sync src/task_service.py\n")


def show_gendoc_instructions():
    print("\n To run /gendoc, open Bob IDE and type:")
    print("   /gendoc src/task_service.py\n")


def show_gentest_instructions():
    print("\n To run /gentest, open Bob IDE and type:")
    print("   /gentest src/task_service.py\n")


def demo():
    print("\n========================================")
    print("   dev-companion · Demo Mode")
    print("========================================")
    print("\nThis tool uses IBM Bob to automatically:")
    print("  /gendoc  — generate documentation")
    print("  /gentest — generate unit tests")
    print("  /sync    — detect stale docs and tests")
    print("\nTarget file: src/task_service.py")
    print("\nCurrent test status:")
    run_tests()


def main():
    parser = argparse.ArgumentParser(
        description="dev-companion — AI-powered docs and test generation with IBM Bob"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("demo", help="Run the full demo")
    subparsers.add_parser("test", help="Run the test suite")
    subparsers.add_parser("gendoc", help="Show gendoc instructions for Bob")
    subparsers.add_parser("gentest", help="Show gentest instructions for Bob")
    subparsers.add_parser("sync", help="Show sync instructions for Bob")

    args = parser.parse_args()

    if args.command == "demo":
        demo()
    elif args.command == "test":
        run_tests()
    elif args.command == "gendoc":
        show_gendoc_instructions()
    elif args.command == "gentest":
        show_gentest_instructions()
    elif args.command == "sync":
        show_sync_instructions()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()