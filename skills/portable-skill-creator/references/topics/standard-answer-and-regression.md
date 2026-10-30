# Standard Answer And Clean Regression

A standard answer is a development baseline approved by the user after a realistic main-conversation run. Approval follows inspection of facts, logic, evidence, artifact quality, and delivery behavior. A Wiki answer, Agent draft, or static validator result is not automatically a standard answer.

Clean regression has three gates:

1. an approved standard answer or artifact exists;
2. the current iteration is complete;
3. the user explicitly requests regression.

Use one fresh evaluator. Give it only the natural user request, representative inputs, ordinary output expectations, and safety boundary. Do not reveal the Skill name/path, native tool route, design conversation, expected answer, suspected gap, scoring rubric, or previous regression.

Compare routing, facts, logic, execution, artifacts, and output contract—not wording. The regression turn ends with evidence, classification, and recommendations. It does not edit the Skill, rescue the evaluator, or launch another regression. Any fix begins only after a new user authorization.
