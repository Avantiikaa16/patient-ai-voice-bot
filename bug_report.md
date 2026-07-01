# Bug Report — Pretty Good AI Voice Agent

Total bugs found: **46**  (High: 9, Medium: 23, Low: 14)

---

## High Severity

### H1: Inconsistent Information Request

- **Severity**: high
- **Scenario**: medication_refill
- **Transcript**: `20260630_174951_medication_refill.json`
- **Approx turn**: Turn 5-14

**What happened:** The agent repeatedly asked the patient to spell out their first and last name, despite already confirming the information multiple times.

**What should have happened:** The agent should have only requested the information once and then proceeded with the medication refill process.

---

### H2: Abrupt Call Termination

- **Severity**: high
- **Scenario**: medication_refill
- **Transcript**: `20260630_174951_medication_refill.json`
- **Approx turn**: Turn 19

**What happened:** The agent suddenly terminated the call without resolving the patient's issue or providing a clear explanation.

**What should have happened:** The agent should have either resolved the patient's issue, transferred the call to a representative, or provided a clear explanation for the termination of the call.

---

### H3: Incorrect Focus on Confirmation

- **Severity**: high
- **Scenario**: reschedule_appointment
- **Transcript**: `20260630_175509_reschedule_appointment.json`
- **Approx turn**: Turn 5 and Turn 7

**What happened:** The agent repeated confirmation of the patient's name and date of birth multiple times and also confirmed the phone number, which was not provided by the patient, instead of proceeding with the rescheduling request.

**What should have happened:** After confirming the patient's name and date of birth, the agent should have moved on to assist with the rescheduling request, providing available time slots for the patient to choose from.

---

### H4: Failed to Process Patient Information

- **Severity**: high
- **Scenario**: insurance_question
- **Transcript**: `20260630_180200_insurance_question.json`
- **Approx turn**: Turn 5

**What happened:** The agent asked for the patient's date of birth again, despite the patient already providing it in Turn 4.

**What should have happened:** The agent should have acknowledged and processed the patient's date of birth provided in Turn 4, instead of asking for it again.

---

### H5: Repeating Unnecessary Prompts

- **Severity**: high
- **Scenario**: urgent_symptom
- **Transcript**: `20260630_180859_urgent_symptom.json`
- **Approx turn**: Turn 5

**What happened:** The agent asked for the patient's date of birth again despite the patient already providing it in the previous turn.

**What should have happened:** The agent should have acknowledged the patient's response and proceeded with the conversation, addressing the patient's concern about the headache.

---

### H6: Failure to Address Medical Concern

- **Severity**: high
- **Scenario**: urgent_symptom
- **Transcript**: `20260630_180859_urgent_symptom.json`
- **Approx turn**: Turns 6-12

**What happened:** The agent failed to adequately address the patient's concern about the severe headache, not providing any medical guidance or scheduling an appointment.

**What should have happened:** The agent should have either provided some initial guidance based on the symptoms described or promptly scheduled an appointment for the patient to see a doctor, given the severity and duration of the headache.

---

### H7: Failed to Handle Weekend Appointment Request

- **Severity**: high
- **Scenario**: weekend_scheduling_edge_case
- **Transcript**: `20260630_181926_weekend_scheduling_edge_case.json`
- **Approx turn**: Turn 6

**What happened:** The agent did not inform the patient that the office is likely closed on Sundays and instead transferred the call without addressing the issue

**What should have happened:** The agent should have politely informed the patient that the office is closed on Sundays and offered alternative dates for the appointment

---

### H8: Abrupt Transfer and Disconnection

- **Severity**: high
- **Scenario**: weekend_scheduling_edge_case
- **Transcript**: `20260630_181926_weekend_scheduling_edge_case.json`
- **Approx turn**: Turn 7-9

**What happened:** The agent transferred the call and then abruptly ended the call with a 'goodbye' message without connecting the patient to a representative

**What should have happened:** The agent should have successfully transferred the call to a patient support team representative and ensured a smooth handover

---

### H9: Incorrect Call Transfer

