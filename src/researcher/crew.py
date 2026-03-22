from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from researcher.tools.custom_tool import MySearchTool
import re


def extract_clean_context(raw_text: str) -> str:
    text = re.sub(r'<[^>]+>', '', raw_text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^\w\s.,;:!?()\-\'\"]', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if len(line) > 20]
    return '\n'.join(lines).strip()


@CrewBase
class Researcher():

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"
    output_path   = "report.md" # Default

    def __init__(self, output_path="report.md"):
        self.output_path = output_path

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            verbose=True,
            tools=[MySearchTool(), SerperDevTool()]
        )

    @agent
    def generate_report(self) -> Agent:
        return Agent(
            config=self.agents_config['generate_report'],
            verbose=True,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def generate(self) -> Task:
        return Task(
            config=self.tasks_config['generate'],
            output_file=self.output_path
        )

    @crew
    def crew(self) -> Crew:              # ✅ just returns a Crew, nothing else
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )