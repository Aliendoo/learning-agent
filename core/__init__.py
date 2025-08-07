"""
Core package for the Learning Agent

This package contains the core workflow orchestration:
- learning_graph: The main LangGraph workflow that coordinates all services
"""

from .learning_graph import build_learning_graph

__all__ = [
    "build_learning_graph"
]