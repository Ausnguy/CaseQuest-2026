# Presentation Script

**Deck:** https://claude.ai/artifact/Cc69HRuTETj6Mak1r7Gy2X. The same script is in each slide's speaker notes.

**Running order (7:00):**

| Part | Time |
|---|---:|
| Video | 1:00 |
| Live demo | ~1:00 |
| 10 slides | 5:00 |
| Q&A (separate) | 3:00 |

**Rule:** the slides are just visuals. You tell the story, so say it in your own words. You don't need to read this word for word.

---

## Live demo · WALI (~1:00)

- **Map:** "This is Parvius, the manager's console. Red cages are sites on safety hold. Arroyo is our biggest problem: it's on hold, and only 42% of its spare shelf is stocked."
- **Early warning:** "The system flags a machine that's likely to fail soon and shows the parts the job needs. The planner decides whether to stage a kit, and has to give a reason."
- **Warehouse and dispatch:** "The manager can only send an engineer once every kit is on the shelf. The engineer gets the job on their phone."
- **Safety gate:** "Watch: as a planner, I can't lift this hold. Only the safety supervisor can sign it off, with a witness and evidence."

---

## Slide 1 · The problem · AAYAN (~30 sec)
Lone Mesa lost 6,599 hours to unplanned breakdowns last year. When we broke that time down, one thing jumped out: almost a quarter of it, 24%, was a broken machine just sitting there waiting for a spare part to arrive.

And one site is worse than the rest. Arroyo has 40% of all the parts-waiting time and only 42% of its spare shelf stocked. It's also one of three sites locked by overdue safety actions, the red cages.

So we picked one problem, parts waiting, and one priority site, Arroyo.

## Slide 2 · The data · AUSTIN (~30 sec)
The data we were given was messy. Most of the sensor file was in there twice. Machine IDs were scrambled, some temperatures were in Fahrenheit, and some totals were missing.

We cleaned all of it and logged every change. Where a number was missing, we either rebuilt it with the case's own formula or left it blank. We never guessed.

Then we proved it: 39 automated checks, including that every single outage adds up exactly to the monthly production numbers. One command rebuilds everything from the raw file.

Our limits: the data is synthetic, readings are once a day, and there are only six sites.

## Slide 3 · The finding · AUSTIN (~30 sec)
This is the chart that decided our recommendation. Each dot is a site. Left to right is how full its spare-parts shelf is. Up and down is how often a breakdown had to wait for a part.

They sit almost perfectly on a line. Arroyo's shelf is 58% empty, and 56% of its breakdowns waited. Juniper's shelf is nearly full, and only 10% waited. The correlation is −0.995.

And when a breakdown does wait, it loses 16 to 18 hours, no matter what broke. Spare parts is the only option that fixes this stage, and it helps with every kind of failure. That's why we chose it.

## Slide 4 · How it works · WALI (~30 sec)
Here's what sits behind the demo you just saw. On the left, data the company already has: sensor readings, work orders and the safety register. No new systems.

In the middle is Parvius. It cleans and checks the data, flags machines likely to fail, tracks the parts warehouse, and holds any site that isn't safe.

On the right, and this is the important part, people make every decision. The planner stages the parts, the safety supervisor signs off, and the manager sends the engineer. The system won't send anyone without the right parts, and every decision is logged. The failure model only advises, and we don't count any savings from it.

## Slide 5 · The logic · AAYAN (~35 sec)
We want you to be able to trace every number we show, so here's the chain.

What we saw in the data: 24% of downtime is waiting for parts. What the case says: a spare-parts program cuts that wait by about 60%, with a range of 35 to 75. That number comes straight from the case's Solutions sheet, not from us.

So we stock spares, and we get about 968 hours of downtime back every year. That's 666 in the first year while it rolls out.

Just as important is what we did NOT claim. We claim no injury prevention, no repair-cost savings, and no hours from sensors or AI. Everything else is recorded data or the case's own numbers.

