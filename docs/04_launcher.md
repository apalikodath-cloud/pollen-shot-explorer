# 04 — Single-powered-wheel launch model (hood vs passive roller)

Task PM-001, HANDOFF §4C, §4D, deliverable 6. Code: `src/launcher.py`. Tests: `tests/test_launcher.py`.
Data: `data/launch_envelope.json`. Figures: `figures/launcher_*.png`.
Status: every output number here is **predicted**: the model is uncalibrated and nothing has been measured yet.
Labels used: **confirmed** (official or vendor source), **user**, **assumed**, **derived**, **predicted**.

Scope stays as the user set it: ONE powered 98 mm flywheel, plus either a fixed hood or ONE unpowered roller. The roller is
never treated as a driven wheel.

## 1. Inputs and provenance

| Quantity | Value (range) | Label / source |
|---|---|---|
| Ball mass m | 0.025 kg (0.0245–0.0255) | confirmed: AndyMark am-5851_yellow lists 0.055 lb = 24.95 g (HANDOFF §1). Weigh samples. |
| Ball radius R_b | 0.0355 m | confirmed nominal 2.8 in (HANDOFF §1, §2). Pieces vary. |
| Ball inertia I_b = k_I m R_b² | k_I 0.63 (0.55–2/3) → I_b 1.99e-5 kg m² (1.73e-5 to 2.10e-5) | derived/assumed, see §1.1 |
| Wheel radius R_w | 0.049 m | user (98 mm wheel) |
| Flywheel inertia I_w | 2.65e-4 kg m² (0.5e-4 to 5e-4) | assumed bare wheel ~1.0e-4, plus goBILDA steel flywheel 3628-0032-0082 (82 mm, 152 g, 1651 g cm² = 1.651e-4 kg m²), confirmed at https://www.gobilda.com/steel-flywheel-82mm-diameter-152g-1651-g-cm/ |
| Motor, goBILDA 5203 1:1 | 6000 rpm free, 0.144 N m stall (1.47 kg cm), 9.2 A @ 12 V | confirmed: https://gobilda.com/5203-series-yellow-jacket-motor-1-1-ratio-24mm-length-8mm-rex-shaft-6000-rpm-3-3-5v-encoder . A related 5202 lists ~5400 rpm *tested* free speed, so the real free speed is lower. |
| Motor, REV HD Hex (bare) | 6000 rpm, 0.105 N m, 8.5 A @ 12 V; UltraPlanetary 5.23:1 → 1147 rpm, 0.55 N m | confirmed: https://docs.revrobotics.com/duo-build/motion/motors/hd-hex-motor |
| Rotor inertia | not published; bounded < ~1e-5 kg m² (×gear²) | assumed |
| μ wheel tread vs PE | 0.8 (0.5–1.2) | assumed |
| μ hood vs PE | 0.3 (0.05–1.0): PTFE/UHMW 0.05–0.15, PC/acrylic/HDPE 0.2–0.4, rubber or grip tape 0.6–1.0 | assumed |
| Compression δ (diametral) | 4 mm (2–8 mm swept) | user candidate (HANDOFF §2) |
| Ball stiffness k_n, with N = k_n δ | 4 N/mm (1.5–10) | **assumed. No source was found.** Measure it (§8). |
| Rolling hysteresis c_rr | 0.02 (0–0.06) | assumed |
| Hood wrap angle | 90° (45–150°) | assumed; no shooter CAD (HANDOFF §2) |
| Feed speed v_in | 0.5 m/s (0.2–1.5); 3–5 m/s probed | assumed |
| Roller: R_t, I_t, bearing drag | 24 mm (12.5–50), 1e-5 kg m² (1e-6 to 2e-4), 5e-4 N m Coulomb (0–3e-3) + 1e-6 N m s | assumed |
| Shot interval | 0.5 s (0.25–1.5) | assumed |

### 1.1 Ball inertia (hollow perforated shell)
- A thin shell has k_I = 2/3. This is the upper bound for any sphere whose mass sits at or inside its surface.
- A uniform PE shell (ρ ≈ 950 kg/m³) of 25 g at R = 35.5 mm needs t ≈ 1.7 mm with no holes, or about 2–2.4 mm with
  20–30 % open area. The thick-shell formula k_I = 0.4(1−q⁵)/(1−q³), q = 1 − t/R, then gives 0.62–0.64 (derived).
- A uniform hole pattern removes mass evenly over the shell, so it does not change k_I.
- 0.55 is a conservative lower bound for ribs, thick bosses and non-sphericity (assumed).
- Pickleball values are not used.
- Measure k_I with a bifilar or trifilar pendulum.

