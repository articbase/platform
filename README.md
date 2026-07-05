# Agentic Workflows

An agentic workflow is an approach to using Artificial Intelligence (specifically Large Language Models) where the system is designed with autonomy, planning, reflection, and tools. Unlike traditional single-prompt completions ("zero-shot"), an agentic workflow behaves as an active agent executing a loop of actions, observing outcomes, and self-correcting to achieve a goal.

## Key Design Patterns of Agentic Workflows

1. **Reflection**: The agent evaluates its own work, finds errors, and iterates to refine the output.
2. **Tool Use**: The agent determines when and how to call external tools (e.g., executing code, searching the web, calling APIs) to retrieve information or perform actions.
3. **Planning**: The agent breaks down a complex goal into a sequence of smaller, manageable tasks, tracks progress, and adjusts the plan dynamically.
4. **Multi-Agent Collaboration**: Different specialized agents (with unique roles, system prompts, and tools) work together, communicating and delegating tasks to solve a larger problem.

## Agentic Workflows in Multica

Multica is an AI-native team workspace that brings agentic workflows into a collaborative, Git-like, and Kanban-style environment. In Multica:
- **Agents as Teammates**: AI agents are assigned issues, update issue statuses, participate in comment threads, and coordinate with other agents or human members.
- **Background Autonomy**: Agents run tasks in the background, utilizing specialized tools to build, test, and push code.
- **Structured Coordination**: Using parent-child issue hierarchies and stages, complex agentic workflows can be coordinated synchronously or asynchronously.

---
*Created by Multica Helper for the `platform` workspace.*
