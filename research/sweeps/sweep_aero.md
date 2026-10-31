# Sweep: Magnus, drag and spin decay of light / hollow / perforated balls (beyond the 12 priority papers)

PM-001 · sweep agent `sweep_aero` · 2026-10-30
Scope: sources NOT among the 12 priority papers (Lindsey 2025, Steyn 2025, Rossmann & Rau 2007, Emond 2024, Brettle, Pedersen 2026, Van Wyk 2026, Sakai 2016, Ito & Kamijima 2025, Cross & Lindsey 2017, Cross 2005, Allen 2010).
POLLEN regime for reference: D = 71 mm, m ≈ 25 g, v ≈ 2–10 m/s → Re = vD/ν ≈ 9.5e3–4.7e4 (ν = 1.5e-5 m²/s), S = ωR/v ≈ 0–2. S = 1 at v = 6 m/s means ω ≈ 169 rad/s ≈ 27 rev/s ≈ 1600 rpm.

**Nothing here is a POLLEN measurement.** Every coefficient below is for a smooth sphere, a table-tennis ball, a Wiffle ball or a dimpled sphere. Use them only to set the shape and the bounds of an uncalibrated Cl(S), Cd(S) and spin-decay model.

## Source list

| id | Citation | URL | Review status | Access | What it contributes |
|---|---|---|---|---|---|
| muto2012 | Muto M., Tsubokura M., Oshima N., "Negative Magnus lift on a rotating sphere at around the critical Reynolds number", Phys. Fluids 24, 014102 (2012), doi:10.1063/1.3673571 | https://eprints.lib.hokudai.ac.jp/repo/huscap/all/49222/PoF24-1_014102.pdf | peer-reviewed journal (LES, i.e. numerical) | full text (author repository) | CL and CD of a smooth spinning sphere at Re = 1.0e4 (inside the POLLEN range). It shows the lift is positive (normal Magnus) at subcritical Re and becomes negative only in the critical regime. It also compiles the older experimental Re windows for negative Magnus. |
| conti2026 | Conti C., Yang B., Sigrist A., Miele L., Saraiji Y., Dürr P., Takahashi N., et al. (Sony AI), "Physics Models for Sim-to-Real Transfer in Professional-Level Robot Table Tennis", arXiv:2606.28805 (v2, 1 Jul 2026) | https://arxiv.org/abs/2606.28805 (HTML: https://arxiv.org/html/2606.28805) | preprint (unreviewed) | full text (HTML) | CD(Re,Sp) and Magnus-coefficient tables for a hollow, light, smooth 40 mm ball. They were fitted to about 58,000 real flight segments at v = 2–17.5 m/s (Re ≈ 5e3–4.6e4), which overlaps POLLEN's Re. It is the best real-data shape for CL(S) at our Re. |
| sareen2024 | Sareen A., Hourigan K., Thompson M.C., "Varying Magnus effect on a rotating sphere at intermediate Reynolds numbers", Int. J. Heat Fluid Flow 109, 109501 (2024), doi:10.1016/j.ijheatfluidflow.2024.109501 | https://research.monash.edu/en/publications/varying-magnus-effect-on-a-rotating-sphere-at-intermediate-reynol/ (PDF host flair.monash.edu could not be reached; SSRN 4662313 returned 403) | peer-reviewed journal (experiment) | **abstract only** | The only experimental rotating-sphere study found that covers 1e3 < Re ≲ 5e4, which is exactly the POLLEN range. It reports a **sudden drop in both CL and CD at a critical rotation ratio**, followed by recovery. The critical value is not available to us. |
| kim2014 | Kim J., Choi H., Park H., Yoo J.Y., "Inverse Magnus effect on a rotating sphere: when and why", J. Fluid Mech. 754, R2 (2014), doi:10.1017/jfm.2014.428 | https://doi.org/10.1017/jfm.2014.428 ; https://scholarworks.unist.ac.kr/handle/201301/17804 | peer-reviewed journal (wind-tunnel experiment) | **abstract only** (Cambridge paywall) | Mechanism of inverse Magnus: the boundary layer on the side moving against the flow goes turbulent while the other side stays laminar. The paper gives empirical separation-angle formulae in (Re, spin ratio) and an onset condition, but we do not have the formulae or numbers. |
| miyazaki2017 | Miyazaki T., et al., "Lift crisis of a spinning table tennis ball", Eur. J. Phys. 38, 024001 (2017), doi:10.1088/1361-6404/aa51ea | https://doi.org/10.1088/1361-6404/aa51ea ; abstract indexed at https://inis.iaea.org/records/7k9tr-6pp60 (402 when fetched) ; UEC press release https://www.ru.uec.ac.jp/e-bulletin/topics/2017/fluid-mechanics-of-table-tennis-balls-discovery-of-spin-crisis.html | peer-reviewed journal (free-flight experiment) | **abstract only** (numbers from the abstract as quoted in search results and the press release) | Free-flight evidence that CL is **non-monotonic in SP**, with a deep valley near SP ≈ 0.5. This is a different measurement from Sakai 2016. |
| vilumbrales2024 | Vilumbrales-Garcia R., Sudarsana P.B., Sareen A., "Lift generation on a sphere through asymmetric roughness using active surface morphing", arXiv:2407.01748 (2024) | https://arxiv.org/abs/2407.01748 | preprint (unreviewed); experiment | full text | Quantifies lift on a **non-spinning** sphere caused by roughness on one side only. This is our best proxy for orientation-dependent side forces from an uneven hole pattern. It gives an empirical fit Re_c(k/d) and CLmax(k/d). |
| briggs1959 | Briggs L.J., "Effect of spin and speed on the lateral deflection (curve) of a baseball; and the Magnus effect for smooth spheres", Am. J. Phys. 27, 589–596 (1959) | (paywalled AJP; only secondary descriptions found: APS News 2019-03 history column; Kharlamov 2007 IT CAS paper) | peer-reviewed journal (wind-tunnel experiment) | **secondary only** | Historical first wind-tunnel observation that a smooth sphere can deflect **opposite** to the normal Magnus direction (reverse Magnus). No numbers were used. |
| james2008 | James D., Haake S., "The spin decay of sports balls in flight", in The Engineering of Sport 7, Vol. 2, Springer, pp. 165–170 (2008) | https://shura.shu.ac.uk/2132/ (blocked by bot check) ; https://sponet.de/sponet/Record/3042117?lng=en | conference proceedings (experiment) | **abstract only** | Measured spin decay of several balls in flight. dω/dt grows linearly with ω0·v0, with a constant that depends on the ball. Decay depends mainly on moment of inertia, then on roughness and boundary-layer regime. This supports a torque model linear in ω·v. |

