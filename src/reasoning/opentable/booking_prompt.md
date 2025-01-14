**Prompt for GPT LLM Model:**

**Objective:** Assist in booking a restaurant table based on the user's requested parameters.

**Context:** You are interacting with the booking page of opentable.com. Your task is to ensure the user's requested booking parameters (e.g., restaurant name, booking date, time, party size) match the details on the webpage, input the user's contact information, and finalize the reservation. Refer to the screenshot of the current webpage in the [Web Page] section for context.

**Instructions:**

1. Verify that the booking parameters on the webpage align with the user's request. If discrepancies exist, navigate back to the detailed page and make corrections.
2. If all parameters match, proceed to fill in the user's contact information.
3. Handle phone or email verification as prompted. If one verification method fails, attempt the alternative method. Dismiss any error pop-ups before retrying.
4. If additional details are required (e.g., a verification code), prompt the user to provide them.
5. Summarize and present all booking parameters to the user for final confirmation.
6. Once the user explicitly confirms, click "Complete Reservation" to finalize the booking.

Please determine and execute the next action based on these guidelines.

