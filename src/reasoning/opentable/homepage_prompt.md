**Task Objective:** Interact with the website to book a restaurant table according to the user's requested parameters.

**Context:** You are currently on the homepage of opentable.com. Decide the next action based on the following guidelines:

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





