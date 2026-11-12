> **Document version:** docs/survey/instrument.en.md v0.1 | 31 Oct 2026 | Author: socio-culture-analyst B (R1d) | Status: draft

# Intercity travel survey: questionnaire (English)

**Designed, not fielded.** This questionnaire has not been shown to any respondent. It is fielded only by a human fielding institution after Tariq's approval, ethics approval and a pilot (`docs/survey/design.md`, section 9). The Arabic version (`instrument.ar.md`) has the same question numbers and the same figures.

*Review note: the Arabic version was written directly in Arabic and must be reviewed by a native speaker before any fielding (checkpoint item for Tariq, A-social-136).*

Notes for the fielding team are in *italics* and are not shown to respondents. Routing is in square brackets.

---

## Section A. Screening

*Show the short introduction: "This survey asks how you travel between cities in Saudi Arabia and how you would choose between ways of travelling. It takes about 20 minutes." Duration to be confirmed by the pilot.*

**A1.** Are you 18 years old or over?
- Yes
- No [end the survey with the thank-you text in Section G]

*18 or over is a consent rule of this study (A-social-121).*

**A2.** Do you usually live in Saudi Arabia?
- Yes
- No [end]

**A3.** In which region do you live?
Riyadh / Makkah / Madinah / Eastern Province / Qassim / Asir / Tabuk / Hail / Northern Borders / Jazan / Najran / Al Bahah / Al Jawf

**A4.** In which governorate do you live? *[list filtered by A3, from `docs/coverage.md`]*

**A5.** Is the place where you live a large city, a town, or a village or rural area?
- Large city
- Town
- Village or rural area

**A6.** In the last 12 months, have you made at least one trip of 150 km or more (one way) to another city or governorate in Saudi Arabia?
- Yes [continue to Section B, then C and D]
- No [continue to Section B, then C1 only, then E and F; skip D]

*150 km one way: A-social-135. A6 = No is kept in the sample: these respondents matter for the equity analysis.*

## Section B. Consent

**B1.** *[Show the consent text from `docs/survey/ethics-consent.md`, section 1 (English) or section 2 (Arabic), in full, before any further question.]*
Do you agree to take part in this survey?
- Yes, I agree [continue]
- No [end with the thank-you text]

## Section C. Your intercity trips

**C1.** In the last 12 months, about how many trips of 150 km or more (one way) to another city did you make? Count each one-way journey as one trip.
- None
- 1–2
- 3–5
- 6–11
- 12 or more

**C2.** In the last 12 months, which of these did you use for such trips? *(Select all that apply.)*
- Car, as the driver
- Car, as a passenger
- Taxi or ride-hailing app
- Intercity coach (bus)
- Train
- Domestic flight
- Other (please state)

**C3.** Please think about your **most recent** trip of 150 km or more to another city.

**C3.1.** Where did the trip start? *(Governorate; default = A4)*

**C3.2.** Where was your destination? *(City or governorate)*

*The fielding team derives the road distance D from C3.1 and C3.2 and applies the pivot rule (design.md, section 3). If D is under 150 km or over 600 km, the nearest band edge is used.*

**C3.3.** How did you mainly travel on that trip? *(Same list as C2; one answer.)*

**C3.4.** What was the main purpose of the trip?
- Travelling to work (a regular commute)
- Business or work trip
- Visiting family or friends
- Umrah or Hajj
- Tourism or leisure
- Study
- Other personal business

**C3.5.** When did you travel?
- A weekday (Sunday to Thursday) *(official working week, S-soc-354, secondary)*
- The weekend (Friday or Saturday)
- During Eid or another public holiday

**C3.6.** Who travelled with you?
- I travelled alone
- With other adults (not family)
- With family members, adults only
- With family members including children

**C3.7.** How many people travelled together in total, including you? *(Number)*

**C3.8.** What luggage did you take?
- None or a small bag only
- A cabin-size bag
- One large suitcase
- More than one large suitcase

**C3.9.** About how long did the trip take, door to door? *(Hours and minutes)*

**C3.10.** About how much did the trip cost you (fuel, tickets, parking, taxis), in SAR? *(Number; "I don't know" allowed)*

**C3.11.** In which month did you travel? *(Month list)*

**C4.** For that trip, which of these could you realistically have used? *(Select all that apply.)*
- A car (own, household or borrowed)
- Intercity coach (bus)
- Train
- Domestic flight

## Section D. Choosing how to travel (choice tasks)

*Only for A6 = Yes. Each respondent is assigned at random to one block (1, 2 or 3) of `docs/survey/choice_sets.csv` and to one season framing, summer or winter, at 50 % each (A-social-128). Within a block, the order of the 9 design tasks is randomised; the dominance task (task 10) is placed at random among them. All times and costs are pivoted by D/400 and rounded (times to 5 min, costs to SAR 5). The flight option is shown only if the respondent's pair has scheduled flights.*

**D0. Introduction shown to the respondent**