- **Severity**: high
- **Scenario**: cost_and_billing_question
- **Transcript**: `20260630_182653_cost_and_billing_question.json`
- **Approx turn**: Turn 5

**What happened:** The agent responded with 'Hello. You've reached the Pretty Good AI test line. Goodbye' instead of transferring the patient to the clinic support team as requested.

**What should have happened:** The agent should have successfully transferred the patient to the clinic support team or provided an alternative solution, such as offering to take a message or scheduling a callback.

---

## Medium Severity

### M1: Incorrect Assumption of Patient Profile

- **Severity**: medium
- **Scenario**: routine_checkup
- **Transcript**: `20260630_174448_routine_checkup.json`
- **Approx turn**: Turn 3

**What happened:** The agent assumed the patient was not in the system and requested to create a demo patient profile despite the patient already providing their name and stating they are an existing patient.

**What should have happened:** The agent should have attempted to locate the patient's existing profile in the system before creating a new one.

---

### M2: Failure to Initially Understand Patient Request

- **Severity**: medium
- **Scenario**: routine_checkup
- **Transcript**: `20260630_174448_routine_checkup.json`
- **Approx turn**: Turn 3

**What happened:** The agent did not initially understand that the patient wanted to schedule an appointment as an existing patient and instead focused on creating a demo patient profile.

**What should have happened:** The agent should have prioritized scheduling the appointment and attempted to locate the patient's existing profile.

---

### M3: Cutting Off Patient Mid-Sentence

- **Severity**: medium
- **Scenario**: routine_checkup
- **Transcript**: `20260630_174448_routine_checkup.json`
- **Approx turn**: Turn 9-11

**What happened:** The agent cut off the patient mid-sentence and then asked the patient to wait, causing confusion.

**What should have happened:** The agent should have allowed the patient to finish speaking before responding.

---

### M4: Excessive Confirmation

- **Severity**: medium
- **Scenario**: medication_refill
- **Transcript**: `20260630_174951_medication_refill.json`
- **Approx turn**: Turn 9-16

**What happened:** The agent asked the patient to confirm their phone number and date of birth multiple times, which was unnecessary and caused frustration.

**What should have happened:** The agent should have confirmed the information only once and then moved forward with the refill process.

---

### M5: Repeating the Same Phrase

- **Severity**: medium
- **Scenario**: medication_refill
- **Transcript**: `20260630_174951_medication_refill.json`
- **Approx turn**: Turn 15

**What happened:** The agent repeated the same phrase ('I have your phone number as... And your date of birth as... Is that correct?') twice in a row.

**What should have happened:** The agent should have only asked for confirmation once and then proceeded with the next step in the process.

---

### M6: Repeating the Same Phrase

- **Severity**: medium
- **Scenario**: reschedule_appointment
- **Transcript**: `20260630_175509_reschedule_appointment.json`
- **Approx turn**: Turn 5

**What happened:** The agent repeated the same confirmation phrase twice in a row.

**What should have happened:** The agent should only confirm the patient's information once and then proceed with the next steps.

---

### M7: Not Addressing the Patient's Request

- **Severity**: medium
- **Scenario**: reschedule_appointment
- **Transcript**: `20260630_175509_reschedule_appointment.json`
- **Approx turn**: Turn 7

**What happened:** The agent asked for confirmation of the phone number, which was not relevant to the rescheduling request, instead of addressing the patient's need to find a new time slot.

**What should have happened:** The agent should have focused on providing available time slots for the patient to reschedule the appointment.

---

### M8: Incorrect Office Name

- **Severity**: medium
- **Scenario**: cancel_appointment
- **Transcript**: `20260630_175813_cancel_appointment.json`
- **Approx turn**: Turn 1

**What happened:** The agent mentioned two different names for the office (PivotPoint Orthopaedics and To The Point Orthopedics) causing confusion.

**What should have happened:** The agent should have consistently used the correct office name to avoid confusion.

---

### M9: Incorrect Name Entry

- **Severity**: medium
- **Scenario**: cancel_appointment
- **Transcript**: `20260630_175813_cancel_appointment.json`
- **Approx turn**: Turn 13