Secondary pointers only (not counted as sources, not verified):
- **Harvey Mudd APS-DFD 2003 abstract "Aerodynamics of Wiffle Balls"** (ADS 2003APS..DFD.MJ005U; ADS returned 405). A search snippet says lift up to 0.2 N was measured on a Wiffle ball at 40 mph, partly attributed to air flowing into the holes. If that is right, it implies CL ≈ 0.24 at Re ≈ 8.8e4 on a ball with **no spin** (my arithmetic: q = 196 Pa, A ≈ 4.3e-3 m² for a 74 mm ball). Unverified.
- **Tavares et al. (golf) spin-decay torque** I·dω/dt = −R ρ A C_M v² with C_M ≈ 0.012·S. Seen only quoted inside US patents (US 6286364 family). Golf ball, unverified.

Rejected after reading: **Creer 2023**, BYU-Idaho BSc thesis "Computational Fluid Dynamics Analysis of Pickleballs" (https://brightspotcdn.byui.edu/f5/ef/bfdce4934c0c97c93cee95c8d33e/isaac-creerf23.pdf). Its abstract says the OpenFOAM model "could not calculate the drag coefficient accurately due to errors in the mesh generation", so do not use its numbers. Not obtainable: the Akron honors thesis on Wiffle hole patterns (Cloudflare block).

## Data extracted

### muto2012: smooth spinning sphere, LES (Table I p. 014102-9, Figs 7–8 p. 014102-7)
Definition (p. 014102-2): Γ = D_p ω / U0. The text calls this "the ratio of the circumferential velocity to the incoming flow velocity", but the formula as printed equals **2S**. The ambiguity is not resolved. Under the printed formula, Γ = 0.2 → S = 0.1 and Γ = 1.0 → S = 0.5. Under the wording, Γ = S.
CL = F_L / (ρ U0² A / 2), with A the frontal area.

| Re | Γ | CD mean (s.d.) | CLz mean (s.d.) | Notes |
|---|---|---|---|---|
| 1.0e4 | 0 | 0.046 as printed (0.016) | 0.005 (0.036) | **The printed 0.046 is a typo.** Fig. 8 plots ≈ 0.44–0.45. |
| 1.0e4 | 0.2 | 0.474 (0.011) | **0.167** (0.029) | normal Magnus; upper-side separation moves to 93° (+6° vs no spin) |
| 1.0e4 | 1.0 | 0.661 (0.054) | **0.301** (0.096) | |
| 2.0e5 | 0.2 | 0.376 (0.029) | **−0.250** (0.041) | negative Magnus (critical regime) |
| 2.0e5 | 1.0 | 0.271 (0.022) | 0.212 (0.034) | lift positive again |
| 1.14e6 | 0.2 / 1.0 | 0.244 / 0.330 | 0.179 / 0.268 | supercritical, positive |

Experimental Re windows for negative Magnus, quoted from p. 014102-2: Taneda 6e4–5e5 (Γ < 0.6); Maccoll 4.6e4–1.1e5; Davies 9e4.
Fig. 7, read by eye (approximate): Tsuji et al. 1985 data at Re 550–1600 rise from CL ≈ 0.05 at Γ ≈ 0.1 to ≈ 0.28 at Γ ≈ 0.7. Maccoll's curve dips to about −0.1 near Γ ≈ 0.2 and turns positive above Γ ≈ 0.4.

### conti2026: table-tennis ball (r = 0.020 m), real match flights (Sec. III-B, Eqs. 1–5 and coefficient tables)
Model: m·a = −½ C_D ρ A v|v| − C_M ρ V (v × ω) + m g, with V = 4/3 π r³, Re = 2vr/ν, Sp = rω/v.
Magnus coefficient (Eq. 5): C_M = m1·ω + s for ω ≤ ω_b, otherwise a·ω² + b·ω + c, with C_M ≥ 0 (so negative Magnus is excluded by construction). The tables are indexed by v_eff.
Converting to a standard lift coefficient (my conversion): **CL = (8/3)·C_M·Sp**.

Computed CL from the published tables (my arithmetic). Re uses the 40 mm ball:

| v (m/s), Re | Sp 0.1 | 0.25 | 0.5 | 0.75 | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|---|---|---|
| 2.0, 5.3e3 | 0.02 | 0.05 | 0.11 | 0.16 | 0.21 | 0.32 | 0.35 |
| 3.5, 9.3e3 | 0.08 | 0.18 | 0.29 | 0.33 | 0.31 | 0.32 | 0.36 |
| 7.5, 2.0e4 | 0.09 | 0.20 | 0.29 | 0.29 | **0.25** | 0.36 | 0.39 |
| 10.5, 2.8e4 | 0.09 | 0.19 | 0.27 | **0.23** | 0.26 | 0.41 | 0.39 |

At Re ≥ 2e4, CL rises steeply up to Sp ≈ 0.5, then **plateaus or dips** between Sp 0.75 and 1.0, then rises again to about 0.4 at Sp 1.5–2. The authors say the 2 m/s row is noisy.

CD breakpoints (Sp → CD):

| v | CD values |
|---|---|
| 2.5 m/s | 0.55 everywhere |
| 7.5 m/s | 0.49 at Sp 0–0.4; ridge 0.55 at 0.75; trough 0.48 at 1.1; 0.53 at 1.3–2 |
| 12.5 m/s | 0.47 → ridge 0.53 at 0.62 → trough 0.41 at 0.95 → 0.48 |
| 17.5 m/s | 0.47 → ridge 0.51 at 0.5 → trough 0.37 at 0.84 → 0.45 |

The paper includes no spin-decay model. Fit quality: median 3D position RMSE 8.1 mm.

### sareen2024 (abstract only)
- Experiments at 1e3 < Re ≲ 5e4.
- "Relatively sudden drop" in both CL and CD at a critical rotation ratio, then recovery at higher rotation. Similar to the drop near the drag crisis but smaller.
- Cause: the separation angle on the advancing side moves once the boundary layer turns unsteady/turbulent through a shear-layer instability. The authors suggest the origins of inverse Magnus may appear at lower Re than they tested.
- The critical rotation ratio, the size of the drop and whether CL changes sign are **not available** to us. Do not fill these in.

### kim2014 (abstract only)
- Inverse Magnus mechanism: the boundary layer moving against the surface transitions to turbulence, which delays separation on that side.
- The authors give empirical separation-location formulae in (Re, spin ratio) and an onset condition. These are not obtained.
- Their APS-DFD 2011 precursor (abstract seen through search only) reports wind-tunnel Re ≈ 0.6e5–2.6e5 and spin ratio 0–0.5. This is above the POLLEN range.

### miyazaki2017 (abstract only)
- 40 mm official ball (Nittaku 3-Star Premium) fired from a three-rotor launcher and filmed with high-speed video.
- Re ≈ 3.0e4–9.0e4, SP 0–1.0.
- "Deep valley of CL around SP = 0.5". Lift almost vanishes at Re = 9.0e4 and 0.48 < SP < 0.5.
- The paper reports qualitative agreement with wind tunnels and quantitative differences.

### vilumbrales2024: non-spinning sphere, dimples on one side (Fig. 2, Eqs. 1–2)
- Setup: 100 mm sphere, Re 6e4–1.3e5, k/d 0–0.01, turbulence intensity < 2 %, force balance plus PIV.
- Smooth-sphere CD ≈ 0.5 (subcritical). CD stays nearly constant when k/d changes.
- CLmax = 0.4 at Re = 1e5 (k/d = 0.003) and 0.35 at Re = 7e4 (k/d = 0.006). That is lift up to about 80 % of drag.
- Fits: **Re_c(k/d) = 75000·exp(−431·k/d) + 49600** and CLmax(k/d) = −0.01·exp(252·k/d) + 0.415.
- The fitted onset Re never drops below about 5e4 for k/d ≤ 0.01. That is the top of the POLLEN range.

### james2008 (abstract only)
- Ball types: tennis, worn tennis, football (soccer), oversize tennis. Fired by bowling machines and filmed with two high-speed cameras.
- Spin decay is linear in ω0·v0, with a constant that depends on the ball.
- Moment of inertia dominates, with roughness and boundary-layer regime second.

## Implications for the PM-001 model

1. **CL(S) baseline, normal Magnus, positive.** Every smooth-ball source at Re 5e3–5e4 shows positive lift that rises steeply to S ≈ 0.5 (CL ≈ 0.25–0.30):
   - Muto, Re 1e4: CL 0.167 at Γ 0.2 and 0.301 at Γ 1.0.
   - Conti: CL 0.09 at S 0.1, ≈ 0.19 at S 0.25 and 0.27–0.29 at S 0.5 (Re ≈ 0.9e4–2.8e4).
   - Suggested uncalibrated band for POLLEN: CL(S) = clamp(0.55·S … 1.2·S, ceiling 0.30–0.45) for S ≤ 0.5. Then a plateau of 0.22–0.35 between S 0.5 and 1.0, and a ceiling of 0.40–0.45 up to S = 2.
   - These are smooth-ball values. Perforations could raise or lower them, so keep the band wide until POLLEN is measured.
2. **Model a dip near S ≈ 0.4–1.0 as an explicit uncertainty case, not as the baseline.** Three sources point to it:
   - Sareen 2024 (sudden CL and CD drop at Re ≤ 5e4);
   - Miyazaki 2017 (CL valley at SP ≈ 0.5);
   - Conti 2026 (CL plateau or dip at Sp 0.75–1 for Re ≥ 2e4).

   A sensitivity case CL_dip(S) = baseline × (1 − 0.6·exp(−((S − S_c)/0.15)²)), with S_c ∈ [0.4, 1.0], is reasonable.
   - **Negative lift (inverse Magnus)** on smooth spheres is documented only at Re ≳ 4.6e4–2e5 (Muto, Kim, Maccoll, Taneda). That is at or above the top of the POLLEN range.
   - Roughness and perforation lower the critical Re (Vilumbrales; Kim's fog-paper citers), so a sign change cannot be ruled out for POLLEN at its fastest (launch, v ≈ 8–10 m/s).
   - Near the apex POLLEN is slow (Re ~1e4–2e4), so the lift there is very likely normal (positive). **More spin is not monotonically better.** This is consistent with HANDOFF §5.
3. **CD rises with spin.** Muto at Re 1e4: CD ≈ 0.45 → 0.47 → 0.66 as Γ goes 0 → 0.2 → 1.0. Conti: CD 0.47–0.55 with a ridge and trough near S 0.5–1.1. Use Cd(S) = Cd0·(1 + k_d·S) with Cd0 ∈ [0.45, 0.60] and k_d ∈ [0, 0.5] as the uncalibrated band. Extra drag partly cancels the range benefit of backspin.
4. **Spin decay is probably small over one shot, but perforations are unbounded.**
   - Model: I·dω/dt = −ρ A R³ k ω v, which is the Tavares form with C_M = k·S.
   - James & Haake's "linear in ω·v" result supports this form.
   - With I_shell ≈ (0.55–0.67)·m R² ≈ 1.7–2.1e-5 kg·m² and v = 4–7 m/s:
     - k = 0.012 (golf value) → 2–3 % spin loss in 1.2 s (my arithmetic);
     - k = 0.03 → 4–9 %;
     - k = 0.06 → 8–16 %.
   - Holes may pump air through the interior and raise k above golf/table-tennis values. No source measured this.
   - **Recommendation:** use k ∈ [0.01, 0.1] as the uncertainty band, and measure spin at launch and again near the HIVE with high-speed video.
5. **Hole-pattern side forces (knuckling).**
   - A non-spinning or slowly spinning perforated ball can feel orientation-dependent lift and side force of order CL ~ 0.1–0.4:
     - the Wiffle snippet implies ≈ 0.24 (unverified);
     - one-side roughness gives up to 0.35–0.4 (Vilumbrales), but only above Re ≈ 5e4 for dimples.
   - The two mechanisms differ. Wiffle balls have holes on one side only and air flows through the interior; POLLEN's holes appear to cover the whole shell, so the net asymmetry should be smaller but nonzero (pieces are "not perfectly spherical", HANDOFF §1).
   - Hypothesis, not established: steady backspin at about 20–40 rev/s turns the hole pattern many times per flight, which should average out orientation forces. Backspin may therefore improve shot-to-shot consistency even where it adds little lift.
   - **Test:** fire no-spin and spin shots at the same speed and compare lateral/vertical dispersion. Model the effect as a random force with CL_noise σ ∈ [0, 0.1] that scales down with spin rate.
6. **Re mapping.** For any table-tennis-derived curve, map by Re (and S), not by speed. POLLEN Re ≈ 1.78 × table-tennis Re at the same speed.

## Caveats
- Only muto2012, conti2026 and vilumbrales2024 were read in full. sareen2024, kim2014, miyazaki2017 and james2008 are abstract-only; briggs1959 and the Wiffle/Tavares items are secondary.
- conti2026 is an unreviewed preprint. Its model clips C_M ≥ 0 and is fitted per trajectory, so its fine structure is partly an artefact of the fit.
- muto2012 is a simulation, not a measurement. Its Γ definition is internally ambiguous: the printed formula gives Γ = 2S, the wording gives Γ = S. Its no-spin CD entry at Re 1e4 has a typo.
- None of these sources measured a perforated hollow ball with spin. POLLEN-specific Cl(S), Cd(S) and spin decay remain unmeasured.
