import os
import sys
import pandas as pd
import subprocess
from report_generator import generate_reports

POINTS_PER_PASS = 2

def evaluate_student_code(student_id, student_file):
    print(f"🔍 Evaluating code for {student_id}...")

    # Copy student solution to workspace
    workspace_dir = os.path.join(os.getcwd(), "workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    target_file = os.path.join(workspace_dir, "solution.py")
    os.system(f"cp {student_file} {target_file}")

    # Clear previous report
    report_path = os.path.join(workspace_dir, "report.txt")
    if os.path.exists(report_path):
        os.remove(report_path)

    # Run driver.py
    print("🚀 Running driver...")
    subprocess.run(
        [sys.executable, ".core/driver.py"],
        capture_output=True,
        text=True
    )

    # Parse report
    results = {}
    total_score = 0

    if not os.path.exists(report_path):
        print("❌ report.txt not found. Possible crash in student code.")
        return {}, 0

    with open(report_path, "r") as f:
        lines = f.readlines()

    test_index = 1
    for line in lines:
        if "Test Case" in line:
            test_name = f"Test Case {test_index}"
            if "✅" in line:
                results[test_name] = POINTS_PER_PASS
                total_score += POINTS_PER_PASS
            else:
                results[test_name] = 0
            test_index += 1

    print(f"🏁 Total score for {student_id}: {total_score} points")
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

        scp_command = f"scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa ubuntu@{ip}:/home/ubuntu/python-full-student-course-manager/workspace/solution.py {student_dir}/solution.py"
        print(f"🔄 Running SCP: {scp_command}")
        os.system(scp_command)

        student_file = os.path.join(student_dir, "solution.py")
        if not os.path.exists(student_file):
            print(f"❌ solution.py missing for {student_id}. Skipping.")
            continue

        res, total = evaluate_student_code(student_id, student_file)
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
