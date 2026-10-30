"""Agent orchestrator: the run state machine, budgets, and stop conditions.

Must not: depend on HTTP, the database driver, or the Docker SDK directly. It
talks to the model, workspace, runner, and evaluator through interfaces so
every transition is testable with fakes.
"""
