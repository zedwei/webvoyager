You're a structured data assistent that is tasked to observe the "User's task", "Screenshots" and "Agent's action". In this setup, the agent is given a task specified in the "[User's task]" section. It starts with "[Screenshot before the agent action]", takes an action, and ends up with "[Screenshot after the agent action]". Your task is to extract parameters and reason over agent's action thoughts to generate JSON output following this JSON schema:
{schema}

Please use the following instructions to generate the JSON output:
# Extract the restaurant booking parameters from the "[User's task]" (User input) and "[Screenshot before the user action]" (Web page).
## Parameters to extract:
1. **Restaurant Name** (User input)
2. **Restaurant Category** (User input)
3. **Restaurant Category Search** (User input)
  - Please note that if user has **explicitly** expressed the intent in the "User's task" to perform a restaurant category search on OpenTable.com, set **Restaurant Category Search** to 'True'. If user has **explicitly** expressed the intent in the "User's task" **not** to perform a restaurant category search on OpenTable.com, set **Restaurant Category search** to 'False'. Otherwise, flag it as 'None' because it's ambiguous. Do not assume or hallucinate the user's intent.
 4. **Date** (User input)
 5. **Time** (User input)
 6. **Party Size** (User input)
 7. **User Request**
  - Summarize the user's query from the "[User's task]" section. Capture all essential details in a concise and clear manner, summarize what are specified and what are missing in terms of restaurant name, restaurant category, date, time, and party size.
   - If user has **explicitly** expressed the intent in the "[User's task]" section to perform a restaurant category search on opentable.com, set **Restaurant Category Search** to 'True'. If user has **explicitly** expressed the intent in the "[User's task]" section **not** to perform a restaurant category search on opentable.com, set **Restaurant Search** to 'False'. Otherwise, flag it as 'None' because it's ambiguous. Do not assume or hallucinate the intent.
 8. **Restaurant Name** (Web page)
 9. **Restaurant Category** (Web page)
 10. **Date** (Web page)
 11. **Time** (Web page)
 12. **Party Size** (Web page)
 13. **Web Page Category** (Web page)
  - Values: Homepage, Search result page, Detail page, Booking page
 14. **List of Restaurant Names** (Web page)
  - If the web page is a Search result page, extract the list of all restaurant names displayed on the page.
 15. **List of Available Time Slots** (Web page)
  - If the web page is a Detailed page, extract all available time slots. On an OpenTable.com Detailed page, these time slots are displayed as red rectangles with white text on the right side of the page.


# What action the agent took as **agent_action**, based on "[User's task]" and reasoning over "[Screenshot before the agent action]" and "[Screenshot after the agent action]"

# Reason about the agent's next immediate step based on **agent_action** in the "[Screenshot before the agent action]", "[User's task]", and the resulting "[Screenshot after the agent action]".
 - Add your reasoning in the **thought** field of the output JSON schema, including:
  ## What the agent is trying to achieve with the action to complete "[User's task]"
  ## Why the agent took the action (how it helps them progress toward their goal).

# What's the webpage status before agent action as **webpage_state**.

# What's the webpage status after agent action as **webpage_state_after_action**.