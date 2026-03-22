import streamlit as st
import os
from researcher.crew import Researcher, extract_clean_context
from researcher.pdf_generator import convert_md_to_pdf
from crewai import Crew, Process

# Constants
REPORT_MD = "report.md"
REPORT_PDF = "report.pdf"

st.set_page_config(page_title="AI Deep Researcher", page_icon="🔍", layout="wide")

st.title("🔍 AI Deep Researcher")
st.markdown("""
Welcome to the **AI Deep Researcher**. Enter a topic below, and our team of AI agents will 
conduct thorough research and generate a professional PDF report for you.
""")

# Input
topic = st.text_input("What would you like me to research?", placeholder="e.g., Future of Quantum Computing")

if st.button("Start Research", type="primary"):
    if not topic:
        st.error("Please enter a topic.")
    else:
        try:
            # ── Clean up previous runs ──────────────────────────
            if os.path.exists(REPORT_MD): os.remove(REPORT_MD)
            if os.path.exists(REPORT_PDF): os.remove(REPORT_PDF)

            with st.status("🚀 Agentic Research in Progress...", expanded=True) as status:
                st.write(f"Conducting research on: **{topic}**")
                
                inputs = {"topic": topic}
                r = Researcher(output_path=REPORT_MD)

                # ── Step 1: Research ──────────────────────────────────
                st.write("🛰️ Researcher agent scouting for information...")
                research_crew = Crew(
                    agents=[r.research_agent()],
                    tasks=[r.research_task()],
                    process=Process.sequential,
                    verbose=True,
                )
                raw_output = research_crew.kickoff(inputs=inputs)
                clean_text = extract_clean_context(raw_output.raw)

                # ── Step 2: Report generation ─────────────────────────
                st.write("📝 Writer agent synthesizing the report...")
                report_crew = Crew(
                    agents=[r.generate_report()],
                    tasks=[r.generate()],
                    process=Process.sequential,
                    verbose=True,
                )
                report_crew.kickoff(inputs={"topic": topic, "clean_text": clean_text})

                # ── Step 3: PDF Generation ─────────────────────────
                st.write("🎨 Converting report to professional PDF...")
                convert_md_to_pdf(REPORT_MD, REPORT_PDF)
                
                status.update(label="✅ Research Complete!", state="complete", expanded=False)

            st.success("The research report has been generated successfully!")

            # Display Markdown
            if os.path.exists(REPORT_MD):
                with st.expander("📄 Preview Report ", expanded=True):
                    with open(REPORT_MD, "r", encoding="utf-8") as f:
                        st.markdown(f.read())

            # Download PDF
            if os.path.exists(REPORT_PDF):
                with open(REPORT_PDF, "rb") as f:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=f,
                        file_name=f"research_report_{topic.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                    )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

st.divider()
