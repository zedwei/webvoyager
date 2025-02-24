**Task Objective:** Interact with the website to book a restaurant table according to the user's requested parameters.

**Context:** You are currently on the homepage of opentable.com. 

1. If the restaurant name is not provided in the user request but the restaurant category is provided in the user request, check **Intent to Perform Restaurant Category Search** from **Parameters to Reason About:**:
 1.1 If the value is 'False', prompt the user to provide the restaurant name.
 1.2 If the value is 'True', search for the restaurant in the search box using the **Category of Restaurant** in the search box located in the top-right corner and navigate to the search result page.
 1.3 If the value is 'None', clarify with the user by asking if they want to **provide the restaurant name** or **search the restaurant using the category on opentable.com homepage**.
2. If the restaurant name and category are not provided in the user request, prompt the user to provide it.
3. If the restaurant name is provided, search for the restaurant name in the search box located in the top-right corner and navigate to the search result page.

**Example Scenarios:**

1. **User's Request:** The user wants to book a table on Jan 15 for 2 people.
   - **Action:** Ask the user to input the name of the restaurant for booking.

2. **User's Request:** The user wants to book a table at Wild Ginger Seattle on Jan 15.
   - **Action:** Type "Wild Ginger Seattle" in the search box in the top-right corner and navigate to the search result page.

Please generate the outputs for task 1, task 2, and task 3 **step by step**.

# Task 1: Infer which **single** action "I" should take based on:
1. Observing the mouse location and focus (if available) in the "[Web page before the action]".
2. Comparing the difference between the "[Web page before the action]" and "[Web page after the action]", and the difference between the "[Description of the user request and web page before the action]" and "[Description of the user request and web page after the action]".
3. The inferred action does **NOT** have to be among the "[Top possible actions]".

# Task 2: Generate the thought about the inferred action. It's **important** to explicitly list the actions that "I" should NOT take and the actions that "I" should take.
1. Summarize what the action that "I" should take based on the result of **task 1** and what alternative actions that "I" should NOT take based on comparing with the input from **"[Top possible actions]"**.
2. Explain why "I" should take the inferred action from **task 1** that will help me make a progress towards completing **"[User's request]"**.
3. Organize the thought in a pattern of "This is the page of **[include a summary of the status of the web page before action]**, I should NOT **[include a list of alternative actions among the "[top 3 possible actions]" that do not match the inferred action from task 1]**. Instead, I should **[include a summary of the action that I should actually take]**, which will help me **[include an explain of how this action will help me make progress towards completing "[User's request]" ]**.

# task 3: Generate a list of actions to avoid, that are actions from "[Top possible actions]" which do not match the inferred action from task 1.
