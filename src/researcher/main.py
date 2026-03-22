from researcher.crew import Researcher, extract_clean_context
from researcher.pdf_generator import convert_md_to_pdf
from crewai import Crew, Process


def run():
    inputs = {"topic": "Impact of Ai on the human mind"}

    try:
        r = Researcher()

        # ── Crew 1: Research ──────────────────────────────────
        research_crew = Crew(
            agents=[r.research_agent()],
            tasks=[r.research_task()],
            process=Process.sequential,
            verbose=True,
        )
        raw_output = research_crew.kickoff(inputs=inputs)
        clean_text = extract_clean_context(str(raw_output))

        # ── Crew 2: Report generation ─────────────────────────
        report_crew = Crew(
            agents=[r.generate_report()],
            tasks=[r.generate()],
            process=Process.sequential,
            verbose=True,
        )
        report_crew.kickoff(inputs={"topic":"Impact of Ai on the human mindt","clean_text": clean_text,})

        # ── PDF Generation ─────────────────────────
        convert_md_to_pdf("report.md", "report.pdf")

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__ == "__main__":
    run()