**What happened:** The agent incorrectly entered the patient's first name as 'Misha' instead of 'Michael'.

**What should have happened:** The agent should have accurately entered the patient's name as provided.

---

### M10: Inconsistent Progress

- **Severity**: medium
- **Scenario**: cancel_appointment
- **Transcript**: `20260630_175813_cancel_appointment.json`
- **Approx turn**: Turn 15

**What happened:** The agent stated they couldn't cancel the appointment and would have a team follow up, then abruptly ended the call.

**What should have happened:** The agent should have either completed the cancellation or provided a clear explanation and next steps before transferring the call.

---

### M11: Repetitive Confirmation

- **Severity**: medium
- **Scenario**: insurance_question
- **Transcript**: `20260630_180200_insurance_question.json`
- **Approx turn**: Turn 7

**What happened:** The agent repeated the confirmation of the patient's name and date of birth multiple times.

**What should have happened:** The agent should have confirmed the patient's information once and then proceeded to address the patient's question about insurance coverage.

---

### M12: Unnecessary Request for Phone Number

- **Severity**: medium
- **Scenario**: insurance_question
- **Transcript**: `20260630_180200_insurance_question.json`
- **Approx turn**: Turn 9

**What happened:** The agent requested the patient's phone number, which was not necessary to answer the patient's question about insurance coverage.

**What should have happened:** The agent should have focused on answering the patient's question about insurance coverage instead of requesting unnecessary information.

---

### M13: Unnecessary Information Requests

- **Severity**: medium
- **Scenario**: urgent_symptom
- **Transcript**: `20260630_180859_urgent_symptom.json`
- **Approx turn**: Turn 9

**What happened:** The agent requested the patient's phone number, which seemed unnecessary given the context of the conversation and the fact that the patient had already provided their name and date of birth.

**What should have happened:** The agent should have focused on addressing the patient's concern about the headache instead of requesting additional information that didn't seem immediately relevant.

---

### M14: Inconsistent Progression

- **Severity**: medium
- **Scenario**: urgent_symptom
- **Transcript**: `20260630_180859_urgent_symptom.json`
- **Approx turn**: Turn 11

**What happened:** The agent confirmed the patient's phone number and date of birth again, which had already been established earlier in the conversation.

**What should have happened:** The agent should have continued to address the patient's concern about the headache, potentially offering guidance or scheduling an appointment, instead of reconfirming already established information.

---

### M15: Abrupt Transfer

- **Severity**: medium
- **Scenario**: urgent_symptom
- **Transcript**: `20260630_180859_urgent_symptom.json`
- **Approx turn**: Turn 13

**What happened:** The agent abruptly transferred the call to a representative without resolving the patient's concern or providing any explanation for the transfer.

**What should have happened:** The agent should have informed the patient about the reason for the transfer and ensured a smooth handover, potentially briefing the next representative on the patient's concern to avoid repetition.

---

### M16: Repeatedly Asking for Same Information

- **Severity**: medium
- **Scenario**: multiple_requests
- **Transcript**: `20260630_181525_multiple_requests.json`
- **Approx turn**: Turn 3-6

**What happened:** The agent repeatedly asked the patient for their full name and date of birth, despite the patient already providing this information.

**What should have happened:** The agent should have acknowledged and stored the patient's name and date of birth after the first time it was provided, and then proceeded with the request.

---

### M17: Not Addressing Multi-Part Request

- **Severity**: medium
- **Scenario**: multiple_requests
- **Transcript**: `20260630_181525_multiple_requests.json`
- **Approx turn**: Turn 4-11

**What happened:** The patient requested both a medication refill and a follow-up appointment, but the agent did not address the appointment scheduling until the patient prompted again.

**What should have happened:** The agent should have acknowledged and addressed both parts of the patient's request simultaneously, or at least provided a clear plan for how both requests would be handled.

---

### M18: Not Confirming Request Before Escalation

- **Severity**: medium
- **Scenario**: multiple_requests
- **Transcript**: `20260630_181525_multiple_requests.json`
- **Approx turn**: Turn 11-12

