"""Enrichment for a pre-defined schema."""
import os 
import sys
sys.path.append( os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) )
from memory_agent.graph import graph



__all__ = ["graph"]
