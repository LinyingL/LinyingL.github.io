---
title: "Speaking as Barometer: How Chinese Diplomats' Words Reflect the Sino-American Relationship"
summary: "A data-driven journalism project analyzing 20 years of Chinese Foreign Ministry press conferences using Sentiment Analysis in R."
tags:
- NLP
- Sentiment Analysis
- R
- Political Economy
- China Studies
date: "2023-01-15T00:00:00Z"

# Links
links:
- name: Original Blog
  url: https://pwiweb.uzh.ch/wordpress/blog/2023/08/21/speaking-as-barometer-how-chinese-diplomats-words-reflect-the-sino-american-relationship/
  icon_pack: fas
  icon: globe
- name: R Code
  url: https://github.com/LinyingL/Datenjournalismus/blob/main/DDJ2.R
  icon_pack: fab
  icon: github

image:
  caption: "Word Cloud Analysis"
  focal_point: Smart
---

*Originally published as a featured blog post at IPZ/UZH.*

### Overview
From trade to human rights, the superpowers are battling on almost all topics since Trump. Through **sentimental analysis** of Chinese Foreign Ministry spokespersons‘ responses on U.S. topics from **2002 to 2022**, this project observes the changing dynamics of the world's most important bilateral relations.

### Methodology
- **Dataset**: Ministry of Foreign Affairs Press Conferences Corpus (2002-2022).
- **Tools**: Analyzed in **R** using the `quanteda` and `zoo` packages.
- **Sentiment Scoring**: Used the Bing dictionary (Liu & Hu, 2004) and the formula: $sentiment = log((positive + 0.5)/(negative + 0.5))$.
- **Visualisation**: Interactive plots generated via `Plotly` and Word Clouds for key diplomatic crises.

### Key Findings
1. **The Era of Constructive Cooperation (2002-2016)**: Diplomatic language remained largely positive, peaking during events like the 2008 Beijing Olympics, despite occasional friction over trade and regional security.
2. **The Shift to Strategic Competition (2017-2022)**: A sharp decline in sentiment following the 2018 Trade War and the COVID-19 pandemic.
3. **The "Wolf Warrior" Turn**: Notable shifts in rhetoric style under different spokespersons (e.g., Zhao Lijian), reflecting a more confrontational diplomatic stance.

> "The human language contains personal attitudes and sentiments. In the diplomatic field, these are often suppressed, but press conferences reveal genuine emotions through on-the-spot reactions."

---
*For the full interactive experience and detailed data charts, please visit the original blog post linked above.*
