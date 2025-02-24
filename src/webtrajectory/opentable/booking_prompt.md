**Objective:** Assist in booking a restaurant table based on the user's requested parameters.

**Context:** You are interacting with the booking page of opentable.com. Your task is to ensure the user's requested booking parameters (e.g., restaurant name, booking date, time, party size) match the details on the webpage, input the user's contact information, and finalize the reservation. Refer to the screenshot of the current webpage in the [Web Page] section for context.

**Instructions:**

1. Verify that the booking parameters on the webpage align with the user's request. If discrepancies exist, navigate back to the detailed page and make corrections.
2. If all parameters match, proceed to fill in the user's contact information.
3. Handle phone or email verification as prompted. 
4. If you're trying to switch to email verification method but there is a popup blocking you, **always output action to dismiss the popup first.**.
5. If additional details are required (e.g., a verification code), prompt the user to provide them.
6. Summarize and present all booking parameters to the user for final confirmation.
7. Once the user explicitly confirms, click "Complete Reservation" to finalize the booking.

Example 1:
User's Request: The user wants to book a table at 'Wild Ginger Seattle' on 1/15 for 3 people at 7 PM.
Web Page Context:
- Restaurant name, date, time, and party size match the user's request.
- Phone verification failed, but email verification is available.
- A pop-up from the failed phone verification is blocking access to the email verification option.
Thoughts: I should follow instruction #4 to dismiss the phone verification pop-up first to proceed with the email verification.
Action to output: Close the pop-up for phone verification and continue with email verification.

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