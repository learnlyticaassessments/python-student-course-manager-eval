import importlib.util
import datetime
import os

def test_student_code(solution_path):
    # Ensure the directory exists
    report_dir = os.path.join(os.path.dirname(__file__), "..", "workspace")
    os.makedirs(report_dir, exist_ok=True)

    report_path = os.path.join(report_dir, "report.txt")

    # Load the student's solution dynamically
    spec = importlib.util.spec_from_file_location("student_module", solution_path)
    student_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(student_module)

    manager = student_module.StudentCourseManager()
    AlreadyRegisteredException = student_module.AlreadyRegisteredException
    CourseNotFoundException = student_module.CourseNotFoundException

    test_cases = [
        {"desc": "Register John for Math", "func": "register", "input": ("John", "Math"), "expected": "John registered for Math"},
        {"desc": "Drop John from Math", "func": "drop", "input": ("John", "Math"), "expected": "John dropped Math"},
        {"desc": "View John's courses", "func": "view", "input": "John", "expected": []},
        {"desc": "Register John for Math again", "func": "exception_register", "input": ("John", "Math"), "exception": AlreadyRegisteredException},
        {"desc": "Drop Alice from History", "func": "exception_drop", "input": ("Alice", "History"), "exception": CourseNotFoundException}
    ]

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = [f"\n=== Test Run at {timestamp} ==="]

    for i, case in enumerate(test_cases, 1):
        try:
            if case["func"] == "register":
                result = manager.register_course(*case["input"])
            elif case["func"] == "drop":
                result = manager.drop_course(*case["input"])
            elif case["func"] == "view":
                result = manager.view_courses(case["input"])
            elif case["func"] == "exception_register":
                # Ensure the course is already registered before triggering the exception
                manager.register_course(*case["input"])  # First registration
                manager.register_course(*case["input"])  # Second registration to trigger exception
            elif case["func"] == "exception_drop":
                result = manager.drop_course(*case["input"])
            else:
                raise ValueError("Unknown function type")

            if "expected" in case and result == case["expected"]:
                msg = f"✅ Test Case {i} Passed: {case['desc']} | Expected={case['expected']}, Actual={result}"
            elif "exception" in case:
                msg = f"❌ Test Case {i} Failed: {case['desc']} | Expected exception {case['exception'].__name__} not raised"
            else:
                msg = f"❌ Test Case {i} Failed: {case['desc']} | Unexpected output"
        except Exception as e:
            if "exception" in case and isinstance(e, case["exception"]):
                msg = f"✅ Test Case {i} Passed: {case['desc']} | Exception {type(e).__name__} correctly raised"
            else:
                msg = f"❌ Test Case {i} Crashed: {case['desc']} | Error={str(e)}"

        print(msg)
        report_lines.append(msg)

    # Write results
    with open(report_path, "a", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

# Automatically run when this script is executed directly
if __name__ == "__main__":
    solution_file = os.path.join(os.path.dirname(__file__), "..", "student_workspace", "solution.py")
    test_student_code(solution_file)