## Slide 6 · The rollout · SIDRA (~30 sec)
Here's the twelve-month plan. Month zero, the site safety supervisors start closing the overdue safety actions, the most serious ones first.

Month one, we pilot at Canyon, a site that isn't on hold. The planner and storekeeper audit the shelf and stock the critical kits. Month two, Cedar and Juniper. Month four, Arroyo, our biggest win, but only once its safety actions are verified closed. Then Mesa and Prairie.

Training is short, for planners and storekeepers. We judge the pilot on how full the spare shelf gets. If Canyon reaches 90% by month three, we expand. If it doesn't, we revise. Any safety bypass, and we stop.

## Slide 7 · The cost · NICK (~30 sec)
We're recommending one improvement: a critical spare-parts program at all six sites.

The total to start is $227,500. That's $168,000 for the spare parts program and $59,500 to clear the overdue safety actions, which the company needs to do anyway. $33,000 of that safety work is what unlocks the three blocked sites. After that, it runs at $19,500 a year.

It fits inside every site's existing staff hours. Even Arroyo, with only two technicians, uses 44 of its 120 available hours. And based on the case's own numbers, it gets back about 968 hours of downtime a year. All costs come straight from the case data. We didn't invent any prices.

## Slide 8 · The return · NICK (~30 sec)
So what does it earn? This line is the running total of what the program brings back, minus what it costs.

It dips a little in the first few months while we stock the sites. Then it crosses zero around month eight, and it keeps climbing to about $1.98 million by year three. That's roughly eight times what it costs.

We stress-tested it. Even if everything goes wrong at once, meaning a smaller effect, slow safety sign-off and oil near $50 a barrel, it still pays for itself by month sixteen.

The biggest lever is how fast the safety actions get closed, which is exactly why safety comes first. One note: these are modeled margins from the case formula, not booked cash.

## Slide 9 · The case for yes · AAYAN (~20 sec)
So why say yes? Three reasons.

One: it goes after the biggest delay we can actually fix. Waiting for parts happens at every site and with every kind of failure.

Two: it's fast. One month to start, nothing else needs to be installed first, and it pays for itself in about eight months.

Three: it's safe by design. Safety locks come first, and people make every decision.

Our ask is simple: approve $227,500 to start the safety sprint and the Canyon pilot next month.

## Slide 10 · Safety · SIDRA (~25 sec)
Last, and most important: safety is never skipped.

**No override.** A site with an open severity-five safety action can't start, there's no button to bypass that, and only the safety supervisor can sign off a closure.

**People decide.** The system only gives advice. A person approves every warning and every dispatch, and every decision is logged.

**Work untouched.** We only cut the time spent waiting for parts. Lockout and tagout, gas monitoring and restart steps stay exactly as they are. And if the data ever fails, every site defaults to on hold.

Thank you. We're happy to take your questions.

---

## Q&A cheat sheet (3 min)

| Question | Who | Answer |
|---|---|---|
| Is the $1.98M real money? | Nick | It's modeled margin from the case's own formula, not booked cash. We claim no repair savings. |
| Why not sensors or AI first? | Aayan | Sensors only help bearing and seal failures and take 5 months to switch on. Every monitored site is also locked by safety holds. We costed sensors at Arroyo as a Phase 2, decided at month 6. |
| What if oil prices drop? | Nick | At about $50 oil it still pays back by month 10. |
| What if the safety fixes are slow? | Sidra | Payback moves from month 8 to month 10. The three sites that aren't on hold still deliver. |
| How accurate is the failure model? | Wali | In testing it flagged 90 of 91 bearing and seal failures early. The data is synthetic, though, so we treat it as advice and count no hours from it. |
| How did you clean the data? | Austin | 39 automated checks. Nothing was guessed, and unknown costs stay unknown. One command rebuilds it all. |
| Where does the 60% come from? | Aayan | The case's own Solutions sheet. We also show its low (35%) and high (75%) cases. |
