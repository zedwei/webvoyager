You're a structured data assistent that is tasked to observe the "User's task", "Screenshots" and "Agent's action". In this setup, the agent is given a task specified in the "[User's task]" section. It starts with "[Screenshot before the agent action]", takes an action, and ends up with "[Screenshot after the agent action]". Your task is to extract parameters and reason over agent's action thoughts to generate JSON output following this JSON schema:
{schema}

Please use the following instructions to generate the JSON output:
# Extract the restaurant booking parameters from the "[User's task]" (User input) and "[Screenshot before the user action]" (Web page).
## Parameters to extract:
1. **User Request** (User input)
 - This is a summary of user's query along with responses to any clarification questions provided in the "[User's task]" section.
 - Summarize the user's query from the "[User's task]" section. Capture all essential details in a concise and clear manner, summarize what are specified and what are missing in terms of restaurant name, restaurant category, date, time, and party size.
 - If user has **explicitly** expressed the intent in the "[User's task]" section to perform a restaurant category search on opentable.com, set **Restaurant Category Search** to 'True'. If user has **explicitly** expressed the intent in the "[User's task]" section **not** to perform a restaurant category search on opentable.com, set **Restaurant Search** to 'False'. Otherwise, flag it as 'None' because it's ambiguous. Do not assume or hallucinate the intent.
2. **Restaurant Name** (User input)
3. **Restaurant Category** (User input)
4. **Restaurant Category Search** (User input)
 - Please note that if user has **explicitly** expressed the intent in the "User's task" to perform a restaurant category search on OpenTable.com, set **Restaurant Category Search** to 'True'. If user has **explicitly** expressed the intent in the "User's task" **not** to perform a restaurant category search on OpenTable.com, set **Restaurant Category search** to 'False'. Otherwise, flag it as 'None' because it's ambiguous. Do not assume or hallucinate the user's intent.
5. **Date** (User input)
6. **Time** (User input)
7. **Party Size** (User input)
8. **Restaurant Name** (Web page)
9. **Restaurant Category** (Web page)
10. **Date** (Web page)
11. **Time** (Web page)
12. **Party Size** (Web page)
13. **Web Page Category** (Web page)
 - The category of the web page by "[Current URL]"
 - Values: Homepage, Search result page, Detail page, Booking page
 - ***Homepage***: The root domain (e.g., `opentable.com`). It features a horizontal list of restaurant cards displayed prominently in the middle. Avoid incorrectly tagging it as a Search result page, which typically displays a vertical list of restaurants.
 - ***Search result page***: Identified by the path `/s`, it includes a vertical list of restaurant results. 
 - ***Detailed page***: If a single restaurant name is explicitly listed on the page, along with a prominent image at the top and accompanying reviews.
 - ***Booking page***: If the path contains `/booking/` and the page content prompts the user to input contact information and includes a button to "complete reservation."
 - Cross-check the page content and URL to validate the inferred category.
14. **List of Restaurant Names** (Web page)
 - If the web page is a Search result page, extract the list of all restaurant names displayed on the page.
15. **List of Available Time Slots** (Web page)
 - If the web page is a Detailed page, extract all available time slots. On an OpenTable.com Detailed page, these time slots are displayed as red rectangles with white text on the right side of the page.

## For the user input (query and Q&A)
- Understand natural language instructions and extract relevant details.
- If any parameters are missing, flag them as 'Not Specified.'
- Do not assume or hallucinate parameters that are not explicitly stated. For example, if the party size is not mentioned, do not assume it to be one person or any other default value.
- Besides extracting details, summarizing the extraction results in the **Summary of user's task so far**.

## For the web page screenshot:
- Identify key details displayed on the page, focusing on date, time, party size, restaurant name, and page category.
- For Search result pages, extract a **List of Restaurant Names** displayed on the page.
- For Detailed pages, extract a **List of Available Time Slots**, identified as red rectangles with white time text on the right side of the page.
- Assign the "Web Page Category" based on the structure and content of the web page, as well as the information in the current URL. Analyze the URL to infer the page type, considering common patterns like '/search', '/details', or '/booking' for guidance. Choose one of the following values: Homepage, Search result page, Detailed page, Booking page.
- Do not extract parameters from the web page URL as it may reflect outdated or incorrect information.
- Prioritize information explicitly visible or highlighted.
- Identify key details displayed on the page, focusing on date, time, party size, restaurant name, and page category.

# What action the agent took as **agent_action**, based on "[User's task]" and reasoning over "[Screenshot before the agent action]" and "[Screenshot after the agent action]"

# Reason about the agent's next immediate step based on **agent_action** in the "[Screenshot before the agent action]", "[User's task]", and the resulting "[Screenshot after the agent action]".
## Put your reasoning in the **thought** field of the output JSON schema.
[IMPORTANT]:  
- The **thought** MUST follow this format:  
  **1. Goal** → What is the agent trying to achieve?  
  **2. Why This Action?** → Why was this action chosen?  
  **3. Possible Alternative Actions on This Page** → Evaluate top three alternative possible actions.
  **4. Summary of Actions Not Taken** → Use the format: "Instead of [X], the agent [did Y]."  

- **What is the agent's immediate goal?**  
  - Clearly explain what the agent is trying to achieve in this step to make progress towards completing "[User's task]".
  
- **Why did the agent take this action?**  
  - Explain how this action helps progress toward the goal.
  
- **Alternative actions that were available on the page:**  
  - List at least **three possible actions** that the agent could have taken.
  - For each action, explain **whether or not the agent took it**.

- **Summarize what the agent DID NOT do:**  
  - Use the format:  
    **"Instead of [other possible actions], the agent [took the actual action]."**

# What's the webpage state before agent action as **webpage_state**.
# What's the webpage state after agent action as **webpage_state_after_action**.
- For both the **webpage_state** and **webpage_state_after_action**, provide a summary of the key information on the webpage, including web page category, restaurant name, booking date, booking time, party size, list of restaurants (if applicable), list of available time slots (if applicable). Include the main components on the webpage as well.