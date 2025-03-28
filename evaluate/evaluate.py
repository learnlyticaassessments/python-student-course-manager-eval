import os
import sys
import pandas as pd
import importlib.util
import subprocess
from report_generator import generate_reports


def load_student_module(student_file):
    """Dynamically load student.py with improved error handling"""
    try:
        # Construct the full path to student.py
        full_path = os.path.abspath(student_file)
        
        # Generate a unique module name to avoid import conflicts
        module_name = f"student_module_{os.path.basename(os.path.dirname(full_path))}"
        
        # Create the module specification
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        
        # Create the module
        student_module = importlib.util.module_from_spec(spec)
        
        # Add the module to sys.modules to make it importable
        sys.modules[module_name] = student_module
        
        # Execute the module
        spec.loader.exec_module(student_module)
        
        return student_module
    except Exception as e:
        print(f"Error importing student module from {student_file}: {e}")
        raise

def evaluate_student_code(student_id, local_path):
    print(f"🔍 Evaluating code for {student_id}...")
    student_file = os.path.join(local_path, "student.py")

    os.environ['CURRENT_STUDENT_DIR'] = local_path

    sys.path.insert(0, local_path)

    # 1. Load student.py FIRST
    try:
        load_student_module(student_file)
    except Exception as e:
        print(f"Error loading student module: {e}")
        return {}, 0
    
    # 2. Run tests using pytest
    print("Running pytest...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "evaluate/test_cases.py", "--tb=short", "-v"],
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
        env=os.environ.copy()  # Pass the modified environment
    )

    print(result)

    # 3. Parse pytest output
    results = {}
    total_score = 0
    from test_cases import test_suite

    seen = set()
    # Parse console output for test results
    for line in result.stdout.split('\n'):
        for tc_id, (_, max_score) in test_suite.items():
            if tc_id in line and tc_id not in seen:
                seen.add(tc_id)
                if "PASSED" in line:
                    results[tc_id] = max_score
                    total_score += max_score
                    print(f"  - {tc_id}: ✅ Passed ({max_score}/{max_score})")
                elif "FAILED" in line:
                    results[tc_id] = 0
                    print(f"  - {tc_id}: ❌ Failed (0/{max_score})")

    # If no results found, consider all tests failed
    if not results:
        for tc_id, (_, max_score) in test_suite.items():
            results[tc_id] = 0
            print(f"  - {tc_id}: ❌ Failed (0/{max_score})")

    # Print total score
    total_possible = sum(m for _, m in test_suite.values())
    print(f"🏁 Total score for {student_id}: {total_score} / {total_possible}")

    # Print error output for debugging
    if result.stderr:
        print("🚨 Pytest Error Output:")
        print(result.stderr)

    return results, total_score

def run_all():
    print("📄 Reading student list from evaluate/students.csv...")
    df = pd.read_csv("evaluate/students.csv")
    results = {}

    for _, row in df.iterrows():
        student_id = row["student_name"].replace(" ", "_")
        ip = row["ip_address"]
        print(f"\n========================================")
        print(f"📥 Pulling code from {student_id} ({ip})")

        student_dir = f"student_repos/{student_id}"
        os.makedirs(student_dir, exist_ok=True)

        scp_command = f"scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa ubuntu@{ip}:/home/ubuntu/python-mini-grocery/student.py {student_dir}/"
        print(f"🔄 Running SCP: {scp_command}")
        os.system(scp_command)

        student_file = os.path.join(student_dir, "student.py")
        if not os.path.exists(student_file):
            print(f"❌ student.py missing for {student_id}. Skipping.")
            continue

        res, total = evaluate_student_code(student_id, student_dir)
        results[student_id] = {
            "name": row["student_name"],
            "email": row["email"],
            "test_results": res,
            "total": total
        }

    print("\n📝 Generating final reports...")
    generate_reports(results)
    print("✅ Evaluation complete. Reports generated.")

if __name__ == "__main__":
    print("🚀 Starting student code evaluation...\n")
    run_all()
