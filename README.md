# Replication package
For the paper *Trust the AI, Doubt Yourself: The Hidden Effect of Urgency on Self-Confidence in Human-AI Interaction*
---

## About
Studies show that interactions with an AI system fosters trust in human users towards AI. An often overlooked element of such interaction dynamics is the (sense of) urgency when the human user is prompted by an AI agent, e.g., for advice or guidance. In this paper, we show that although the presence of urgency in human-AI interactions does not affect the trust in AI, it may be detrimental to the human user's self-confidence and self-efficacy. In the long run, the loss of confidence may lead to performance loss, suboptimal decisions, human errors, and ultimately, unsustainable AI systems.
Our evidence comes from an experiment with 30 human participants.
Our results indicate that users may feel more confident in their work when they are eased into the human-AI setup rather than exposed to it without preparation. We elaborate on the implications of this finding for software engineers and decision-makers.

## Contents

- `/data`
  - `P1-1-30.xlsx` - Data sheet of 30 participants for Phase 1
  - `P2-1-30.xlsx` - Data sheet of 30 participants for Phase 2
  - `Participants_Scores.csv` - Data sheet of the participant's scores for both phases
- `/scripts` – Analysis scripts for the automated analysis of data
- `/questionnaire` - Full questionnaires used in the study 
- `/output` – Results of the analyses as used in the article  

## How to use

### Install requirements

- Install requirements by executing `pip install -r requirements.txt` from the root folder.

### Run analysis scripts

- Generate results of the analyses by executing `python scripts/script.py` from the root folder.

