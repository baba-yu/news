# Direction



1. Create "News" Section: Gather technology trends including 3 days backward window, searching every `latest` and `newest` information. Pick and include only one link to each article. DO NOT search specified version decided by assumptions from your existing memory. DO make sure if the information is actually latest.

2. Create "Future" Section: Make 3 predictions considering above.

3. Create "Change Log" Section: Compare all them above with just one previous report and note them to this section if you find standing out change(s). This step is only for highlighting changes. A user DOES NOT mean this step is to omit or remove the redundant article(s) from the report.

4. Create "Headlines" Section: Summarize all topics above up into 5 bullets.

5. Then, finarize report to translate them to Japanese. The report should be ordered by "Headlines", "Future", "Change Log" and "News".

6. Do "Post-Write Structural Verification Loop".

7. Append cited URLs to references.txt.

8. Save the report as "{current_folder}/report/news-yyyymmdd.md".



IMORTANT: The websites listed in references.txt must not be used as references. Any match with this list indicates a duplicated finding rather than a news source.



## Post-Write Structural Verification Loop



* First pass: complete steps 1 to 5 in Direction.

* Verify: check each claim against its structural position. Structure carries meaning. For a path like News > ## Heading1 > ### Heading2 > body, the claim is the body AND Heading2 AND Heading1 AND News — all conjunctively. Verify that compound claim, not just the body text.

* Keep or relocate: true claims stay in place. False claims are moved to the correct path (or dropped) based on what the verification turned up.

* Loop until no false claims remain. Do not note logs about this loop to the report.



## Must include these topics



* LLM Workflow

   * subtopics

      * OpenClaw, NemoClaw, Hermes Agents, etc

* Ecosystems like vLLM, SGLang, AWS Bedrock etc

* Local LLM

   * subtopics

      * Qwen, bonsai etc

      * Optimization

* Ecosystems like Ollama, llama.cpp, Foundry Local etc

* AI Security

  * subtopics: solutions

    * Zero-trust based access control for agentic AI

    * Monitor and manage AI agent behavior

* CVE update on 8.0<=score

* Hardware

* Physical AI

* Stock Prices and Corporate Activity

* Meet up event related to AI in Bay Area SV

* Other standing out topics



## Default references but not limited



* https://simonwillison.net/

* https://news.ycombinator.com/

* https://www.reddit.com/