**Task Objective:** Interact with the website to book a restaurant table according to the user's requested parameters.

**Context**: You are currently on the search result page of opentable.com. Review the search results on the webpage to locate the restaurant matching the user's request and decide the next action based on the following guidelines:

1. If the exact restaurant name provided by the user is found in the search results, click on the restaurant title to navigate to its detailed page.
2. If one or multiple similar restaurant names are found, ask the user to confirm if it's the correct one. Once confirmed, click on the restaurant title to navigate to its detailed page.
3. If the restaurant name provided by the user is not found, check if the search query displayed on the search result page matches the user’s request. If it does not, correct the search query and search again.
4. If the search query matches the user request but no matching restaurant is found in the search results, ask the user to provide a corrected name.
5. Never try to proceed with booking directly on this page.

**Example Scenarios:**

**Example 1:** 

**User's Request:** The user wants to book a table at 'Wild Ginger Seattle' for tonight, December 31, 2025.

**List of restaurant names on the search result page:** ['Wild Ginger McKenzie- South Lake Union', 'Wild Ginger Downtown Seattle', 'Wild Ginger - Bellevue']

**Action:** Click on the title of "Wild Ginger Downtown Seattle."



**Example 2:**

**User's Request:** The user wants to book a table at 'Wild Ginger' for tonight, December 31, 2025.

**List of restaurant names on the search result page:** ['Wild Ginger McKenzie- South Lake Union', 'Wild Ginger - Bellevue']

**Action:** Ask the user if the requested restaurant is 'Wild Ginger McKenzie- South Lake Union' or 'Wild Ginger - Bellevue.'



**Example 3:**

**User's Request:** The user wants to book a table at 'El Gaucho Bellevue' for tonight, December 31, 2025.

**List of restaurant names on the search result page:** ['Wild Ginger McKenzie- South Lake Union', 'Wild Ginger - Bellevue']

**Action:** Ask the user to correct the restaurant name because the provided name cannot be found.

Please generate the outputs for task 1, task 2, and task 3 **step by step**:

# Task 1: Infer which action "I" should take based on the input from "[User's request]", "[Web page before the action]", and "[Web page after the action]". The actions may NOT be included in the "[Top possible actions]".

# Task 2: Generate the thought about the inferred action. It's **important** to explicitly list the actions that "I" should NOT take and the actions that "I" should take.

1. Summarize what the action that "I" should take based on the result of **task 1** and what alternative actions that "I" should NOT take based on comparing with the input from **"[Top possible actions]"**.
2. Explain why "I" should take the inferred action from **task 1** that will help me make a progress towards completing **"[User's request]"**.
3. Organize the thought in a pattern of "This is the page of **[include a summary of the status of the web page before action]**, I should NOT **[include a list of alternative actions among the "[top 3 possible actions]" that do not match the inferred action from task 1]**. Instead, I should **[include a summary of the action that I should actually take]**, which will help me **[include an explain of how this action will help me make progress towards completing "[User's request]" ]**.

# task 3: Generate a list of actions to avoid, that are actions from "[Top possible actions]" which do not match the inferred action from task 1.
