**Driving metric: net rating.** All three answers are built on one number: **net rating**, the points a unit scores minus the points it allows, per 100 possessions.

- Offensive rating (ORtg) = 100 × points scored ÷ offensive possessions
- Defensive rating (DRtg) = 100 × points allowed ÷ defensive possessions (lower is better)
- **Net rating = ORtg − DRtg**

I chose it because it covers **both ends of the floor** and is **per possession**. Raw plus-minus mostly rewards whoever played the most. ORtg or DRtg alone ignores half the game. League average this sample: 117.1 points per 100 possessions, 36.1% from three, 28.1% offensive rebound rate, 71.9% defensive rebound rate.

Following the prompt, I don't discount results for small samples. I do require a unit to have played before its rating counts: the highest "net ratings" in the data (+200 to +300) come from lineups that played 1 to 5 possessions. Every number below can be reproduced in the deployed app with the preset named in each answer; I also recalculated the key numbers directly from the raw JSON to confirm them.

---

1. Which 5-man lineup in the league has the most positive on-court impact?

**Justice League: Phantom Stranger, Superman, Green Lantern, Red Tornado, Batman. Net rating +36.0.** In the app: *Best lineups* preset, with the min. possessions slider at 40.

**How the net rating is calculated for this lineup:**

| | Points | Possessions | Per 100 |
|---|---|---|---|
| Offense | 37 scored | 25 | **148.0** ORtg |
| Defense | 28 allowed | 25 | **112.0** DRtg |
| **Net** | **+9** | | **+36.0** |

**Which lineups are compared.** Lineups with at least **40 total possessions**, about 20 on each end, a bit less than a quarter of a game. That's 11 of the 227 five-man lineups, and together they account for about a quarter of all five-man lineup possessions. Top five by net rating:

| # | Lineup | Poss | ORtg | DRtg | **Net** |
|---|---|---|---|---|---|
| 1 | **JL: Phantom Stranger, Superman, Green Lantern, Red Tornado, Batman** | 50 | 148.0 | 112.0 | **+36.0** |
| 2 | TS: Sniffles, Witch Hazel, LeBron James, Bugs Bunny, Lola Bunny | 52 | 80.8 | 50.0 | +30.8 |
| 3 | JL: Nightwing, Phantom Stranger, Green Lantern, Black Canary, Batman | 47 | 100.0 | 86.4 | +13.6 |
| 4 | JL: Phantom Stranger, Hawkman, Green Lantern, Red Tornado, Black Canary | 95 | 129.8 | 116.7 | +13.1 |
| 5 | TS: Yosemite Sam, Tweety, Daffy Duck, LeBron James, Tasmanian Devil | 67 | 117.6 | 109.1 | +8.6 |

**Where the +36.0 comes from.** Mostly offense: the lineup scores **30.9 more points per 100 than the league average** (148.0 vs. 117.1) and allows **5.1 fewer** (112.0 vs. 117.1). That comes down to shot quality and ball security: a **76.1% effective FG%** (league 55.3%) and a **4% turnover rate** (league 14%).

**The pick holds up under other rankings.** It leads #2 by 5.2 points of net rating. It is also #2 in raw plus-minus (+9), behind a lineup that played only 18 possessions.

**Weakness to know about:** it rebounded 0 of 8 of its own misses, so it wins by making its first shot. That matters for question 3.

2. Which player has the most positive on-court impact?

**Dr. Strange (The Avengers). On/off net rating +34.5.** In the app: *Player impact* preset.

**Same metric, applied to one player.** A lineup's net rating credits exactly the five players on the floor. A single player's on-court net rating also includes his four teammates, so a good player on a good team looks better than he is. To isolate the player, I use **on/off net rating**: the team's net rating with him on the court minus its net rating with him on the bench. Same metric as question 1, just compared against his own team.

**Candidates** (at least 200 on-court possessions, about one full game):

| Player | Team (overall net) | On-court net | Off-court net | **On/off** |
|---|---|---|---|---|
| **Dr. Strange** | Avengers (−7.0) | +15.8 | −18.7 | **+34.5** |
| Red Tornado | Justice League (+1.1) | +14.1 | −3.6 | +17.7 |
| Green Lantern | Justice League (+1.1) | +8.3 | −9.1 | +17.4 |
| Sniffles | Tune Squad (+5.8) | **+19.3** | +2.6 | +16.8 |