### 1.2 Dean Brettle, *Flywheel Shooter Analysis* (https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html)
- Assumptions, as stated on the page:
  - the projectile rolls without slipping on the hood at exit, and on the wheel at exit;
  - no other forces or torques act; motor compensation happens only after exit;
  - the axle and hood are fixed to a massive frame;
  - the bodies are rigid, so the ball is not compressed.
- Results:
  - ω_wi/ω_wf = 1 + (1+k_p)/(4k_w) · m_p/m_w;
  - v_p = ω_wf r_w / 2;
  - ω_p = v_p/r_p;
  - efficiency η = (2 + (1+k_p)/(4k_w) · m_p/m_w)⁻¹ < 50 %.
- Limits stated in the page's Discussion:
  - If the ball is still slipping at exit, "its exit velocity will be determined by the frictional forces", which do
    not depend on wheel speed. The page advises designing for rolling at exit in the worst case.
  - Compression "will typically cause the shape factor to rise". Because the ball is not a perfect spring, the wheel
    slows more than predicted, and this is usually compensated empirically.
  - Kick of the shooter mount.
  - A low-latency control loop can refill the wheel during contact. Otherwise coast mode is suggested.
- This model keeps Brettle's impulse accounting and adds slip, compression radius, finite contact length, a normal-load
  law, centripetal unloading, hysteresis, motor torque and the passive roller. With the right switches it reproduces
  his formula exactly; a unit test checks this.

## 2. Ideal no-slip stationary hood (derived)
Planar case:
- the wheel is below the ball and the hood is above it;
- x is the direction of travel;
- s is the ball's angular velocity, positive = backspin (the wheel-side point moves forward relative to the centre);
- Ω is the wheel speed, positive = surface moves forward at the contact.

Contact-point velocities [m/s] for diametrically opposite contacts at distance r_c from the ball centre:

    hood-side point:   v − s r_c        wheel-side point:   v + s r_c

No slip at the fixed hood means v − s r_c = 0. No slip at the wheel means v + s r_c = R_w Ω. Adding and subtracting:

    v_exit = R_w Ω_exit / 2                [m/s]    (Ω in rad/s, R_w in m)
    ω_ball = v_exit / r_c                  [rad/s]
    S = ω R_b / v = R_b / r_c              (= 1 for a rigid ball, r_c = R_b)

Example: 3000 rpm gives 314.2 rad/s, so v = 0.049·314.2/2 = 7.70 m/s and ω = 216.8 rad/s = 2070 rpm, at the wheel speed
**at exit**.

The hood does not need to be straight. For a hood concentric with the wheel, both contact normals pass through the ball
centre and the wheel axis, and the tangential directions coincide. The same equations then hold with s as the
*absolute* ball angular velocity. The only changes are that the exit direction turns through the wrap angle and that
the normal loads become unequal (§3).

The ideal relations fail when:
1. **The ball slips at exit**, at either contact.
   - Wheel slip: the Coulomb force μN does not depend on RPM, so v and spin stop growing with RPM. This is the
     "grip-limited" regime in §5.
   - Hood slip: S lies between 1 and m r_c R_b / I_b (≈ 1.5).