**What happened:** The agent did not confirm that the patient's requests (medication refill and appointment scheduling) would be handled by the support team before escalating the call.

**What should have happened:** The agent should have confirmed with the patient that the support team would be able to assist with both requests before transferring the call.

---

### M19: Lack of Clear Explanation for Transfer

- **Severity**: medium
- **Scenario**: weekend_scheduling_edge_case
- **Transcript**: `20260630_181926_weekend_scheduling_edge_case.json`
- **Approx turn**: Turn 7

**What happened:** The agent did not provide a clear explanation for transferring the call, which may have caused confusion for the patient

**What should have happened:** The agent should have explained the reason for the transfer, such as 'I'm going to transfer you to a representative who can assist you with scheduling an appointment'

---

### M20: Lack of Reason for Visit

- **Severity**: medium
- **Scenario**: confused_elderly_caller
- **Transcript**: `20260630_182200_confused_elderly_caller.json`
- **Approx turn**: Turn 2

**What happened:** The agent did not ask for the reason for the visit

**What should have happened:** The agent should have asked for the reason for the visit to ensure the appointment is scheduled with the correct provider and to prioritize urgent cases

---

### M21: Lack of Initial Information Collection

- **Severity**: medium
- **Scenario**: cost_and_billing_question
- **Transcript**: `20260630_182653_cost_and_billing_question.json`
- **Approx turn**: Turn 1

**What happened:** The agent did not collect the patient's name and instead made an incorrect assumption about the patient's identity.

**What should have happened:** The agent should have asked for and collected the patient's name and other relevant information, such as date of birth, at the beginning of the call.

---

### M22: Failed to Collect Required Information

- **Severity**: medium
- **Scenario**: office_hours_and_location
- **Transcript**: `20260630_192450_office_hours_and_location.json`
- **Approx turn**: Turn 2

**What happened:** The agent did not collect the patient's date of birth or reason for the potential visit.

**What should have happened:** The agent should have asked for the patient's date of birth and reason for considering becoming a new patient to better assist and prepare for a potential appointment.

---

### M23: Initial Greeting Repetition

- **Severity**: medium
- **Scenario**: new_patient
- **Transcript**: `20260630_223922_new_patient.json`
- **Approx turn**: Turn 1

**What happened:** The agent repeated the greeting and introduction to the clinic.

**What should have happened:** The agent should have provided a single, clear greeting and introduction to avoid confusion and efficiently start the conversation.

---

## Low Severity

### L1: Providing Unrequested Information

- **Severity**: low
- **Scenario**: routine_checkup
- **Transcript**: `20260630_174448_routine_checkup.json`
- **Approx turn**: Turn 5

**What happened:** The agent provided a date of birth for demo purposes without being asked for it and without confirming if it was correct.

**What should have happened:** The agent should have asked the patient to confirm their date of birth instead of providing an unverified one.

---

### L2: Repetition of Information

- **Severity**: low
- **Scenario**: routine_checkup
- **Transcript**: `20260630_174448_routine_checkup.json`
- **Approx turn**: Turn 13

**What happened:** The agent repeated the same appointment information twice.

**What should have happened:** The agent should have provided the information once and then waited for the patient's response.

---

### L3: Redundant Request for Date of Birth

- **Severity**: low
- **Scenario**: cancel_appointment
- **Transcript**: `20260630_175813_cancel_appointment.json`
- **Approx turn**: Turn 7

**What happened:** The agent asked for the patient's date of birth again after it was already provided.

**What should have happened:** The agent should have acknowledged the previously provided date of birth and proceeded with the conversation.

---

### L4: Initial Greeting Issue

- **Severity**: low
- **Scenario**: insurance_question
- **Transcript**: `20260630_180200_insurance_question.json`
- **Approx turn**: Turn 1

**What happened:** The agent's initial greeting was unclear and mentioned 'Or Pretty Good AI', which may cause confusion.

**What should have happened:** The agent should have provided a clear and concise greeting, introducing the medical office and its purpose.

---

### L5: Abrupt Transfer

- **Severity**: low
- **Scenario**: insurance_question
- **Transcript**: `20260630_180200_insurance_question.json`
- **Approx turn**: Turn 11