**Rechecking the result.** I recalculated these numbers directly from the raw possession data, without the app's code, and they match. One result needs explaining: on **on-court** net rating alone, **Sniffles ranks first (+19.3)**, ahead of Dr. Strange (+15.8). That changes once you account for team:

- The Tune Squad is the league's best team (+5.8) and is still **+2.6 without Sniffles**. Part of his +19.3 is his teammates.
- The Avengers are the league's worst team (−7.0), and they go from **−18.7 without Dr. Strange to +15.8 with him**. That swing is about double anyone else's.
- If the minimum is raised to 300 possessions, Dr. Strange also leads on on-court net rating. He also has the league's best raw plus-minus (+32).

**Where his impact comes from:** mostly defense. Opponents score 104.5 per 100 with him on the court, 12.6 below league average, and the Avengers still score 120.2.

3. A new team is entering the league, and they are known for deploying lineups with multiple centers and large forwards. These lineups are effective at both offensive and defensive rebounding due to their size and emphasis on crashing the glass. Which 5-man lineup is best suited to countering this strategy, and why?

**Tune Squad: Sniffles, Witch Hazel, LeBron James, Bugs Bunny, Lola Bunny.** In the app: *Counter big lineups* preset with the min. possessions slider at 40. The table is sorted by REB%; compare the Net and 3P% columns.

**How I ranked lineups.** A glass-crashing big lineup wins by creating extra possessions: offensive rebounds give it second shots, and defensive rebounds deny the opponent any. So I ranked in two steps:
1. **Rebounding first.** Total rebound share: the percentage of all available rebounds, on both ends, that a lineup secures. A counter has to take the glass away on defense and not give it up on offense. The data has no heights or positions, so rebound rates are the direct measure of "can handle size."
2. **Net rating second.** Among the best rebounding lineups, pick the one that actually outscores opponents. Rebounding only matters if it turns into points.

**Top rebounding lineups** (40+ possessions; league: 71.9% defensive, 28.1% offensive rebound rate):

| Lineup | Total REB% | DREB% | OREB% | **Net** | 3P% |
|---|---|---|---|---|---|
| JL: Phantom Stranger, Superman, Elongated Man, Aquaman, Batman | 57.7% | 100% (9/9) | 35.3% | −16.2 | 40.0% (2/5) |
| **TS: Sniffles, Witch Hazel, LeBron James, Bugs Bunny, Lola Bunny** | **57.6%** | **92.9% (13/14)** | **31.6%** | **+30.8** | 14.3% (2/14) |
| JL: Phantom Stranger, Green Lantern, Red Tornado, Black Canary, Batman | 56.0% | 76.9% (10/13) | 33.3% | +7.1 | 44.4% (4/9) |

The top two are essentially tied on the glass. **Net rating separates them by 47 points per 100:** the Justice League unit gets outscored by 16.2, and the Tune Squad unit outscores opponents by 30.8.

**Why the Tune Squad lineup counters size:**
- **It ends possessions after one miss.** A 92.9% defensive rebound rate, 21 points above league average, means the big team's main weapon, second-chance shots, almost disappears.
- **It doesn't give up its own glass.** A 31.6% offensive rebound rate, above league average, so the opponent's size doesn't win the other end either.
- **It wins the possession battle in other ways too.** It forces turnovers on 26.9% of possessions, nearly double the league's 14%. A lineup with multiple centers is usually slower with the ball, and every turnover is a possession the big team never gets to crash the glass on.
- **Its first-shot defense is elite.** Opponents post a 22.2% effective FG% against it, and a 50.0 defensive rating: half the league's 117.1. Few makes plus almost no second chances leaves a glass-crashing team with very little.
- **It outscores opponents: +30.8 net rating,** the best of any lineup in the top rebounding group.

**3-point shooting: the trade-off to plan around.**
- **Its own shooting is its weakness.** It made 2 of 14 threes (14.3%, league 36.1%) while taking half its shots from deep. Against a big team, threes normally pull a center away from the basket. This lineup doesn't make enough of them to force that, so a big team can pack the paint against it on offense.
- **On defense it holds up:** opponents made 0 of 7 threes against it, so a big team can't punish it from outside either.
- **If shooting is the priority,** the Justice League unit in the third row is the alternative: nearly as good on the glass (56.0%), 44.4% from three, and positive but smaller net rating (+7.1). I rank rebounding first because it's the specific strength this opponent is built on, and the Tune Squad unit takes it away better while outscoring opponents by far more.
