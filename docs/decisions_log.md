# Decisions Log

I built on dbt v1, which my learning material used and which is still fully supported, and left out orchestration so I could focus on modeling, testing and reconciliation. I generated clean data first, then planted 20 errors with an answer key, and kept all money in integer cents with whole-month, price-snapshot billing so every total is exact and every result can be checked. I added dbt tests while building each model, with known exceptions like unapplied cash set to warn, and chose Streamlit for the dashboard because the tool in the video had changed since it was recorded.
