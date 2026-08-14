# Project overview

Campfire combines two local security filters before user prompts are passed to a downstream LLM or agent workflow.

1. The PII detector labels Korean personally identifiable information at token/span level.
2. The injection detector scores whether a user input contains prompt-injection behavior.

The packaged repository keeps experiment logic and published results separate from private raw data and heavyweight model caches.
