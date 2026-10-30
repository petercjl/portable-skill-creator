# Query: Run A Clean Regression

Read [Standard answers and regression](../topics/standard-answer-and-regression.md).

Verify the three gates: an accepted standard answer/artifact exists, the iteration is complete, and the user explicitly requested clean regression. If any gate fails, report `clean-regression-not-run`. Otherwise use one fresh evaluator with only the natural request, representative inputs, normal delivery requirements, and safety boundaries. Report; do not patch or retest.
