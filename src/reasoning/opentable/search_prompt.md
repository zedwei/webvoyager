**Task Objective:** Interact with the website to book a restaurant table according to the user's requested parameters.

**Context**: You are currently on the search result page of opentable.com. Review the search results on the webpage to locate the restaurant matching the user's request and decide the next action based on the following guidelines:

1. If the exact restaurant name provided by the user is found in the search results, click on the restaurant title to navigate to its detailed page.
2. If one or multiple similar restaurant names are found, ask the user to confirm if it's the correct one. Once confirmed, click on the restaurant title to navigate to its detailed page.
3. If the restaurant name provided by the user is not found, check if the search query displayed on the search result page matches the user’s request. If it does not, correct the search query and search again.
4. If the search query matches the user request but no matching restaurant is found in the search results, ask the user to provide a corrected name.

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
