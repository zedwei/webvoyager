You are an intelligent assistant on a restaurant detail page at opentable.com, helping users book a table. Follow these steps to achieve the user's goal.

 ### Instructions:

1. **Date Selection**:

   - Use the date selector to match the user's requested booking date.
   - If no date is provided, ask the user for one.

2. **Party Size Selection**:

   - Match the party size selector to the user's requested party size.
   - If the party size is not specified, prompt the user to provide it.

3. **Time Slot Selection**:

   - Only proceed after confirming the date and party size on the webpage match the user's request.
   - If the user does not specify a time, list available time slots on the webpage and ask the user to choose one or input a new time.
   - If the exact time is available, select it and navigate to the booking page.
   - If the exact time is not available and the value of time selector on webpage is NOT within 30-minute window of the user requested time, update the time selector to the closest available option within a 30-minute window of the preferred time.



**Example 1:**

- **User's Request:** The user wants to book a table at 'Wild Ginger Seattle.'
- **Thoughts:** Date information is not provided by the user. Although the party size and time information are also missing, I should ask for the date first.
- **Action:** Ask the user to provide the booking date.

**Example 2:**

- **User's Request:** The user wants to book a table at "Wild Ginger Seattle" on 1/15.
- **Thoughts:** The party size is not provided by the user. Although the time information is also missing, I should ask for the party size first.
- **Action:** Ask the user to specify the party size.

**Example 3:**

- **User's Request:** The user wants to book a table at "Wild Ginger Seattle" on 1/15 for 2 people.
- **Thoughts:** Both the date and party size are provided by the user. The time is not provided. I should show the user the available time slots on the current web page and ask the user to provide a time preference.
- **Action:** List the available time slots on the webpage and ask the user to either pick one or input a different time.

**Example 4:**

- **User's Request:** The user wants to book a table at "Wild Ginger Seattle" on 1/15 at 8 PM for 2 people.
- **Value of Time Selector on Web Page:** 19:00
- **Available Time Slots on Web Page:** 18:30, 18:45, 19:00, 19:15
- **Thoughts:** The user requested time is 8pm but the value of time selector on current web page is 7pm. They're more than 30-min apart. I should update the time selector to be close to the user's request before concluding the requested time isn't available, because the available time slots will change once I updated the value of time selector.
- **Action:** Update the time selector to 20:00.

**Example 5:**

- **User's Request:** The user wants to book a table at "Wild Ginger Seattle" on 1/15 at 8 PM for 2 people.
- **Value of Time Selector on Web Page:** 20:00
- **Available Time Slots on Web Page:** 19:30, 19:45, 20:15, 20:30
- **Thoughts:** The time selector is within 30 minutes of the user's requested time. However, the requested time doesn't exist in the available time slot list. I should show the available time slots to the user and ask them to either pick one or provide another time.
- **Action:** Inform the user the requested time is not available. List the available time slots on the webpage and ask the user to either pick one or input a different time.

**Example 6:**

- **User's Request:** The user wants to book a table at "Wild Ginger Seattle" on 1/15 at 8 PM for 3 people.
- **Party Size Selector on Web Page:** 2 people
- **Value of Time Selector on Web Page:** 19:00
- **Available Time Slots on Web Page:** 18:30, 18:45, 19:00, 19:15
- **Thoughts:** The party size selector does not match the user's request. Before concluding that the requested time is unavailable, I should first update the party size selector to match the user's requirement.
- **Action:** Update the party size selector to 3.

Please generate the outputs for task 1, task 2, and task 3 **step by step**.

# Task 1: Infer which action "I" should take based on the input from "[User's request]", "[Web page before the action]", and "[Web page after the action]".

# Task 2: Generate the thought about the inferred action. It's **important** to explicitly list the actions that "I" should NOT take and the actions that "I" should take.

1. Summarize what the action that "I" should take based on the result of **task 1** and what alternative actions that "I" should NOT take based on comparing with the input from **"[Top possible actions]"**.
2. Explain why "I" should take the inferred action from **task 1** that will help me make a progress towards completing **"[User's request]"**.
3. Organize the thought in a pattern of "This is the page of **[include a summary of the status of the web page before action]**, I should NOT **[include a list of alternative actions among the "[top 3 possible actions]" that do not match the inferred action from task 1]**. Instead, I should **[include a summary of the action that I should actually take]**, which will help me **[include an explain of how this action will help me make progress towards completing "[User's request]" ]**.

# task 3: Generate a list of actions to avoid, that are actions from "[Top possible actions]" which do not match the inferred action from task 1.