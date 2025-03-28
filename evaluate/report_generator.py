import pandas as pd
import os

def generate_reports(results_dict):
    summary_rows = []

    for student_id, info in results_dict.items():
        row = {
            "Student": info["name"],
            "Email": info["email"],
            "Total Marks": info["total"]
        }
        row.update(info["test_results"])
        summary_rows.append(row)

        report = [f"<h1>Report for {info['name']}</h1>"]
        report.append(f"<p><b>Email:</b> {info['email']}</p>")
        report.append(f"<p><b>Total Score:</b> {info['total']}</p><ul>")
        for tc, marks in info["test_results"].items():
            status = "✅ Passed" if marks > 0 else "❌ Failed"
            report.append(f"<li>{tc}: {status} ({marks} marks)</li>")
        report.append("</ul>")

        os.makedirs("results/reports", exist_ok=True)
        with open(f"results/reports/{student_id}.html", "w") as f:
            f.write("\n".join(report))

    df = pd.DataFrame(summary_rows)
    os.makedirs("results", exist_ok=True)
    df.to_excel("results/summary.xlsx", index=False)