2. **The ball compresses.**
   - r_c < R_b, so S = R_b/r_c > 1 (1.03 at 2 mm, 1.06 at 4 mm, 1.13 at 8 mm with λ = 1).
   - The wheel tread also compresses, so the effective R_w is R_w − δ_w and v drops.
   - Hysteresis makes the wheel lose extra speed (Brettle's "shape factor rises").
   - How the squeeze splits between ball and tread, and the flattened-patch rolling radius, are unknown, so
     r_c = R_b − λδ/2 with λ ∈ [0, 1].
3. **The contacts are not diametrically opposite.**
   - A converging or diverging hood, or a ball off the wheel's radial line, tilts the contact normals.
   - The constraints then mix normal and tangential components, δ changes along the path, and v_exit ≠ R_wΩ/2.
   - This needs CAD and is not modelled beyond a uniform-gap concentric hood.
4. **The wheel slows during contact.** Ω_exit < Ω_initial (Brettle drop, §3.2). The ideal relations use the *exit* wheel
   speed.
5. **The ball enters already moving or spinning** (fast feeder). The ideal state is reached only if the contact is long
   enough. Otherwise S < 1 is possible (§4).
6. **The ball is a non-sphere** (variation between pieces, perforation lands). This adds scatter and is not modelled.

## 3. Impulse / contact model (`simulate_shot`)

### 3.1 Equations
State: v, s, Ω, Ω_t (roller only), and the path position x. F_w and F_t are the friction forces **on the ball**,
positive forward.

    m   dv/dt    = F_w + F_t
    I_b ds/dt    = r_c (F_w − F_t) + M_hyst,ball
    I_w dΩ/dt    = −R_w F_w + τ_motor(Ω) − M_hyst,wheel        (τ_motor = 0: coast, Brettle; or full-voltage DC line)
    I_t dΩ_t/dt  = −R_t F_t − τ_bearing(Ω_t) + M_hyst,roller   (roller only; τ_b = τ_c tanh(Ω_t/0.5) + c_v Ω_t)
    slip_w = R_w Ω − (v + s r_c),   slip_t = R_t Ω_t − (v − s r_c)   (hood: R_t Ω_t ≡ 0)

How each step is solved:
- **Coulomb friction:** |F| ≤ μN with exact stick/slip. Each step is a 2×2 box LCP. A = J M⁻¹ Jᵀ is symmetric positive
  definite, so the solution is unique and all 9 modes are enumerated.
- **Energy ledger:** each step is a constant-force impulse update, and the ledger uses mid-step velocities. Wheel KE
  lost + motor work = ball KE + roller KE + sliding loss + hysteresis + bearing loss, and it closes to about 1e-13 J
  (unit-tested).

Normal loads:
- **Hood:** δ is constant along a concentric hood of wrap angle θ. The ball is a series pair of half-springs, so
  N_t + N_w = 2 k_n δ. The centripetal requirement gives N_t − N_w = m v²/ρ, with ρ = R_w + r_c. Therefore
  N_w = k_nδ − m v²/(2ρ). If N_w reaches 0, the ball rides on the hood alone and the result is flagged
  `lost_wheel_contact`.
- **Roller:** the ball passes a nip. The gap grows parabolically,
  δ(x) = δ − x²/2·[1/(R_w+R_b) + 1/(R_t+R_b)], so the contact length is short (≈ 34 mm for 4 mm and R_t = 24 mm,
  against ≈ 131 mm for a 90° hood).
- Gravity along the path is ignored: the contact time of 12–60 ms gives an error of < 0.06 m/s.

### 3.2 Momentum accounting (derived; exact checks in the tests)
Wheel impulse J_w = −I_w ΔΩ/R_w. Roller impulse J_t = −I_t ΔΩ_t/R_t.

    m Δv = J_w + J_t ,     I_b Δs = r_c (J_w − J_t)
    ⇒ roller:  m Δv + I_w ΔΩ/R_w + I_t ΔΩ_t/R_t = 0   and   I_b Δs/r_c + I_w ΔΩ/R_w − I_t ΔΩ_t/R_t = 0
    ⇒ hood:    m Δv + I_b Δs/r_c + 2 I_w ΔΩ/R_w = 0

Rolling at both contacts at exit, starting from feed speed v_in (generalised Brettle):

    Ω_i = Ω_f [1 + R_w² (m + I_b/r_c²) / (4 I_w)] − R_w m v_in / (2 I_w)

- With r_c = R_b and v_in = 0, the bracket is Brettle's 1 + (1+k_I) m R_w²/(4 I_w).
- Nominal I_w = 2.65e-4: ratio 1.092, about an 8.5 % drop (≈ 254 rpm at 3000 rpm).
- Bare wheel, I_w = 1e-4: ratio 1.245, about a 20 % drop.
- **Derived.**

### 3.3 Why a fixed hood gives S ≥ R_b/r_c ≥ 1 (and how S can exceed 1)
- **Wheel friction alone**, ball starting at rest:
  - m dv = F dt and I_b ds = r_c F dt, so S = m r_c R_b / I_b = 1/k_I · (r_c/R_b) ≈ **1.50** (nominal).
  - Because k_I < 1, the ball's hood-side point moves **backward**. The hood's static friction therefore pushes the
    ball **forward**, F_t = F_w(k−1)/(k+1) < 0 in Brettle's sign. It removes spin and adds speed until S = R_b/r_c.
- **The hood's job** is therefore to pull S *down* toward 1, not to create spin.
- **High hood friction or a long wrap:** rolling is reached, so S = R_b/r_c ≈ 1.03–1.13.
- **Low friction (PTFE) and a short wrap:** S stays nearer 1.5 (max 1.27 in the parameter box with c_rr = 0.02).
- **S < 1 from a fixed hood** is possible only if the ball **enters already moving** (pre-accelerated, little spin)
  *and* leaves before hood friction rolls it up. Examples at 3000 rpm: 20° wrap, μ_h 0.05, v_in 4 m/s gives S 0.49;
  45°, 0.05, 5 m/s gives S 0.64. This is impractical and fragile.

## 4. Passive upper roller
I_t dΩ_t/dt = −R_t F_t − τ_bearing.

**Prediction: with a slow feed, the ball drags the roller BACKWARD.** The roller turns in the same rotational sense as the
flywheel, with its contact surface moving opposite to the ball. The cause is the same as in §3.3: k_I < 1 makes the
ball's top point move backward. The model therefore predicts:
- A light roller lets S rise toward ≈ 1.5 instead of reducing spin. At 3000 rpm from rest: I_t 3e-7 gives S 1.13–1.24
  depending on R_t; I_t 1e-5 with R_t 24 mm gives 1.107.
- A heavy roller approaches the fixed hood (I_t 2e-4 gives 1.063; the hood gives 1.060).
- Exception at low wheel speed: at 1000 rpm the 0.5 m/s feed is a large fraction of v_exit, so the nominal roller is spun
  forward (+79 rpm) and S = 0.974. The backward drag appears from about 2000 rpm upward (roller −66 to −90 rpm).
  See `figures/launcher_roller.png`.
- The HANDOFF heuristic, "a free roller spins up and reduces the spin differential", only holds when the ball's top
  point moves **forward**. That happens with a fast feed, v_in of a few m/s:
  - 3000 rpm, light roller: v_in 2 m/s gives S 0.92; 4 m/s gives S 0.67.
  - The roller is then spun forward, so later shots in a burst are pre-spun forward and **S drifts down shot to shot**.
    With near-frictionless bearings, a 0.5 s interval and v_in 3 m/s: 0.90 → 0.72 over 6 shots.
  - With 5e-4 N m bearing drag, the roller stops between shots and S is repeatable.
- Driving the roller's surface forward (S < 1) needs an external drive, which is out of scope. The hypothetical values are
  listed in the JSON only to show the mechanism (Ω_t0 +200 rad/s gives S 0.26).
- **Speed penalty:** the nip contact is short, so a roller is grip-limited far earlier. Nominal: v caps at **5.03 m/s**
  above ≈ 2500 rpm, against 8.91 m/s for the 90° hood at the same δ and k_n.

## 5. Results (predicted; `data/launch_envelope.json`)
Nominal hood: μ_w 0.8, μ_h 0.3, δ 4 mm, k_n 4 N/mm, wrap 90°, k_I 0.63, I_w 2.65e-4, coasting wheel.

| wheel rpm | v_exit m/s | spin rpm | S | rpm drop | regime |
|---|---|---|---|---|---|
| 1000 | 2.24 | 638 | 1.060 | 127 | rolling (hysteresis-heavy) |
| 2000 | 4.64 | 1323 | 1.060 | 192 | rolling |
| 3000 | 7.00 | 1994 | 1.060 | 273 | rolling |
| 3500 | 8.17 | 2329 | 1.060 | 316 | rolling |
| ≥4000 | **8.91** | 2539 | 1.060 | 344 | **wheel slipping at exit: grip-limited, RPM independent** |

Other configurations:

| Configuration | Grip-limited cap of v_exit | Notes |
|---|---|---|
| Ideal (Brettle) | none (14.09 m/s at 6000 rpm) | S = 1 |
| PTFE hood, 45° wrap | 7.34 m/s | |
| Soft ball (k_n 1.5 N/mm) | 5.45 m/s | |
| Stiff ball (10 N/mm) at 8 mm squeeze | none up to 6000 rpm (13.9 m/s) | S 1.127; rpm drop 347–589; hysteresis loss large at low rpm |

Parameter box at 3000 rpm:

| Mechanism | S range | v range |
|---|---|---|
| Fixed hood (405 cases) | 1.029 – 1.274 | 3.2 – 7.05 m/s |
| Passive roller (216 cases, shots 1–3 of a burst) | 1.06 – 1.24 | 4.9 – 7.1 m/s |

**The single-wheel device does not give independent control of v and ω.** Both mechanisms deliver S of roughly 1.0–1.3,
with ω ≈ S·v/R_b, so the spin is fixed by the exit speed. Ways to move S:
- **Up**, toward ≈ 1.5: low-μ hood with a short wrap, a light passive roller, or more compression.
- **Below 1:** only with a fast pre-accelerated feed.

Practical consequence for the trajectory team: use S ∈ [1.0, 1.3] as the realistic hood or roller band at
v ≈ 4–9 m/s. Treat S < 1 or S > 1.5 as unreachable without design changes (feeder speed, a driven second wheel — out of
scope).

Motor and wheel recovery, hood nominal (derived):
- During contact: full 12 V instead of coasting raises v by 0.16–0.26 m/s at 2000–3000 rpm and cuts the drop by
  60–100 rpm. In the grip-limited regime (4000 rpm) it adds no exit speed and only cuts the drop from 344 to 300 rpm.
- After the shot, a 5203 1:1 motor restores the drop in ≈ 0.10 s at 3000 rpm, 0.18 s at 4000 and 0.34 s at 5000. It
  cannot hold 6000 rpm under load. Battery sag (11.5 V) lengthens these times.
- This assumes no current limit and no controller lag. Running near free speed costs both recovery and consistency.

Energy and wear at 3000 rpm (ledger):

| Loss | Hood | Roller |
|---|---|---|
| Ball KE gained | 1.04 J | 0.56 J |
| Wheel KE spent | 2.27 J | 1.60 J |
| Wheel-contact sliding loss | 1.09 J | 1.00 J |
| Top-contact sliding loss | ≈ 0.001 J | ≈ 0.001 J |
| Hysteresis | 0.14 J | 0.04 J |

- The top contact sticks almost immediately in both cases, so **ball wear and heating are dominated by the wheel-side
  slip during spin-up**. That loss is ≈ half of the wheel energy in any slip-then-roll process (Brettle η < 50 %).
- A hood adds about 3× the hysteresis of a roller because the squeeze lasts longer.
- Rubbing on a hood only becomes significant with low-μ hoods or fast feeds, where the ball slides along the hood.

## 6. Hood vs passive roller (evidence from this model)

| Criterion | Fixed hood (concentric, 90°) | Passive roller (nip) |
|---|---|---|
| Achievable v at δ 4 mm, k_n 4 N/mm | up to 8.9 m/s (grip cap) | up to 5.0 m/s (short nip) |
| S | 1.03–1.13 (set by compression); up to 1.27 with PTFE and short wrap | 1.06–1.24 from rest/slow feed (above the hood); < 1 only with a fast feed |
| Consistency | rolling exit → S fixed by geometry; v tracks exit wheel RPM (battery, recovery) | depends on I_t, bearing drag, shot interval and feed speed; S drifts in bursts when bearings are free |
| Losses | more hysteresis (longer squeeze) | less hysteresis; less wheel energy per shot |
| Ball wear | dominated by wheel slip; hood scuff small unless low μ or fast feed | same wheel slip; roller adds little |
| Grip-limited regime | consistent in v (RPM independent) but sensitive to μ and N, i.e. ball-to-ball and wear | same, earlier |

**Recommendation (predicted, to be tested): use the fixed hood.**
- It reaches the speed range with margin and gives a stable S ≈ 1.06 at 4 mm.
- The passive roller does not "reduce spin" for a slow-fed ball; it slightly *raises* S and costs exit speed.
- If higher S is needed, the cheapest lever is a low-μ hood section near the exit, or a shorter wrap. Both raise S toward
  1.2–1.3 with little loss of v.
- Do not design to the grip-limited regime unless you have measured that it is repeatable.

## 7. Limitations (state with any number used downstream)
- Linear N(δ) with an unknown k_n. A hollow shell buckles, so N(δ) is non-linear.
- The split of compression between ball and tread is unknown (λ).
- Constant μ; real tread μ falls with slip speed and heat.
- 1-D concentric contact path. Entry ramps, converging hoods and off-axis contacts are not modelled.
- No ball rotation about other axes; no sidespin.
- No frame kick.
- Motor modelled as a linear line without current limit or controller dynamics.
- Ball mass, radius and stiffness variation between pieces only through the parameter boxes.
- All results are **predicted**.

## 8. Measurements that would calibrate this model
1. Weigh 10 balls. Find k_I with a trifilar pendulum.
2. Measure N(δ) between flat plates at 2, 4, 6 and 8 mm on a kitchen scale. This gives k_n and the non-linearity.
3. Measure μ by incline or pull test for ball on tread and ball on candidate hood materials.
4. Slow-motion video with ball markings: v_exit and spin vs wheel RPM, for 2, 4 and 6 mm gaps. Log encoder RPM before and
   after each shot to get the drop.
5. Roller only: put a marker on the roller and check its rotation sense. The model predicts it turns *with* the flywheel
   when the feed is slow. If it turns the other way, the k_I or feed assumption is wrong.

## 9. Reproduce
    python src/launcher.py                       # writes data/launch_envelope.json and figures/launcher_*.png
    python -m unittest discover -s tests -v