> Imagine you are making the same trip again, from **[C3.1]** to **[C3.2]**, in **[July / January]**.
> On the next screens you will see up to four ways of making this trip: your car, a new train service, a domestic flight and an intercity coach. Each screen describes them differently. Please choose the one you would actually use if these were the only options.
> - **Times** are for the whole journey stage described. "Time to reach the station…" includes getting to the station or airport at the start and from it to your destination at the end.
> - **The car cost** is for the whole car (fuel and parking). **Ticket prices** are per person, one way.
> - **"Trips arriving on time"**: when a train or flight is late, it arrives on average 30 minutes late. *(A-mode-013)*
> - **"A train every 30 minutes"** means you can choose a departure about every 30 minutes.
> - There are no right or wrong answers.

**Worked example: block 1, task 1** (from `docs/survey/choice_sets.csv`, shown here at the 400 km reference trip, before pivoting)

**D1.** Which would you choose for this trip?

| | Your own car (or a household car) | Train (new intercity service) | Domestic flight | Intercity coach (bus) |
|---|---|---|---|---|
| Door-to-door driving time | 270 minutes | | | |
| Fuel and parking cost for the car | SAR 120 | | | |
| Time on the train / flight time / time on the coach | | 210 minutes | 85 minutes | 390 minutes |
| Time to reach the station, airport or bus station and from it to your destination | | 20 minutes | 120 minutes (including check-in and security) | 15 minutes |
| Ticket price (one way, per person) | | SAR 180 | SAR 180 | SAR 60 |
| A train / flight / coach every | | 30 minutes | 60 minutes | 240 minutes (4 hours) |
| Trips arriving on time | | 95 % | 80 % | |
| Class | | Economy | | VIP |
| Women-only or family carriage | | Not available | | |
| Prayer area on board or at the stations | | Not available | | |
| Luggage included | | Cabin bag only | Cabin bag + one large suitcase | |
| Shaded or air-conditioned walk and transfer at the stations | | Available | | |
| **I would choose** | ☐ | ☐ | ☐ | ☐ |

*Blank cells: the attribute does not apply to that option and is shown as "–". Coach and car show no on-time share in this design.*

**D2–D10.** The remaining tasks of the assigned block, in the same layout, with the levels from `choice_sets.csv`.

**D11.** *(After the last task.)* How easy was it to make these choices?
- Very easy / Easy / Neither easy nor difficult / Difficult / Very difficult

**D12.** When choosing, did you ignore any of the features? *(Select all that apply.)*
- Travel time / Cost or ticket price / Time to reach the station or airport / How often services run / Trips arriving on time / Class / Women-only or family carriage / Prayer area / Luggage / Shaded or air-conditioned walk / I did not ignore any

## Section E. Your views

*Five-point scale for each statement: Strongly disagree / Disagree / Neither agree nor disagree / Agree / Strongly agree. Statement order randomised. These items test hypotheses (design.md, section 2); they make no claim about Saudi travellers.*

**E1.** In summer I avoid walking outdoors to reach transport, even for a few minutes.

**E2.** A women-only or family section would make me more comfortable travelling by train or coach.

**E3.** Facilities at stations, such as prayer areas, washrooms and waiting areas, matter to me when I choose how to travel.

**E4.** I would rather drive myself than depend on a timetable.

**E5.** I can use time on a train or coach well, for example to work, read or rest.

**E6.** Travelling with large luggage on public transport is difficult.

**E7.** I trust that public transport between cities leaves and arrives on time.

**E8.** The cost of fuel matters when I decide how to travel.

**E9.** I think about the environmental impact of how I travel.

**E10.** For this statement, please choose "Disagree". *(Attention check.)*

## Section F. About you

*These questions are used only to describe the sample and to weight it to official statistics. No name, ID number, phone number or address is asked.*

**F1.** Are you: Male / Female

**F2.** Your age: 18–24 / 25–34 / 35–44 / 45–54 / 55–64 / 65 or over *(A-social-127)*

**F3.** Your nationality: Saudi / Non-Saudi

**F4.** How many people live in your household, including you? *(Number)*

**F5.** How many of them are children under 12? *(Number)*

**F6.** What is your main activity?
- Employed full time
- Employed part time
- Self-employed or business owner
- Student
- Homemaker
- Looking for work
- Retired
- Other

**F7.** Do you hold a valid Saudi driving licence? Yes / No

**F8.** For a trip like the one in C3, is a car available to you?
- Always
- Sometimes
- Never

**F9.** How many cars does your household have? 0 / 1 / 2 / 3 or more

**F10.** In a usual week, on how many days do you work from home? 0 / 1 / 2 / 3 / 4 / 5 or more / Not applicable

**F11.** *(Optional.)* What is your household's total monthly income, in SAR? *(A-social-126)*
- Less than 5,000
- 5,000–9,999
- 10,000–14,999
- 15,000–24,999
- 25,000–39,999
- 40,000 or more
- Prefer not to say

**F12.** Your highest level of education:
- Below secondary
- Secondary
- Diploma
- Bachelor's degree
- Postgraduate

## Section G. Closing

> Thank you for taking part. Your answers are anonymous and will be used only in aggregate, for research on intercity travel. If you have questions about this survey or your data, contact: **[to be filled by the fielding institution]**.
>
> Your random completion code is **[code]**. Keep it if you may want to ask for your answers to be deleted within 30 days (A-social-140).

*Recorded automatically, not asked: interview language (Arabic/English), assigned block, season framing, task order, completion time (for the speeder rule A-social-129), consent timestamp and the random completion code (generated at submission, not derived from any answer). No IP address or device identifier is stored (ethics-consent.md, section 4).*
