from llm_adaptive_router import RouteMetadata

from services import conversational, retrieve, run_crag_pipeline, run_research


routes = {
        "conv": RouteMetadata(
            invoker=conversational,
            capabilities=["general knowledge","memory storage"],
            cost=0.002,
            performance_score=0.9,
            example_sentences=["Hi", "How is it going?", "How are you?"],
            # additional_info={"key": "value"},
        ),
        "retrv": RouteMetadata(
            invoker=retrieve,
            capabilities=["retrieval",],
            cost=0.002,
            performance_score=0.9,
            example_sentences=["Look at the db", "Retrieve the document titled 'Project Plan Q4'"],
            # additional_info={"key": "value"},
        ),
        "crag": RouteMetadata(
            invoker=run_crag_pipeline,
            capabilities=["web search",],
            cost=0.002,
            performance_score=0.9,
            example_sentences=["What's the weather forecast for tomorrow in New York City?", 
                               "Who won the Nobel Prize in Literature this year?"],
        ),
        "research": RouteMetadata(
            invoker=run_research,
            capabilities=["research","web search and report"],
            cost=0.002,
            performance_score=0.9,
            example_sentences=["What is the best way to cook a steak?",
                               "What is the best way do algotrade?",
                               "Research the history of the internet.",
                               "Research",
                               "Give me a report"
                               ],
        ),
    }