**What happened:** The agent transferred the patient to a representative without providing a clear explanation or introduction.

**What should have happened:** The agent should have provided a clear explanation for the transfer and introduced the patient to the representative, ensuring a smooth transition.

---

### L6: Unclear Escalation Process

- **Severity**: low
- **Scenario**: multiple_requests
- **Transcript**: `20260630_181525_multiple_requests.json`
- **Approx turn**: Turn 11

**What happened:** The agent stated they couldn't proceed further and offered to connect the patient to the patient support team, but didn't provide a clear reason for the escalation.

**What should have happened:** The agent should have provided a clear explanation for why they were unable to assist the patient and what the patient could expect from the support team.

---

### L7: Redundant Confirmation

- **Severity**: low
- **Scenario**: weekend_scheduling_edge_case
- **Transcript**: `20260630_181926_weekend_scheduling_edge_case.json`
- **Approx turn**: Turn 5

**What happened:** The agent asked the patient to confirm their name and date of birth, and then also asked them to spell their last name, which may be unnecessary

**What should have happened:** The agent could have confirmed the patient's information in a more efficient manner, such as only asking for the last name spelling if necessary

---

### L8: Informal Greeting

- **Severity**: low
- **Scenario**: confused_elderly_caller
- **Transcript**: `20260630_182200_confused_elderly_caller.json`
- **Approx turn**: Turn 15

**What happened:** The agent used an informal greeting ('Thanks for letting me know, buddy')

**What should have happened:** The agent should have used a more formal and professional greeting, such as 'Thank you, Betty' to maintain a professional tone throughout the conversation

---

### L9: Informal Greeting

- **Severity**: low
- **Scenario**: confused_elderly_caller
- **Transcript**: `20260630_182200_confused_elderly_caller.json`
- **Approx turn**: Turn 16

**What happened:** The agent was referred to as 'sweetie', which may indicate the patient is being overly familiar, but the agent did not correct this

**What should have happened:** The agent should have maintained a professional tone and avoided encouraging overly familiar language

---

### L10: Repeated Holds

- **Severity**: low
- **Scenario**: confused_elderly_caller
- **Transcript**: `20260630_182200_confused_elderly_caller.json`
- **Approx turn**: Multiple turns

**What happened:** The agent put the patient on hold multiple times, which may cause frustration

**What should have happened:** The agent should have tried to minimize the number of holds or provided more information to the patient while on hold

---

### L11: Initial Greeting Repetition

- **Severity**: low
- **Scenario**: cost_and_billing_question
- **Transcript**: `20260630_182653_cost_and_billing_question.json`
- **Approx turn**: Turn 1

**What happened:** The agent repeated the greeting and introduction to the medical office.

**What should have happened:** The agent should have provided a single, clear greeting and introduction to the medical office.

---

### L12: Initial Greeting Issue

- **Severity**: low
- **Scenario**: office_hours_and_location
- **Transcript**: `20260630_192450_office_hours_and_location.json`
- **Approx turn**: Turn 1

**What happened:** The agent assumed the caller's name was Sarah without confirmation and repeated the greeting.

**What should have happened:** The agent should have asked for the caller's name without assuming it, ensuring a more personalized and accurate greeting.

---

### L13: Repetitive Response

- **Severity**: low
- **Scenario**: new_patient
- **Transcript**: `20260630_223922_new_patient.json`
- **Approx turn**: Turn 3

**What happened:** The agent repeated similar information about the clinic's focus on orthopedic care multiple times in the same response.

**What should have happened:** The agent should have provided a concise and clear response without repetition, addressing the patient's question directly and efficiently.

---

### L14: Repetitive Response Again

- **Severity**: low
- **Scenario**: new_patient
- **Transcript**: `20260630_223922_new_patient.json`
- **Approx turn**: Turn 5

**What happened:** The agent again repeated similar information about not being able to recommend specific primary care doctors and suggesting alternatives, in a nearly identical manner.

**What should have happened:** The agent should have provided a varied response or acknowledged the repetition to show understanding and adaptability in the conversation.

---

