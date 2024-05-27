# org_clock_scraper
Scrape Org mode clock tables and submit to Tempo API.

Example Org mode table:

     #+BEGIN: clocktable :scope subtree :maxlevel 4 :narrow 80!
     #+CAPTION: Clock summary at [2024-05-27 Mon 18:07]
     | Headline                      | Time   |   |      |      |
     |-------------------------------+--------+---+------+------|
     | *Total time*                  | *0:01* |   |      |      |
     |-------------------------------+--------+---+------+------|
     | \_    <2024-05-27 Mon>        |        |   | 0:01 |      |
     | \_      [TEAMOPS-8 NB-T] misc |        |   |      | 0:01 |
     #+END:

Entries take the form `[<Jira ticket> <billable type>]`
