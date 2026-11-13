FeatureScript 3112;
import(path : "onshape/std/common.fs", version : "3112.0");

/*
 POLLEN precision shooter, Concept A: concentric tilting hood + counter-roller head.
 Source brief: FTC_POLLEN_PRECISION_SHOOTER_CAD_HANDOFF.md (2026-11-07).

 Frame (brief): X downrange, Y up, Z along the shafts, F = main flywheel centre = origin.
 Onshape world: brief (x, y, z) -> world (x, -z, y), so the brief's side view is Onshape's Front view.
 alpha = exit angle FROM VERTICAL (+Y toward +X); t(alpha) = (sin a, cos a);
 counter-roller centre = F + C (cos a, -sin a), i.e. phi = -alpha.

 All solids are nominal, undeformed envelopes. Ball-to-wheel / ball-to-hood overlap is the intended
 nominal soft-body compression, not a rigid collision.
 ASSUMPTION (flagged): when placing ball centres the interference is split equally between the two
 contacts (main wheel / hood or main wheel / counter-roller).
 Dimensions that are not in the brief are placeholders; their variable descriptions say TBD.

 Ramp feed (feed_handoff = 1): balls come UP the robot ramp, roll over a convex crest, drop down a short chute
 and land on a FIXED slotted floor (two rails, concentric with F) under the main wheel. A narrow tongue on the
 TILTING head runs inside the floor slot ahead of the hood; it lifts the ball off the rails and into the main
 wheel at every alpha between the stops, so the fixed floor never has to move with the head.
 feed_handoff = 0 restores the original straight hood lead (no floor).

 Actuators (feature option "Actuators", default on; placeholders, every part TBD): one servo on the outside of the
 -Z frame plate sets alpha. Servo -> coupler -> 8 mm shaft (bearing in the -Z frame plate) -> pinion, meshing with a
 gear sector bolted to the -Z head side plate (pitch radius ang_sector_R about F, ratio ang_ratio : 1). The servo
 therefore tilts the whole head (hood, counter-roller, its guard and motor) about F. A second servo turns a ball gate
 (the "flapper") on a shaft across the feed just upstream of the crest apex: closed, it holds the next ball on the
 ramp; open (feature option "Crest gate open", swing gate_swing) it swings up with the flow and lets one ball over.
 Turning "Actuators" off restores the earlier model (clevis pin on the tail arm, no servos, no gate).
*/

const MM = millimeter;
const ZAX = vector(0, -1, 0);            // brief +Z in world coordinates
const ORIGIN = vector(0, 0, 0) * meter;
const PNAME = "pollenName";              // attribute holding each part's name (read by the clearance check)
const TAIL = 140 * degree;               // head-local direction of the stop / actuator arm
const MOTOR_C = vector(115, 72) * millimeter;   // head-local counter motor envelope centre (TBD)
const A_MIN = 5 * degree;                // head hard stops (alpha range from the brief)
const A_MAX = 25 * degree;
const WALL_H = 44 * millimeter;          // feed side-wall height above the rail line (TBD)
// Actuator placeholders (all TBD): angle servo + pinion + gear sector on the -Z side, ball gate at the crest.
const ANG_MESH = 150 * degree;           // frame angle (about F) of the angle pinion centre
const GATE_DX = 8.4 * millimeter;        // gate shaft this far upstream (-x) of the crest apex
const GATE_UP = 11 * millimeter;         // gate shaft this far above the top of a D_max ball at the crest apex

export const ALPHA_BOUNDS = { (degree) : [0, 15, 45] } as AngleBoundSpec;
export const OFF_BOUNDS = { (millimeter) : [-5000, 0, 5000] } as LengthBoundSpec;

// ---------------------------------------------------------------- helpers
function W(x is ValueWithUnits, y is ValueWithUnits, z is ValueWithUnits) returns Vector
{
    return vector(x, -z, y);
}

function zPlane(xo is ValueWithUnits, z is ValueWithUnits) returns Plane
{
    return plane(W(xo, 0 * MM, z), ZAX, vector(1, 0, 0));
}

function pol(r is ValueWithUnits, th is ValueWithUnits) returns Vector
{
    return vector(r * cos(th), r * sin(th));
}

function vr(context is Context, name is string)
{
    return getVariable(context, name);
}

// Variable with a default, so the feed variables are optional.
function vrd(context is Context, name is string, dflt)
{
    var v = dflt;
    try silent
    {
        v = getVariable(context, name);
    }
    return v;
}

function fmm(x is ValueWithUnits) returns string
{
    return toString(roundToPrecision(x / MM, 2));
}

function fdg(x is ValueWithUnits) returns string
{
    return toString(roundToPrecision(x / degree, 1));
}

// Angle before the nip line (ball centre on a circle of radius rc about F) at which a ball of
// diameter D first reaches the counter-roller envelope. 0 if it never touches.
function contactAngle(rc is ValueWithUnits, C is ValueWithUnits, Rc is ValueWithUnits, D is ValueWithUnits) returns ValueWithUnits
{
    const reach = Rc + D / 2;
    var c = (rc * rc + C * C - reach * reach) / (2 * rc * C);
    if (c >= 1)
        return 0 * degree;
    if (c < -1)
        c = -1;
    return acos(c);
}

// Distance along the exit line (from the nip line) at which a ball loses contact with a wheel whose
// centre is a distance a from the nip-line ball centre, measured perpendicular to the exit line.
function sepDist(a is ValueWithUnits, reach is ValueWithUnits) returns ValueWithUnits
{
    if (reach <= a)
        return 0 * MM;
    return sqrt(reach * reach - a * a);
}

// ---- ramp feed helpers. On the floor the ball rolls on two rail edges at |z| = gw (the slot half-width).
function hD(r is ValueWithUnits, gw is ValueWithUnits) returns ValueWithUnits      // ball centre height above the rail-edge line
{
    return sqrt(r * r - gw * gw);
}

function sagOf(r is ValueWithUnits, gw is ValueWithUnits) returns ValueWithUnits   // ball bottom below the rail-edge line
{
    return r - hD(r, gw);
}

function sStep(t is number) returns number                                        // smoothstep on [0, 1]
{
    return 3 * t * t - 2 * t * t * t;
}

function sInv(s is number) returns number                                         // inverse smoothstep on [0, 1]
{
    const c = min(1, max(0, s));
    return 0.5 - sin(asin(1 - 2 * c) / 3);
}

function dirV(a is ValueWithUnits) returns Vector                                 // unit direction at angle a
{
    return vector(cos(a), sin(a));
}

function nrmV(a is ValueWithUnits) returns Vector                                 // left normal of direction a (the ball side)
{
    return vector(-sin(a), cos(a));
}

function tongueR(g is map, t is number) returns ValueWithUnits                    // tongue inner radius at fraction t of the lead arc
{
    return g.Rte - (g.Rte - g.Rh) * sStep(t);
}

// Ball-centre path along the head tongue for ball diameter D, GLOBAL angles (head at g.alpha):
// on the rails until the tongue lifts the ball, resting on the tongue until it reaches the main wheel,
// then squeezed between wheel and tongue (equal split, as elsewhere) up to the hood start.
function tonguePath(g is map, D is ValueWithUnits, n is number) returns map
{
    const r = D / 2;
    const span = g.Rte - g.Rh;
    const gripR = g.Rm + D;
    const tLift = sInv((g.Rte - (g.Rrail + sagOf(r, g.slotHw))) / span);
    const tGrip = sInv((g.Rte - gripR) / span);
    // samples: lift point, 3 steps to the grip point, 5 steps to the hood start (no near-zero segments)
    var ts = [tLift];
    if (tGrip > tLift + 0.005 && tGrip < 0.995)
    {
        for (var k = 1; k <= 3; k += 1)
            ts = append(ts, tLift + (tGrip - tLift) * k / 3);
        for (var k = 1; k <= 5; k += 1)
            ts = append(ts, tGrip + (1 - tGrip) * k / 5);
    }
    else
    {
        for (var k = 1; k <= n; k += 1)
            ts = append(ts, tLift + (1 - tLift) * k / n);
    }
    var pts = [];
    for (var t in ts)
    {
        const rt = tongueR(g, t);
        const rc = rt <= gripR ? (g.Rm + rt) / 2 : rt - r;
        pts = append(pts, pol(rc, g.thc + g.thEL + g.leadArc * t));
    }
    return { "tLift" : tLift, "tGrip" : tGrip, "thLift" : g.thc + g.thEL + g.leadArc * tLift, "thGrip" : g.thc + g.thEL + g.leadArc * tGrip, "pts" : pts };
}

export function pollenGeom(context is Context, alpha is ValueWithUnits, D is ValueWithUnits) returns map
{
    var g = {};
    g.alpha = alpha;
    g.D = D;
    g.Rm = vr(context, "R_main");
    g.Rc = vr(context, "R_ctr");
    g.C = vr(context, "shaft_spacing");
    g.Rh = vr(context, "R_hood_inner");
    g.Cz = g.Rh + g.Rc;                               // C at p = 0 (hood datum): carrier slot centre
    g.thk = vr(context, "hood_thk");
    g.clr = vr(context, "ctr_clear");
    g.adj = vr(context, "adj_travel");
    g.Dmin = vr(context, "D_ball_min");
    g.Dnom = vr(context, "D_ball_nom");
    g.Dmax = vr(context, "D_ball_max");
    g.lead = vr(context, "hood_lead");
    g.Lcorr = vr(context, "L_corridor");
    // The printed hood is fixed to the head while the radial adjuster moves the counter-roller, so the hood
    // is designed once for the whole adjuster range [delta_adj_min, delta_adj_max] (nominal-ball nip values).
    g.dAdjMin = vr(context, "delta_adj_min");
    g.dAdjMax = vr(context, "delta_adj_max");
    g.Ctight = g.Dnom + g.Rm + g.Rc - g.dAdjMax;      // tight stop: smallest C, worst case for the hood end
    g.Cloose = g.Dnom + g.Rm + g.Rc - g.dAdjMin;      // loose stop: largest C
    g.dSet = g.Dnom + g.Rm + g.Rc - g.C;              // current adjuster setting (= delta_nip)
    g.rNip = (g.C + g.Rm - g.Rc) / 2;                 // nip-line ball centre radius (equal split)
    g.rHood = (g.Rm + g.Rh) / 2;                      // hood-locus ball centre radius (equal split)
    g.dNip = D + g.Rm + g.Rc - g.C;                   // nominal nip interference, this ball
    g.dHood = D - (g.Rh - g.Rm);                      // nominal hood interference, this ball
    g.dCtrMax = contactAngle(g.rHood, g.Ctight, g.Rc, g.Dmax);   // D_max at the tight stop
    g.dCtrBall = contactAngle(g.rHood, g.C, g.Rc, D);            // this ball at the current setting
    g.dEnd = g.dCtrMax + vr(context, "hood_end_margin");
    g.thEndL = -g.dEnd;                               // head-local (counter-roller on +X)
    g.thStartL = g.thEndL - vr(context, "hood_arc");
    g.thc = -alpha;                                   // global
    g.thEnd = g.thc + g.thEndL;
    g.thStart = g.thc + g.thStartL;
    g.Cc = pol(g.C, g.thc);
    g.t = vector(sin(alpha), cos(alpha));
    g.n = vector(cos(alpha), -sin(alpha));
    g.Pnip = g.n * g.rNip;
    g.sMain = sepDist(g.rNip, g.Rm + D / 2);
    g.sCtr = sepDist(g.C - g.rNip, g.Rc + D / 2);
    g.sRel = max(g.sMain, g.sCtr);
    g.Prel = g.Pnip + g.t * g.sRel;
    g.sCorr = max(sepDist(g.rNip, g.Rm + g.Dmax / 2), sepDist(g.C - g.rNip, g.Rc + g.Dmax / 2));

    // ---- ramp feed handoff (brief 3.2 / 4): fixed slotted floor + head-mounted tongue ----
    g.feed = vrd(context, "feed_handoff", 1) > 0.5;
    g.beta = vrd(context, "feed_angle", -35 * degree);        // chute direction where it meets the rails (negative = going down)
    g.phiR = vrd(context, "ramp_angle", 20 * degree);         // robot ramp direction (positive = going up toward the shooter)
    g.leadArc = vrd(context, "lead_arc", 20 * degree);        // tongue lead-in arc ahead of the hood start
    g.slotHw = vrd(context, "feed_slot_hw", 10 * MM);         // floor slot half-width: rails at |z| >= this
    g.tongueHw = vrd(context, "tongue_hw", 8 * MM);           // head tongue half-width (runs inside the slot)
    g.Rcr = vrd(context, "crest_R", 50 * MM);
    g.Lch = vrd(context, "chute_L", 40 * MM);
    g.Lramp = vrd(context, "ramp_stub_L", 60 * MM);
    g.tFl = vrd(context, "floor_t", 4 * MM);
    g.tKe = vrd(context, "keel_t", 3 * MM);
    const rMax = g.Dmax / 2;
    const rMin = g.Dmin / 2;
    // rails sit outside the hood, and far enough out that D_max rolling on them clears the main wheel by 1 mm
    g.Rrail = max(g.Rh + g.thk + 1 * MM, g.Rm + rMax + hD(rMax, g.slotHw) + 1 * MM);
    g.sagMax = max(sagOf(rMin, g.slotHw), sagOf(rMax, g.slotHw));
    g.Rte = g.Rrail + g.sagMax + 0.5 * MM;                   // tongue entry: 0.5 mm below the lowest ball bottom on the rails
    g.thEL = g.thStartL - g.leadArc;                         // head-local tongue entry
    g.thE = g.thc + g.thEL;                                  // global tongue entry
    g.thT = g.beta - 90 * degree;                            // global angle where the chute is tangent to the rail arc
    const span = g.Rte - g.Rh;
    const tl0 = sInv((g.Rte - (g.Rrail + sagOf(rMin, g.slotHw) - 0.5 * MM)) / span);
    const tl1 = sInv((g.Rte - (g.Rrail + sagOf(rMax, g.slotHw) - 0.5 * MM)) / span);
    // rails end 3 deg after the tongue has lifted any ball by 0.5 mm at the 5 deg stop (the latest lift)
    g.thFe = -A_MIN + g.thEL + max(tl0, tl1) * g.leadArc + 3 * degree;
    // at the 25 deg stop the tongue tip must stay 2 deg past the end of the chute keel
    g.feedSpare = (-A_MAX + g.thEL) - (g.thT + 2 * degree);
    g.hoodArcMax = vr(context, "hood_arc") + g.feedSpare;
    g.betaMax = g.beta + g.feedSpare;
    g.dB = dirV(g.beta);
    g.nB = nrmV(g.beta);
    g.dR = dirV(g.phiR);
    g.nR = nrmV(g.phiR);
    g.T = pol(g.Rrail, g.thT);                               // chute meets the rails
    g.Pce = g.T - g.dB * g.Lch;                              // crest end / chute start
    g.Ccr = g.Pce - g.nB * g.Rcr;                            // crest centre
    g.Pcs = g.Ccr + g.nR * g.Rcr;                            // crest start / ramp stub end
    g.Prs = g.Pcs - g.dR * g.Lramp;                          // ramp stub start
    g.Rpl = g.Rh + g.thk + 10 * MM;                          // head side plate outer radius
    g.Rtab = g.Rpl + 3 * MM;                                 // feed bracket tabs pass 3 mm outside the head plates
    g.Rbr = g.Rpl + 6.5 * MM;                                // feed bracket outer radius
    return g;
}

// ---------------------------------------------------------------- sketch helpers
function skSectorAt(sk is Sketch, nm is string, c is Vector, r0 is ValueWithUnits, r1 is ValueWithUnits, a0 is ValueWithUnits, a1 is ValueWithUnits)
{
    const am = (a0 + a1) / 2;
    skArc(sk, nm ~ "o", { "start" : c + pol(r1, a0), "mid" : c + pol(r1, am), "end" : c + pol(r1, a1) });
    if (r0 > 0.001 * MM)
    {
        skArc(sk, nm ~ "i", { "start" : c + pol(r0, a0), "mid" : c + pol(r0, am), "end" : c + pol(r0, a1) });
        skLineSegment(sk, nm ~ "a", { "start" : c + pol(r0, a0), "end" : c + pol(r1, a0) });
        skLineSegment(sk, nm ~ "b", { "start" : c + pol(r0, a1), "end" : c + pol(r1, a1) });
    }
    else
    {
        skLineSegment(sk, nm ~ "a", { "start" : c, "end" : c + pol(r1, a0) });
        skLineSegment(sk, nm ~ "b", { "start" : c, "end" : c + pol(r1, a1) });
    }
}

function skPoly(sk is Sketch, nm is string, pts is array)
{
    const n = size(pts);
    for (var i = 0; i < n; i += 1)
    {
        skLineSegment(sk, nm ~ toString(i), { "start" : pts[i], "end" : pts[(i + 1) % n] });
    }
}

function rectPts(c is Vector, u is Vector, a is ValueWithUnits, b is ValueWithUnits) returns array
{
    const p = vector(-u[1], u[0]);
    return [c + u * a + p * b, c - u * a + p * b, c - u * a - p * b, c + u * a - p * b];
}

function hoodPts(g is map, thS is ValueWithUnits, thE is ValueWithUnits) returns map
{
    const Ri = g.Rh;
    const Ro = g.Rh + g.thk;
    const tb = vector(sin(thS), -cos(thS));           // backwards along the travel tangent at thS
    const thm = (thS + thE) / 2;
    return {
            "i0" : pol(Ri, thS) + tb * g.lead,
            "i1" : pol(Ri, thS),
            "im" : pol(Ri, thm),
            "i2" : pol(Ri, thE),
            "o2" : pol(Ro, thE),
            "om" : pol(Ro, thm),
            "o1" : pol(Ro, thS),
            "o0" : pol(Ro, thS) + tb * g.lead
        };
}

function drawHood(sk is Sketch, p is string, g is map, thS is ValueWithUnits, thE is ValueWithUnits, constr is boolean)
{
    const q = hoodPts(g, thS, thE);
    skLineSegment(sk, p ~ "L0", { "start" : q.i0, "end" : q.i1, "construction" : constr });
    skArc(sk, p ~ "Ai", { "start" : q.i1, "mid" : q.im, "end" : q.i2, "construction" : constr });
    skLineSegment(sk, p ~ "E", { "start" : q.i2, "end" : q.o2, "construction" : constr });
    skArc(sk, p ~ "Ao", { "start" : q.o2, "mid" : q.om, "end" : q.o1, "construction" : constr });
    skLineSegment(sk, p ~ "L1", { "start" : q.o1, "end" : q.o0, "construction" : constr });
    skLineSegment(sk, p ~ "L2", { "start" : q.o0, "end" : q.i0, "construction" : constr });
}

// Ramp-feed hood: no straight lead (the head tongue feeds it); the full-width hood opens with a 2.5 mm flare
// over the first 5 deg, so the ball meets it only after the tongue has brought the ball to R_hood_inner.
function drawHoodFeed(sk is Sketch, p is string, g is map, thS is ValueWithUnits, thE is ValueWithUnits, constr is boolean)
{
    const Ro = g.Rh + g.thk;
    const thC = thS + 5 * degree;
    const a = pol(g.Rh + 2.5 * MM, thS);
    skLineSegment(sk, p ~ "F", { "start" : a, "end" : pol(g.Rh, thC), "construction" : constr });
    skArc(sk, p ~ "Ai", { "start" : pol(g.Rh, thC), "mid" : pol(g.Rh, (thC + thE) / 2), "end" : pol(g.Rh, thE), "construction" : constr });
    skLineSegment(sk, p ~ "E", { "start" : pol(g.Rh, thE), "end" : pol(Ro, thE), "construction" : constr });
    skArc(sk, p ~ "Ao", { "start" : pol(Ro, thE), "mid" : pol(Ro, (thS + thE) / 2), "end" : pol(Ro, thS), "construction" : constr });
    skLineSegment(sk, p ~ "S", { "start" : pol(Ro, thS), "end" : a, "construction" : constr });
}

// Tongue profile points, inner (off = 0) or outer (off = hood_thk) surface, from the tip (t = 0) to the hood start (t = 1).
function tonguePts(g is map, thS is ValueWithUnits, off is ValueWithUnits, n is number) returns array
{
    var pts = [];
    for (var i = 0; i <= n; i += 1)
    {
        const t = i / n;
        const rt = i == 0 ? g.Rte : (i == n ? g.Rh : tongueR(g, t));
        const th = i == 0 ? thS - g.leadArc : (i == n ? thS : thS - g.leadArc + g.leadArc * t);
        pts = append(pts, pol(rt + off, th));
    }
    return pts;
}

// Head tongue (printed with the hood, |z| <= tongue_hw): its inner surface falls from R_te (below every ball resting
// on the rails) to R_hood_inner over lead_arc with a smoothstep, then runs 5 deg into the hood.
function drawTongue(sk is Sketch, p is string, g is map, thS is ValueWithUnits, constr is boolean)
{
    const n = 12;
    const Ro = g.Rh + g.thk;
    const thC = thS + 5 * degree;
    const pin = tonguePts(g, thS, 0 * MM, n);
    const pout = tonguePts(g, thS, g.thk, n);
    var rout = [];
    for (var i = n; i >= 0; i -= 1)
        rout = append(rout, pout[i]);
    skFitSpline(sk, p ~ "si", { "points" : pin, "construction" : constr });
    skArc(sk, p ~ "ai", { "start" : pol(g.Rh, thS), "mid" : pol(g.Rh, thS + 2.5 * degree), "end" : pol(g.Rh, thC), "construction" : constr });
    skLineSegment(sk, p ~ "e", { "start" : pol(g.Rh, thC), "end" : pol(Ro, thC), "construction" : constr });
    skArc(sk, p ~ "ao", { "start" : pol(Ro, thC), "mid" : pol(Ro, thS + 2.5 * degree), "end" : pol(Ro, thS), "construction" : constr });
    skFitSpline(sk, p ~ "so", { "points" : rout, "construction" : constr });
    skLineSegment(sk, p ~ "tip", { "start" : pol(g.Rte + g.thk, thS - g.leadArc), "end" : pol(g.Rte, thS - g.leadArc), "construction" : constr });
}

// Side-layout view of the fixed ramp feed: the floor (rail-edge line) and the D_ball centre path into the hood.
function drawFeedLayout(sk is Sketch, p is string, g is map)
{
    const r = g.D / 2;
    const h = hD(r, g.slotHw);
    const am = (g.phiR + g.beta) / 2 + 90 * degree;
    const rho = g.Rrail - h;
    const tp = tonguePath(g, g.D, 8);
    skLineSegment(sk, p ~ "f0", { "start" : g.Prs, "end" : g.Pcs });
    skArc(sk, p ~ "f1", { "start" : g.Pcs, "mid" : g.Ccr + pol(g.Rcr, am), "end" : g.Pce });
    skLineSegment(sk, p ~ "f2", { "start" : g.Pce, "end" : g.T });
    skArc(sk, p ~ "f3", { "start" : g.T, "mid" : pol(g.Rrail, (g.thT + g.thFe) / 2), "end" : pol(g.Rrail, g.thFe) });
    skLineSegment(sk, p ~ "c0", { "start" : g.Prs + g.nR * h, "end" : g.Pcs + g.nR * h, "construction" : true });
    skArc(sk, p ~ "c1", { "start" : g.Pcs + g.nR * h, "mid" : g.Ccr + pol(g.Rcr + h, am), "end" : g.Pce + g.nB * h, "construction" : true });
    skLineSegment(sk, p ~ "c2", { "start" : g.Pce + g.nB * h, "end" : pol(rho, g.thT), "construction" : true });
    if (tp.thLift - g.thT > 0.5 * degree)
        skArc(sk, p ~ "c3", { "start" : pol(rho, g.thT), "mid" : pol(rho, (g.thT + tp.thLift) / 2), "end" : pol(rho, tp.thLift), "construction" : true });
    for (var i = 0; i < size(tp.pts) - 1; i += 1)
        skLineSegment(sk, p ~ "pT" ~ toString(i), { "start" : tp.pts[i], "end" : tp.pts[i + 1], "construction" : true });
    // ball snapshots: on the crest, landing on the rails, lifted by the tongue, gripped by the main wheel
    skCircle(sk, p ~ "b0", { "center" : g.Ccr + pol(g.Rcr + h, am), "radius" : r, "construction" : true });
    skCircle(sk, p ~ "b1", { "center" : pol(rho, g.thT), "radius" : r, "construction" : true });
    skCircle(sk, p ~ "b2", { "center" : tp.pts[0], "radius" : r, "construction" : true });
    skCircle(sk, p ~ "b3", { "center" : pol(g.Rm + r, tp.thGrip), "radius" : r, "construction" : true });
}

function drawLayout(sk is Sketch, p is string, g is map, full is boolean)
{
    const O = vector(0, 0) * MM;
    if (full)
    {
        skCircle(sk, p ~ "main", { "center" : O, "radius" : g.Rm });
        skCircle(sk, p ~ "F", { "center" : O, "radius" : 1.5 * MM, "construction" : true });
    }
    skCircle(sk, p ~ "ctr", { "center" : g.Cc, "radius" : g.Rc });
    skCircle(sk, p ~ "ctrC", { "center" : g.Cc, "radius" : 1.5 * MM, "construction" : true });
    skLineSegment(sk, p ~ "loc", { "start" : O, "end" : g.Cc, "construction" : true });
    skCircle(sk, p ~ "ball", { "center" : g.Pnip, "radius" : g.D / 2 });
    skLineSegment(sk, p ~ "exit", { "start" : g.Pnip, "end" : g.Pnip + g.t * g.Lcorr, "construction" : true });
    skLineSegment(sk, p ~ "vert", { "start" : g.Pnip, "end" : g.Pnip + vector(0 * MM, 150 * MM), "construction" : true });
    if (g.feed)
    {
        drawHoodFeed(sk, p ~ "hd", g, g.thStart, g.thEnd, !full);
        drawTongue(sk, p ~ "tg", g, g.thStart, !full);
    }
    else
        drawHood(sk, p ~ "hd", g, g.thStart, g.thEnd, !full);
    if (full)
    {
        skCircle(sk, p ~ "ctrClr", { "center" : g.Cc, "radius" : g.Rc + g.clr, "construction" : true });
        skArc(sk, p ~ "hdat", { "start" : pol(g.Rh, g.thStart - 15 * degree), "mid" : pol(g.Rh, (g.thStart + g.thc) / 2), "end" : pol(g.Rh, g.thc + 20 * degree), "construction" : true });
        skCircle(sk, p ~ "bmin", { "center" : g.Pnip, "radius" : g.Dmin / 2, "construction" : true });
        skCircle(sk, p ~ "bmax", { "center" : g.Pnip, "radius" : g.Dmax / 2, "construction" : true });
        const e1 = pol(g.rHood, g.thStart);
        if (g.feed)
            drawFeedLayout(sk, p ~ "fd", g);           // ramp, crest, chute, rails, tongue lift and ball snapshots
        else
        {
            const tb = vector(sin(g.thStart), -cos(g.thStart));
            const e0 = e1 + tb * g.lead;
            skLineSegment(sk, p ~ "pathL", { "start" : e0, "end" : e1, "construction" : true });
            skCircle(sk, p ~ "e0", { "center" : e0, "radius" : g.D / 2, "construction" : true });
        }
        skArc(sk, p ~ "pathG", { "start" : e1, "mid" : pol(g.rHood, (g.thStart + g.thEnd) / 2), "end" : pol(g.rHood, g.thEnd), "construction" : true });
        skArc(sk, p ~ "pathU", { "start" : pol(g.rHood, g.thEnd), "mid" : pol(g.rHood, (g.thEnd + g.thc) / 2), "end" : pol(g.rHood, g.thc), "construction" : true });
        // rolling-envelope snapshots: hood start, mid hood, hood end, release, exit
        skCircle(sk, p ~ "e1", { "center" : e1, "radius" : g.D / 2, "construction" : true });
        skCircle(sk, p ~ "e2", { "center" : pol(g.rHood, (g.thStart + g.thEnd) / 2), "radius" : g.D / 2, "construction" : true });
        skCircle(sk, p ~ "e3", { "center" : pol(g.rHood, g.thEnd), "radius" : g.D / 2, "construction" : true });
        skCircle(sk, p ~ "e4", { "center" : g.Prel, "radius" : g.D / 2, "construction" : true });
        skCircle(sk, p ~ "e5", { "center" : g.Pnip + g.t * 150 * MM, "radius" : g.Dmax / 2, "construction" : true });
        skPoint(sk, p ~ "pNip", { "position" : g.Pnip });
        skPoint(sk, p ~ "pRel", { "position" : g.Prel });
        // exit corridor: D_max envelope swept along t from its first no-contact position
        const off = vector(g.t[1], -g.t[0]) * (g.Dmax / 2);
        const c0 = g.Pnip + g.t * g.sCorr;
        const c1 = g.Pnip + g.t * g.Lcorr;
        skLineSegment(sk, p ~ "corA", { "start" : c0 + off, "end" : c1 + off, "construction" : true });
        skLineSegment(sk, p ~ "corB", { "start" : c0 - off, "end" : c1 - off, "construction" : true });
    }
}

function layoutLabels(g is map) returns array
{
    var lines = [
            "alpha_geom = " ~ fdg(g.alpha) ~ " deg FROM VERTICAL (" ~ fdg(90 * degree - g.alpha) ~ " deg above horizontal)",
            "C = " ~ fmm(g.C) ~ " | D_ball = " ~ fmm(g.D) ~ " | delta_nip = " ~ fmm(g.dNip) ~ " | delta_hood = " ~ fmm(g.dHood) ~ " | p = " ~ fmm(g.Cz - g.C) ~ " mm",
            "hood datum R " ~ fmm(g.Rh) ~ " | fixed hood ends " ~ fdg(g.dEnd) ~ " deg before nip line (D_max at tight stop delta_nip " ~ fmm(g.dAdjMax) ~ " meets counter-roller at " ~ fdg(g.dCtrMax) ~ " deg)",
            "this ball meets counter-roller " ~ fdg(g.dCtrBall) ~ " deg before nip | nip ball centre r " ~ fmm(g.rNip) ~ " | release datum " ~ fmm(g.sRel) ~ " mm past nip",
            "geometric exit direction t = (sin a, cos a); measured dynamic exit angle = TBD"
        ];
    if (g.feed)
        lines = append(lines, "ramp feed: ramp up " ~ fdg(g.phiR) ~ " deg, crest R " ~ fmm(g.Rcr) ~ ", chute " ~ fdg(-g.beta) ~ " deg down onto fixed rails R " ~ fmm(g.Rrail) ~ "; head tongue lead " ~ fdg(g.leadArc) ~ " deg; spare at the " ~ fdg(A_MAX) ~ " deg stop " ~ fdg(g.feedSpare) ~ " deg");
    return lines;
}

function addLabels(context is Context, id is Id, pl is Plane, lines is array, at is Vector, h is ValueWithUnits)
{
    try silent
    {
        const sk = newSketchOnPlane(context, id, { "sketchPlane" : pl });
        var i = 0;
        for (var s in lines)
        {
            const p0 = at - vector(0 * MM, h * 1.7 * i);
            const n = size(splitIntoCharacters(s));
            skText(sk, "t" ~ toString(i), { "text" : s, "fontName" : "OpenSans-Regular.ttf", "firstCorner" : p0, "secondCorner" : p0 + vector(h * 0.62 * n, h) });
            i += 1;
        }
        skSolve(sk);
    }
}

// ---------------------------------------------------------------- solid helpers
function extrudeZ(context is Context, id is Id, z0 is ValueWithUnits, z1 is ValueWithUnits, holes is boolean, draw is function) returns Query
{
    const sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : zPlane(0 * MM, z0) });
    draw(sk);
    skSolve(sk);
    opExtrude(context, id + "ex", {
                "entities" : qSketchRegion(id + "sk", holes),
                "direction" : ZAX,
                "endBound" : BoundingType.BLIND,
                "endDepth" : z1 - z0
            });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    return qCreatedBy(id + "ex", EntityType.BODY);
}

function cylZ(context is Context, id is Id, c is Vector, r is ValueWithUnits, z0 is ValueWithUnits, z1 is ValueWithUnits) returns Query
{
    fCylinder(context, id, { "bottomCenter" : W(c[0], c[1], z0), "topCenter" : W(c[0], c[1], z1), "radius" : r });
    return qCreatedBy(id, EntityType.BODY);
}

function ringZ(context is Context, id is Id, c is Vector, r0 is ValueWithUnits, r1 is ValueWithUnits, z0 is ValueWithUnits, z1 is ValueWithUnits) returns Query
{
    return extrudeZ(context, id, z0, z1, true, function(sk is Sketch)
        {
            skCircle(sk, "o", { "center" : c, "radius" : r1 });
            skCircle(sk, "i", { "center" : c, "radius" : r0 });
        });
}

function xCyl(context is Context, id is Id, x0 is ValueWithUnits, x1 is ValueWithUnits, y is ValueWithUnits, z is ValueWithUnits, r is ValueWithUnits) returns Query
{
    fCylinder(context, id, { "bottomCenter" : W(x0, y, z), "topCenter" : W(x1, y, z), "radius" : r });
    return qCreatedBy(id, EntityType.BODY);
}

// Solid sphere (world centre c): half-disc in the world XY plane revolved 360 deg about world Y through c.
// (std fSphere in this version wants a vertex query for its centre, so it is not used.)
function sphereAt(context is Context, id is Id, c is Vector, r is ValueWithUnits) returns Query
{
    const sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(c, vector(0, 0, 1), vector(1, 0, 0)) });
    skArc(sk, "a", { "start" : vector(0 * MM, -r), "mid" : vector(r, 0 * MM), "end" : vector(0 * MM, r) });
    skLineSegment(sk, "l", { "start" : vector(0 * MM, r), "end" : vector(0 * MM, -r) });
    skSolve(sk);
    opRevolve(context, id + "rv", { "entities" : qSketchRegion(id + "sk"), "axis" : line(c, vector(0, 1, 0)), "angleForward" : 360 * degree });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    return qCreatedBy(id + "rv", EntityType.BODY);
}

function capsule(context is Context, id is Id, a is Vector, b is Vector, r is ValueWithUnits) returns Query
{
    fCylinder(context, id + "c", { "bottomCenter" : a, "topCenter" : b, "radius" : r });
    const s0 = sphereAt(context, id + "s0", a, r);
    const s1 = sphereAt(context, id + "s1", b, r);
    const q = qUnion([qCreatedBy(id + "c", EntityType.BODY), s0, s1]);
    opBoolean(context, id + "u", { "tools" : q, "operationType" : BooleanOperationType.UNION });
    return q;
}

function W2(p is Vector) returns Vector                   // brief-plane point (x, y) at z = 0 -> world
{
    return W(p[0], p[1], 0 * MM);
}

// Swept volume of a ball (radius R, centre on a circle of radius rC about the brief-plane point c) moving between
// thFrom and thTo (thTo > thFrom): the revolved disc (torus segment, flat end caps) plus the full ball at each end.
function revolveBallAbout(context is Context, id is Id, c is Vector, rC is ValueWithUnits, R is ValueWithUnits, thFrom is ValueWithUnits, thTo is ValueWithUnits) returns Query
{
    const cw = W2(c);
    const nrm = vector(sin(thTo), 0, -cos(thTo));
    const xd = vector(cos(thTo), 0, sin(thTo));
    const sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(cw, nrm, xd) });
    skCircle(sk, "c", { "center" : vector(rC, 0 * MM), "radius" : R });
    skSolve(sk);
    opRevolve(context, id + "rv", { "entities" : qSketchRegion(id + "sk"), "axis" : line(cw, vector(0, 1, 0)), "angleForward" : thTo - thFrom });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    const s0 = sphereAt(context, id + "e0", W2(c + pol(rC, thFrom)), R);
    const s1 = sphereAt(context, id + "e1", W2(c + pol(rC, thTo)), R);
    const q = qUnion([qCreatedBy(id + "rv", EntityType.BODY), s0, s1]);
    opBoolean(context, id + "u", { "tools" : q, "operationType" : BooleanOperationType.UNION });
    return q;
}

// Same, centred on F.
function revolveBall(context is Context, id is Id, rC is ValueWithUnits, R is ValueWithUnits, thFrom is ValueWithUnits, thTo is ValueWithUnits) returns Query
{
    return revolveBallAbout(context, id, vector(0, 0) * MM, rC, R, thFrom, thTo);
}

function nameIt(context is Context, q is Query, name is string, col is Color, bom is boolean)
{
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.NAME, "value" : name });
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.APPEARANCE, "value" : col });
    if (!bom)
        setProperty(context, { "entities" : q, "propertyType" : PropertyType.EXCLUDE_FROM_BOM, "value" : true });
    // part names cannot be read back during regeneration, so the name is also kept as an attribute
    if (!isQueryEmpty(context, q))
        setAttribute(context, { "entities" : q, "name" : PNAME, "attribute" : name });
}

// Name that nameIt gave this body; "" when it has none.
function pollenNameOf(context is Context, q is Query) returns string
{
    const v = getAttribute(context, { "entity" : q, "name" : PNAME });
    return v is string ? v : "";
}

// armR: radius of the tail arm end (90 mm originally; shorter on the -Z plate when the gear sector is fitted).
// pin: cut the clevis pin hole (only needed without the servo drive).
function buildHeadPlate(context is Context, id is Id, g is map, z0 is ValueWithUnits, z1 is ValueWithUnits, armR is ValueWithUnits, pin is boolean) returns Query
{
    const O = vector(0, 0) * MM;
    const Rpl = g.Rpl;
    const a0 = g.thStartL - 16 * degree;
    const a1 = 30 * degree;
    const td = vector(cos(TAIL), sin(TAIL));
    const Cz = vector(g.Cz, 0 * MM);
    const pcs = [
            extrudeZ(context, id + "sec", z0, z1, false, function(sk is Sketch)
                {
                    skSectorAt(sk, "s", O, 0 * MM, Rpl, a0, a1);
                }),
            cylZ(context, id + "lobe", Cz, 40 * MM, z0, z1),
            cylZ(context, id + "boss", O, 32 * MM, z0, z1),
            cylZ(context, id + "mb", MOTOR_C, 26 * MM, z0, z1),
            extrudeZ(context, id + "arm", z0, z1, false, function(sk is Sketch)
                {
                    skPoly(sk, "a", rectPts(td * (armR / 2), td, armR / 2, 13 * MM));
                }),
            cylZ(context, id + "armE", td * armR, 13 * MM, z0, z1)
        ];
    const plate = qUnion(pcs);
    opBoolean(context, id + "u", { "tools" : plate, "operationType" : BooleanOperationType.UNION });
    const zm = (z0 + z1) / 2;
    var cl = [
            cylZ(context, id + "bore", O, 21 * MM, z0 - MM, z1 + MM),
            extrudeZ(context, id + "slot", z0 - MM, z1 + MM, false, function(sk is Sketch)
                {
                    skPoly(sk, "q", rectPts(Cz, vector(1, 0), 20 * MM + g.adj, 17 * MM));
                }),
            xCyl(context, id + "h1", g.Cz + 20 * MM + g.adj - MM, g.Cz + 44 * MM, 8 * MM, zm, 2.1 * MM),
            xCyl(context, id + "h2", g.Cz + 20 * MM + g.adj - MM, g.Cz + 44 * MM, -8 * MM, zm, 2.1 * MM)
        ];
    if (pin)
        cl = append(cl, cylZ(context, id + "pin", td * 80 * MM, 3 * MM, z0 - MM, z1 + MM));
    opBoolean(context, id + "c", { "tools" : qUnion(cl), "targets" : plate, "operationType" : BooleanOperationType.SUBTRACTION });
    return plate;
}

// holes: centres of 16 mm bearing holes (actuator shafts) in this plate.
function buildFramePlate(context is Context, id is Id, g is map, z0 is ValueWithUnits, z1 is ValueWithUnits, holes is array) returns Query
{
    const O = vector(0, 0) * MM;
    var pcs = [
            cylZ(context, id + "ring", O, 45 * MM, z0, z1),
            extrudeZ(context, id + "rect", z0, z1, false, function(sk is Sketch)
                {
                    skPoly(sk, "r", rectPts(vector(-95, 0) * MM, vector(1, 0), 95 * MM, 80 * MM));
                })
        ];
    if (g.feed)
    {
        // extension down and back that carries the fixed feed floor (side walls and rail-end bracket tabs)
        const x0 = g.Prs[0] - 25 * MM;
        const x1 = g.Rbr * cos(g.thFe) + 10 * MM;
        const y0 = g.Rbr * sin(g.thFe) - 6 * MM;
        const y1 = -30 * MM;
        pcs = append(pcs, extrudeZ(context, id + "ext", z0, z1, false, function(sk is Sketch)
                {
                    skPoly(sk, "e", [vector(x0, y0), vector(x1, y0), vector(x1, y1), vector(x0, y1)]);
                }));
    }
    const plate = qUnion(pcs);
    opBoolean(context, id + "u", { "tools" : plate, "operationType" : BooleanOperationType.UNION });
    var cuts = [cylZ(context, id + "bore", O, 11 * MM, z0 - MM, z1 + MM)];
    for (var i = 0; i < size(holes); i += 1)
        cuts = append(cuts, cylZ(context, id + ("hole" ~ toString(i)), holes[i], 8 * MM, z0 - MM, z1 + MM));
    opBoolean(context, id + "c", { "tools" : qUnion(cuts), "targets" : plate, "operationType" : BooleanOperationType.SUBTRACTION });
    return plate;
}

// Generic standard-size hobby servo envelope (model TBD): case 40 x 20 x 38 with the output shaft 10 mm from the case
// centre, mounting flange 54 x 20 x 2.5 placed 8 mm below the output face. The servo hangs outside the -Z frame plate:
// output face at zOut, frame plate outer face at zPl (zPl > zOut). u = unit vector from the output toward the case
// centre. Returns [case + flange envelope, the 4 standoffs to the frame plate].
function servoEnv(context is Context, id is Id, out is Vector, u is Vector, zOut is ValueWithUnits, zPl is ValueWithUnits) returns array
{
    const cc = out + u * (10 * MM);
    const p = vector(-u[1], u[0]);
    const cs = extrudeZ(context, id + "case", zOut - 38 * MM, zOut, false, function(sk is Sketch)
        {
            skPoly(sk, "c", rectPts(cc, u, 20 * MM, 10 * MM));
        });
    const fl = extrudeZ(context, id + "fl", zOut - 10.5 * MM, zOut - 8 * MM, false, function(sk is Sketch)
        {
            skPoly(sk, "f", rectPts(cc, u, 27 * MM, 10 * MM));
        });
    const env = qUnion([cs, fl]);
    opBoolean(context, id + "u", { "tools" : env, "operationType" : BooleanOperationType.UNION });
    var so = [];
    var k = 0;
    for (var a in [-1, 1])
    {
        for (var b in [-1, 1])
        {
            so = append(so, cylZ(context, id + ("so" ~ toString(k)), cc + u * (a * 24 * MM) + p * (b * 5 * MM), 2.5 * MM, zOut - 8 * MM, zPl));
            k += 1;
        }
    }
    return [env, qUnion(so)];
}

// ---------------------------------------------------------------- features
annotation { "Feature Type Name" : "POLLEN side layout", "Feature Type Description" : "Concept A 2D side-view kinematic layout (brief Phase 1)" }
export const pollenSideLayout = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Use configured alpha", "Default" : true }
        definition.useCfgAlpha is boolean;
        if (!definition.useCfgAlpha)
        {
            annotation { "Name" : "alpha from vertical" }
            isAngle(definition.alpha, ALPHA_BOUNDS);
        }
        annotation { "Name" : "Use configured D_ball", "Default" : true }
        definition.useCfgBall is boolean;
        annotation { "Name" : "Overlay 5 / 15 / 25 deg", "Default" : false }
        definition.overlay is boolean;
        annotation { "Name" : "X offset" }
        isLength(definition.xOffset, OFF_BOUNDS);
        annotation { "Name" : "Sketch plane z (brief frame)" }
        isLength(definition.zOffset, OFF_BOUNDS);
        annotation { "Name" : "Labels", "Default" : true }
        definition.labels is boolean;
    }
    {
        const alpha = definition.useCfgAlpha ? vr(context, "alpha") : definition.alpha;
        const D = definition.useCfgBall ? vr(context, "D_ball") : vr(context, "D_ball_nom");
        const pl = zPlane(definition.xOffset, definition.zOffset);
        const sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : pl });
        var lines = [];
        if (definition.overlay)
        {
            var k = 0;
            for (var a in [5, 15, 25])
            {
                const g = pollenGeom(context, a * degree, D);
                drawLayout(sk, "s" ~ toString(k), g, a == 15);
                k += 1;
            }
            lines = ["OVERLAY alpha = 5 / 15 / 25 deg from vertical, D_ball = " ~ fmm(D) ~ " mm",
                    "rotating the head about F keeps C, delta_nip and the hood-to-roller relation unchanged",
                    "measured dynamic exit angle = TBD"];
        }
        else
        {
            const g = pollenGeom(context, alpha, D);
            drawLayout(sk, "s", g, true);
            lines = layoutLabels(g);
        }
        skSolve(sk);
        if (definition.labels)
            addLabels(context, id + "lbl", pl, lines, vector(-175, -170) * MM, 6 * MM);
    });

annotation { "Feature Type Name" : "POLLEN head A 3D", "Feature Type Description" : "Concept A concentric tilting head: placeholder solids, envelopes and reference bodies (brief Phase 2)" }
export const pollenHeadA3D = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Reference bodies (ball, sweeps, corridor)", "Default" : true }
        definition.refs is boolean;
        annotation { "Name" : "Actuators: angle servo + gear sector, crest gate + servo (placeholders)", "Default" : true }
        definition.actuators is boolean;
        annotation { "Name" : "Crest gate open (releasing a ball)", "Default" : false }
        definition.gateOpen is boolean;
    }
    {
        const alpha = vr(context, "alpha");
        const D = vr(context, "D_ball");
        const g = pollenGeom(context, alpha, D);
        const zl = vr(context, "lane_w") / 2;
        const th = vr(context, "t_head");
        const tf = vr(context, "t_frame");
        const gf = vr(context, "g_frame");
        const zf0 = zl + th + gf;
        const zf1 = zf0 + tf;
        const Wm = vr(context, "W_main");
        const Wc = vr(context, "W_ctr");
        const rs = vr(context, "d_main_shaft") / 2;
        const hard = vr(context, "hardness_ctr");
        const O = vector(0, 0) * MM;
        const Cl = vector(g.C, 0 * MM);
        const BRG = color(0.8, 0.75, 0.4, 1);
        const ENV = color(0.6, 0.3, 0.8, 0.35);
        const ACT = color(0.25, 0.6, 0.35, 1);
        const HW = color(0.3, 0.3, 0.3, 1);
        var head = [];

        // ---- actuator layout (placeholders, all TBD) ----
        const act = definition.actuators;
        const Rs = vrd(context, "ang_sector_R", 100 * MM);            // gear sector pitch radius about F
        const Nr = vrd(context, "ang_ratio", 5);                       // sector : pinion
        const rp = max(Rs / Nr, 6 * MM);                               // pinion pitch radius
        const Pp = pol(Rs + rp, ANG_MESH);                             // pinion centre (frame, fixed)
        const zOut = -zf1 - 8 * MM;                                    // output face of both servos (outside the -Z frame plate)
        var Sg = undefined;                                            // crest gate shaft centre (frame, fixed)
        if (act && g.feed)
        {
            const rMx = g.Dmax / 2;
            Sg = vector(g.Ccr[0] - GATE_DX, g.Ccr[1] + g.Rcr + hD(rMx, g.slotHw) + rMx + GATE_UP);
        }
        var hpN = undefined;                                           // -Z head side plate (carries the gear sector)

        // ---- rotating head: built with the counter-roller on +X, then rotated by -alpha about F ----
        var hood = extrudeZ(context, id + "hood", -zl, zl, false, function(sk is Sketch)
            {
                if (g.feed)
                    drawHoodFeed(sk, "h", g, g.thStartL, g.thEndL, false);
                else
                    drawHood(sk, "h", g, g.thStartL, g.thEndL, false);
            });
        if (g.feed)
        {
            // feed tongue: narrow lead-in printed with the hood; runs inside the fixed floor slot ahead of the hood
            const tongue = extrudeZ(context, id + "tongue", -g.tongueHw, g.tongueHw, false, function(sk is Sketch)
                {
                    drawTongue(sk, "t", g, g.thStartL, false);
                });
            hood = qUnion([hood, tongue]);
            opBoolean(context, id + "tongueU", { "tools" : hood, "operationType" : BooleanOperationType.UNION });
        }
        // relief: counter-roller + ctr_clear swept over the whole radial adjuster range (tight to loose stop)
        const relR = g.Rc + g.clr;
        var rel = [cylZ(context, id + "hoodRel", vector(g.Ctight, 0 * MM), relR, -zl - MM, zl + MM),
                   cylZ(context, id + "hoodRel2", vector(g.Cloose, 0 * MM), relR, -zl - MM, zl + MM)];
        if (g.Cloose - g.Ctight > 0.01 * MM)
            rel = append(rel, extrudeZ(context, id + "hoodRel3", -zl - MM, zl + MM, false, function(sk is Sketch)
                    {
                        skPoly(sk, "r", rectPts(vector((g.Ctight + g.Cloose) / 2, 0 * MM), vector(1, 0), (g.Cloose - g.Ctight) / 2, relR));
                    }));
        try silent
        {
            opBoolean(context, id + "hoodCut", { "tools" : qUnion(rel), "targets" : hood, "operationType" : BooleanOperationType.SUBTRACTION });
        }
        try silent
        {
            opDeleteBodies(context, id + "hoodRelDel", { "entities" : qUnion(rel) });
        }
        nameIt(context, hood, g.feed ? "Hood + feed tongue (printed): R_hood_inner, tongue lifts the ball off the fixed rails, ends before counter-roller contact" : "Hood (printed): R_hood_inner, ends before counter-roller contact", color(0.95, 0.55, 0.1, 1), true);
        head = append(head, hood);

        const ctr = extrudeZ(context, id + "ctr", -Wc / 2, Wc / 2, true, function(sk is Sketch)
            {
                skCircle(sk, "o", { "center" : Cl, "radius" : g.Rc });
                skCircle(sk, "i", { "center" : Cl, "radius" : 7.4 * MM });
            });
        const grey = hard < 40 ? 0.85 : (hard < 52 ? 0.55 : 0.12);
        nameIt(context, ctr, "Counter-roller REV ION Grip 2in " ~ toString(roundToPrecision(hard, 0)) ~ "A (placeholder)", color(grey, grey, grey, 1), true);
        head = append(head, ctr);

        const hexR = 12.7 * MM / sqrt(3);
        var hexPts = [];
        for (var i = 0; i < 6; i += 1)
            hexPts = append(hexPts, Cl + pol(hexR, (30 + 60 * i) * degree));
        const cshaft = extrudeZ(context, id + "cshaft", -zl - th - 3 * MM, zl + th + 18 * MM, false, function(sk is Sketch)
            {
                skPoly(sk, "x", hexPts);
            });
        nameIt(context, cshaft, "Counter shaft 1/2in hex (length TBD)", color(0.85, 0.85, 0.88, 1), true);
        head = append(head, cshaft);

        var mcOwn = {};                                   // owner parts for the assembly mate connectors
        for (var s in [1, -1])
        {
            const sd = s > 0 ? "P" : "N";
            const nm = s > 0 ? " +Z (drive side)" : " -Z";
            const z0 = s > 0 ? zl : -zl - th;
            const z1 = z0 + th;
            const zm = (z0 + z1) / 2;
            // with the gear sector the -Z tail arm stops 3 mm inside the sector pitch circle, clear of the pinion
            const armR = (act && s < 0) ? Rs - 16 * MM : 90 * MM;
            const hp = buildHeadPlate(context, id + ("hp" ~ sd), g, z0, z1, armR, !act);
            nameIt(context, hp, "Head side plate" ~ nm ~ " (pivots about F)", color(0.2, 0.45, 0.85, 1), true);
            if (s < 0)
                hpN = hp;
            const car = extrudeZ(context, id + ("car" ~ sd), z0, z1, true, function(sk is Sketch)
                {
                    skPoly(sk, "r", rectPts(Cl, vector(1, 0), 20 * MM, 16.95 * MM));
                    skCircle(sk, "b", { "center" : Cl, "radius" : 14.29 * MM });
                });
            nameIt(context, car, "Counter carrier" ~ nm ~ " (radial-only slide, lockable)", color(0.35, 0.65, 0.95, 1), true);
            const brg = ringZ(context, id + ("cb" ~ sd), Cl, 7.4 * MM, 14.29 * MM, z0, z1);
            nameIt(context, brg, "Counter bearing 1/2in hex x 1.125in OD" ~ nm ~ " (TBD)", BRG, true);
            const pb = ringZ(context, id + ("pb" ~ sd), O, 15 * MM, 21 * MM, z0, z1);
            nameIt(context, pb, "Head pivot bearing 30x42" ~ nm ~ " (TBD)", BRG, true);
            const sc1 = xCyl(context, id + ("sa" ~ sd), g.C + 20 * MM, g.Cz + 46 * MM, 8 * MM, zm, 2 * MM);
            const sc2 = xCyl(context, id + ("sb" ~ sd), g.C + 20 * MM, g.Cz + 46 * MM, -8 * MM, zm, 2 * MM);
            nameIt(context, sc1, "Radial adjuster push screw" ~ nm ~ " (TBD)", color(0.3, 0.3, 0.3, 1), true);
            nameIt(context, sc2, "Radial adjuster pull/lock screw" ~ nm ~ " (TBD)", color(0.3, 0.3, 0.3, 1), true);
            head = concatenateArrays([head, [hp, car, brg, pb, sc1, sc2]]);
            if (s > 0)
            {
                mcOwn.head = hp;
                mcOwn.car = car;
            }
        }

        const gIn = g.Rc + g.clr + g.adj;
        const cg = extrudeZ(context, id + "cg", -zl, zl, false, function(sk is Sketch)
            {
                skSectorAt(sk, "g", vector(g.Cz, 0 * MM), gIn, gIn + 3 * MM, -95 * degree, 95 * degree);
            });
        nameIt(context, cg, "Counter-roller guard (head-mounted)", color(0.95, 0.85, 0.1, 1), true);
        const cm = cylZ(context, id + "cm", MOTOR_C, 19 * MM, zl + th, zl + th + 70 * MM);
        nameIt(context, cm, "ENVELOPE counter-roller motor (TBD)", ENV, false);
        const cp = ringZ(context, id + "cp", Cl, 7.4 * MM, 15 * MM, zl + th + 2 * MM, zl + th + 14 * MM);
        nameIt(context, cp, "ENVELOPE counter pulley/belt (TBD)", ENV, false);
        head = concatenateArrays([head, [cg, cm, cp]]);
        if (!act)
        {
            const ap = cylZ(context, id + "ap", vector(cos(TAIL), sin(TAIL)) * 80 * MM, 2.9 * MM, zl - 8 * MM, zl + th);
            nameIt(context, ap, "Actuator interface: clevis pin on tail arm (actuator TBD)", HW, true);
            head = append(head, ap);
        }
        else
        {
            // angle drive, head side: gear sector web on the -Z head plate layer, from the tail arm (TAIL) to 7 deg past
            // the mesh point at the 25 deg stop; teeth on the pitch circle ang_sector_R about F (0.5 mm modelled gap)
            const sec = extrudeZ(context, id + "gsec", -zl - th, -zl, false, function(sk is Sketch)
                {
                    skSectorAt(sk, "g", O, 28 * MM, Rs - 0.25 * MM, TAIL, ANG_MESH + A_MAX + 7 * degree);
                });
            opBoolean(context, id + "gsecC", { "tools" : hpN, "targets" : sec, "operationType" : BooleanOperationType.SUBTRACTION, "keepTools" : true });
            nameIt(context, sec, "Angle gear sector, pitch R " ~ fmm(Rs) ~ " about F (teeth, module, material TBD), bolted to head side plate -Z", ACT, true);
            head = append(head, sec);
        }

        var swHeadOk = !g.feed;
        if (definition.refs)
        {
            const rb = sphereAt(context, id + "rb", W(g.rNip, 0 * MM, 0 * MM), D / 2);
            nameIt(context, rb, "REF ball at nip line (D_ball, undeformed)", color(1, 0.85, 0, 0.6), false);
            var refs = [rb];
            if (!g.feed)
            {
                // straight-lead feed: the sweep is head-local and rotates with the head
                const sw1 = revolveBall(context, id + "sw1", g.rHood, D / 2, g.thStartL, g.thEndL);
                const tb = vector(sin(g.thStartL), -cos(g.thStartL));
                const e1 = pol(g.rHood, g.thStartL);
                const e0 = e1 + tb * g.lead;
                const sw1b = capsule(context, id + "sw1b", W(e0[0], e0[1], 0 * MM), W(e1[0], e1[1], 0 * MM), D / 2);
                const swA = qUnion([sw1, sw1b]);
                opBoolean(context, id + "sw1u", { "tools" : swA, "operationType" : BooleanOperationType.UNION });
                nameIt(context, swA, "REF ball sweep feed entry to hood end (D_ball)", color(1, 0.85, 0, 0.25), false);
                refs = append(refs, swA);
            }
            else
            {
                // ramp feed: the tongue-lift-to-hood-end part of the sweep is rigid with the head, so it is built
                // head-local and rotates with the head (the fixed ramp-to-rails part is built later in frame coordinates)
                var gl = g;
                gl.thc = 0 * degree;
                const tpl = tonguePath(gl, D, 8);
                try silent
                {
                    var sh = [revolveBall(context, id + "sw1", g.rHood, D / 2, g.thStartL, g.thEndL)];
                    for (var i = 0; i < size(tpl.pts) - 1; i += 1)
                    {
                        if (norm(tpl.pts[i + 1] - tpl.pts[i]) > 0.05 * MM)
                            sh = append(sh, capsule(context, id + "sw1" + ("t" ~ toString(i)), W2(tpl.pts[i]), W2(tpl.pts[i + 1]), D / 2));
                    }
                    const swA = qUnion(sh);
                    opBoolean(context, id + "sw1u", { "tools" : swA, "operationType" : BooleanOperationType.UNION });
                    nameIt(context, swA, "REF ball sweep feed, head part: tongue lift to hood end (D_ball)", color(1, 0.85, 0, 0.25), false);
                    refs = append(refs, swA);
                    swHeadOk = true;
                }
                if (!swHeadOk)
                {
                    try silent
                    {
                        opDeleteBodies(context, id + "sw1Del", { "entities" : qCreatedBy(id + "sw1", EntityType.BODY) });
                    }
                }
            }
            const swB = revolveBall(context, id + "sw2", g.rHood, D / 2, g.thEndL, 0 * degree);
            nameIt(context, swB, "REF ball sweep hood end to nip, unguided (D_ball)", color(1, 0.5, 0, 0.25), false);
            const cor = capsule(context, id + "cor", W(g.rNip, g.sCorr + 1 * MM, 0 * MM), W(g.rNip, g.Lcorr, 0 * MM), g.Dmax / 2);
            nameIt(context, cor, "REF exit corridor (D_max envelope)", color(0.2, 0.8, 0.3, 0.25), false);
            head = concatenateArrays([head, refs, [swB, cor]]);
        }

        opTransform(context, id + "rot", { "bodies" : qUnion(head), "transform" : rotationAround(line(ORIGIN, ZAX), -alpha) });

        // ---- part-owned mate connectors for the motion assembly (no geometry) ----
        // Pivot connectors: origin on the main axis, Z = world +Y (brief -Z), X = counter-roller direction, so a
        // revolute mate from the frame connector to the head connector reads +alpha.
        // Radial connectors: Z points inward along the counter-roller direction; the head one sits at the
        // zero-squeeze centre distance D_nom + R_main + R_ctr, so a slider from head to carrier reads delta_nip.
        const radW = vector(cos(alpha), 0, -sin(alpha));
        const C0 = g.Dnom + g.Rm + g.Rc;
        opMateConnector(context, id + "mcHeadPivot", { "coordSystem" : coordSystem(ORIGIN, radW, vector(0, 1, 0)), "owner" : mcOwn.head });
        opMateConnector(context, id + "mcHeadRadial", { "coordSystem" : coordSystem(radW * C0, vector(0, 1, 0), -radW), "owner" : mcOwn.head });
        opMateConnector(context, id + "mcCarrier", { "coordSystem" : coordSystem(radW * g.C, vector(0, 1, 0), -radW), "owner" : mcOwn.car });

        // ---- fixed frame (does not rotate) ----
        const mw = ringZ(context, id + "mw", O, rs, g.Rm, -Wm / 2, Wm / 2);
        nameIt(context, mw, "Main flywheel goBILDA 96mm Hogback 50A (placeholder, width TBD)", color(0.12, 0.12, 0.12, 1), true);
        const ms = cylZ(context, id + "ms", O, rs, -zf1 - 5 * MM, zf1 + 30 * MM);
        nameIt(context, ms, "Main shaft (interface TBD)", color(0.85, 0.85, 0.88, 1), true);
        for (var s in [1, -1])
        {
            const sd = s > 0 ? "P" : "N";
            const nm = s > 0 ? " +Z (drive side)" : " -Z";
            const z0 = s > 0 ? zf0 : -zf1;
            const z1 = z0 + tf;
            var hl = [];
            if (act && s < 0)
                hl = append(hl, Pp);
            if (Sg != undefined)
                hl = append(hl, Sg);
            const fp = buildFramePlate(context, id + ("fp" ~ sd), g, z0, z1, hl);
            nameIt(context, fp, "Frame side plate" ~ nm ~ " (fixed, mounts to robot)", color(0.7, 0.7, 0.72, 1), true);
            const mb = ringZ(context, id + ("mb" ~ sd), O, rs, 11 * MM, z0, z1);
            nameIt(context, mb, "Main shaft bearing" ~ nm ~ " (TBD)", BRG, true);
            const hz0 = s > 0 ? zl : -zf0;
            const hub = ringZ(context, id + ("hub" ~ sd), O, 7 * MM, 15 * MM, hz0, hz0 + (zf0 - zl));
            nameIt(context, hub, "Pivot hub" ~ nm ~ " (fixed, coaxial with main shaft, carries head)", color(0.55, 0.55, 0.6, 1), true);
            if (s > 0)
                mcOwn.hub = hub;
        }
        opMateConnector(context, id + "mcFramePivot", { "coordSystem" : coordSystem(ORIGIN, vector(1, 0, 0), vector(0, 1, 0)), "owner" : mcOwn.hub });
        const stops = [[A_MIN, 1, "Hard stop alpha = " ~ fdg(A_MIN) ~ " deg"], [A_MAX, -1, "Hard stop alpha = " ~ fdg(A_MAX) ~ " deg"]];
        var k = 0;
        for (var st in stops)
        {
            const ang = TAIL - st[0];
            const u = vector(cos(ang), sin(ang));
            const nL = vector(-u[1], u[0]);
            const c = u * 75 * MM + nL * (st[1] * 18 * MM);
            const sb = extrudeZ(context, id + ("st" ~ toString(k)), zl, zf0, false, function(sk is Sketch)
                {
                    skPoly(sk, "b", rectPts(c, u, 9 * MM, 5 * MM));
                });
            nameIt(context, sb, st[2] ~ " (on frame plate +Z)", color(0.85, 0.15, 0.15, 1), true);
            k += 1;
        }
        const enc = ringZ(context, id + "enc", O, 15.5 * MM, 28 * MM, zl + th + 1 * MM, zf0 - 1 * MM);
        nameIt(context, enc, "ENVELOPE angle encoder allowance on pivot (TBD)", ENV, false);
        // with the ramp feed the guard stops short of the chute (ball path)
        const gEnd = g.feed ? min(210 * degree, g.thT + 325 * degree) : 210 * degree;
        const mg = extrudeZ(context, id + "mg", -Wm / 2 - 5 * MM, Wm / 2 + 5 * MM, false, function(sk is Sketch)
            {
                skSectorAt(sk, "g", O, g.Rm + 6 * MM, g.Rm + 9 * MM, 50 * degree, gEnd);
            });
        nameIt(context, mg, "Main-wheel guard (fixed, mounts TBD)", color(0.95, 0.85, 0.1, 1), true);
        const mm = cylZ(context, id + "mm", vector(-120, 45) * MM, 19 * MM, zf1, zf1 + 70 * MM);
        nameIt(context, mm, "ENVELOPE main motor (TBD)", ENV, false);
        const mp = ringZ(context, id + "mp", O, rs, 20 * MM, zf1 + 3 * MM, zf1 + 15 * MM);
        nameIt(context, mp, "ENVELOPE main pulley/belt (TBD)", ENV, false);

        // ---- angle drive, frame side (placeholders, all TBD): servo -> coupler -> shaft -> pinion -> gear sector ----
        if (act)
        {
            const pin = ringZ(context, id + "pinion", Pp, 4 * MM, rp - 0.25 * MM, -zl - th, -zl);
            nameIt(context, pin, "Angle pinion, pitch R " ~ fmm(rp) ~ " (teeth, module, material TBD), on the angle servo shaft", ACT, true);
            const psh = cylZ(context, id + "psh", Pp, 4 * MM, zOut, -zl);
            nameIt(context, psh, "Angle drive shaft 8 mm (TBD): servo coupler to pinion", color(0.85, 0.85, 0.88, 1), true);
            const pbr = ringZ(context, id + "pbr", Pp, 4 * MM, 8 * MM, -zf1, -zf0);
            nameIt(context, pbr, "Angle shaft bearing 8x16 in frame plate -Z (TBD)", BRG, true);
            const pcp = ringZ(context, id + "pcp", Pp, 4 * MM, 7 * MM, zOut, zOut + 6 * MM);
            nameIt(context, pcp, "Servo coupler, angle servo (servo spline to 8 mm shaft, TBD)", HW, true);
            const asv = servoEnv(context, id + "asv", Pp, -dirV(ANG_MESH), zOut, -zf1);
            nameIt(context, asv[0], "ENVELOPE angle servo, standard size (model, torque, travel TBD)", ENV, false);
            nameIt(context, asv[1], "Servo standoffs (4) to frame plate -Z, angle servo (TBD)", HW, true);
        }

        // ---- fixed ramp feed floor (frame, does not rotate): ramp stub, convex crest, chute, slotted transfer rails ----
        var swOk = false;
        if (g.feed)
        {
            const zr = zl - 2 * MM;                                   // floor half-width; side walls outside this
            const fT = g.tFl;
            const kT = g.tKe;
            const am = (g.phiR + g.beta) / 2 + 90 * degree;
            // closed strip along ramp -> crest -> chute between offsets o0 < o1 from the rail-edge line (+ = ball side)
            const band = function(sk is Sketch, nm is string, o0 is ValueWithUnits, o1 is ValueWithUnits)
                {
                    skLineSegment(sk, nm ~ "a", { "start" : g.Prs + g.nR * o1, "end" : g.Pcs + g.nR * o1 });
                    skArc(sk, nm ~ "b", { "start" : g.Pcs + g.nR * o1, "mid" : g.Ccr + pol(g.Rcr + o1, am), "end" : g.Pce + g.nB * o1 });
                    skLineSegment(sk, nm ~ "c", { "start" : g.Pce + g.nB * o1, "end" : g.T + g.nB * o1 });
                    skLineSegment(sk, nm ~ "d", { "start" : g.T + g.nB * o1, "end" : g.T + g.nB * o0 });
                    skLineSegment(sk, nm ~ "e", { "start" : g.T + g.nB * o0, "end" : g.Pce + g.nB * o0 });
                    skArc(sk, nm ~ "f", { "start" : g.Pce + g.nB * o0, "mid" : g.Ccr + pol(g.Rcr + o0, am), "end" : g.Pcs + g.nR * o0 });
                    skLineSegment(sk, nm ~ "g", { "start" : g.Pcs + g.nR * o0, "end" : g.Prs + g.nR * o0 });
                    skLineSegment(sk, nm ~ "h", { "start" : g.Prs + g.nR * o0, "end" : g.Prs + g.nR * o1 });
                };
            // rail: floor_t thick under the rail-edge line, from the ramp stub start to the rail end (past the tongue lift)
            const rail = function(sk is Sketch)
                {
                    const pE = pol(g.Rrail, g.thFe);
                    const pEo = pol(g.Rrail + fT, g.thFe);
                    const pTo = pol(g.Rrail + fT, g.thT);
                    const thM = (g.thT + g.thFe) / 2;
                    skLineSegment(sk, "a", { "start" : g.Prs, "end" : g.Pcs });
                    skArc(sk, "b", { "start" : g.Pcs, "mid" : g.Ccr + pol(g.Rcr, am), "end" : g.Pce });
                    skLineSegment(sk, "c", { "start" : g.Pce, "end" : g.T });
                    skArc(sk, "d", { "start" : g.T, "mid" : pol(g.Rrail, thM), "end" : pE });
                    skLineSegment(sk, "e", { "start" : pE, "end" : pEo });
                    skArc(sk, "f", { "start" : pEo, "mid" : pol(g.Rrail + fT, thM), "end" : pTo });
                    skLineSegment(sk, "g", { "start" : pTo, "end" : g.Pce - g.nB * fT });
                    skArc(sk, "h", { "start" : g.Pce - g.nB * fT, "mid" : g.Ccr + pol(g.Rcr - fT, am), "end" : g.Pcs - g.nR * fT });
                    skLineSegment(sk, "i", { "start" : g.Pcs - g.nR * fT, "end" : g.Prs - g.nR * fT });
                    skLineSegment(sk, "j", { "start" : g.Prs - g.nR * fT, "end" : g.Prs });
                };
            // rail-end bracket: radial strip r0..r1, 10 mm wide, flush with the rail end
            const uF = vector(cos(g.thFe), sin(g.thFe));
            const tF = vector(-sin(g.thFe), cos(g.thFe));
            const brk = function(r0 is ValueWithUnits, r1 is ValueWithUnits)
                {
                    return rectPts(uF * ((r0 + r1) / 2) - tF * (5 * MM), uF, (r1 - r0) / 2, 5 * MM);
                };
            const rW = g.Rrail + fT - 1 * MM;
            const fl = [
                    extrudeZ(context, id + "flRp", g.slotHw, zr, false, rail),
                    extrudeZ(context, id + "flRn", -zr, -g.slotHw, false, rail),
                    extrudeZ(context, id + "flK", -zr, zr, false, function(sk is Sketch) { band(sk, "k", -(fT + kT), -fT); }),
                    extrudeZ(context, id + "flWp", zr, zf0, false, function(sk is Sketch) { band(sk, "w", -(fT + kT), WALL_H); }),
                    extrudeZ(context, id + "flWn", -zf0, -zr, false, function(sk is Sketch) { band(sk, "w", -(fT + kT), WALL_H); }),
                    extrudeZ(context, id + "flBp", g.slotHw, zr, false, function(sk is Sketch) { skPoly(sk, "b", brk(rW, g.Rbr)); }),
                    extrudeZ(context, id + "flBn", -zr, -g.slotHw, false, function(sk is Sketch) { skPoly(sk, "b", brk(rW, g.Rbr)); }),
                    extrudeZ(context, id + "flTp", zr, zf0, false, function(sk is Sketch) { skPoly(sk, "b", brk(g.Rtab, g.Rbr)); }),
                    extrudeZ(context, id + "flTn", -zf0, -zr, false, function(sk is Sketch) { skPoly(sk, "b", brk(g.Rtab, g.Rbr)); })
                ];
            const flr = qUnion(fl);
            opBoolean(context, id + "flU", { "tools" : flr, "operationType" : BooleanOperationType.UNION });
            nameIt(context, flr, "Feed floor (printed, fixed): ramp stub, crest, chute, slotted transfer rails, rail-end bracket (mounts TBD)", color(0.3, 0.75, 0.75, 1), true);

            // REF ball sweep, fixed part (frame coordinates, the same at every alpha): ramp, crest, chute, and the rails
            // up to where the tongue lifts the ball at the A_MIN stop (the latest lift). At larger alpha the tongue
            // lifts the ball earlier, so this envelope overlaps the head part there.
            if (definition.refs)
            {
                const fw = id + "fw";
                const rB = D / 2;
                const hB = hD(rB, g.slotHw);
                const rho = g.Rrail - hB;
                var g5 = g;
                g5.thc = -A_MIN;
                const thLift5 = tonguePath(g5, D, 8).thLift;
                try silent
                {
                    var sw = [
                            capsule(context, fw + "ramp", W2(g.Prs + g.nR * hB), W2(g.Pcs + g.nR * hB), rB),
                            revolveBallAbout(context, fw + "crest", g.Ccr, g.Rcr + hB, rB, g.beta + 90 * degree, g.phiR + 90 * degree),
                            capsule(context, fw + "chute", W2(g.Pce + g.nB * hB), W2(pol(rho, g.thT)), rB)
                        ];
                    if (thLift5 - g.thT > 0.2 * degree)
                        sw = append(sw, revolveBall(context, fw + "rail", rho, rB, g.thT, thLift5));
                    const swq = qUnion(sw);
                    opBoolean(context, id + "fwU", { "tools" : swq, "operationType" : BooleanOperationType.UNION });
                    nameIt(context, swq, "REF ball sweep feed, fixed part: ramp, crest, chute, rails to the latest tongue lift (D_ball)", color(1, 0.85, 0, 0.25), false);
                    swOk = true;
                }
                if (!swOk)
                {
                    try silent
                    {
                        opDeleteBodies(context, id + "fwDel", { "entities" : qCreatedBy(fw, EntityType.BODY) });
                    }
                }
            }
        }

        // ---- crest gate ("flapper", placeholders, all TBD): a flap on a cross shaft just upstream of the crest apex.
        // Closed (hanging down) it holds the next ball on the ramp; the servo swings it gate_swing with the flow (up and
        // downstream) to let one ball over the crest. The ball pushes the closed flap toward open, so the servo holds it.
        const gSwing = vrd(context, "gate_swing", 90 * degree);
        if (Sg != undefined)
        {
            const dxF = Sg[0] - g.Ccr[0];
            const yFl = g.Ccr[1] + sqrt(g.Rcr * g.Rcr - dxF * dxF);  // crest floor under the shaft
            const Lf = Sg[1] - (yFl + 6 * MM);                        // flap tip 6 mm above the floor
            const fb = extrudeZ(context, id + "gflap", -16 * MM, 16 * MM, false, function(sk is Sketch)
                {
                    skPoly(sk, "f", rectPts(vector(Sg[0], Sg[1] - (Lf + 5.5 * MM) / 2), vector(0, 1), (Lf - 5.5 * MM) / 2, 1.5 * MM));
                });
            const flap = qUnion([fb, cylZ(context, id + "ghub", Sg, 7 * MM, -16 * MM, 16 * MM)]);
            opBoolean(context, id + "gflapU", { "tools" : flap, "operationType" : BooleanOperationType.UNION });
            opBoolean(context, id + "gflapB", { "tools" : cylZ(context, id + "gbore", Sg, 4 * MM, -17 * MM, 17 * MM), "targets" : flap, "operationType" : BooleanOperationType.SUBTRACTION });
            if (definition.gateOpen)
                opTransform(context, id + "gateRot", { "bodies" : flap, "transform" : rotationAround(line(W2(Sg), ZAX), gSwing) });
            nameIt(context, flap, "Crest gate flap (printed, TBD): " ~ (definition.gateOpen ? "OPEN, swung " ~ fdg(gSwing) ~ " deg" : "CLOSED, holds the next ball"), color(0.85, 0.2, 0.55, 1), true);
            const gsh = cylZ(context, id + "gsh", Sg, 4 * MM, zOut, zf1);
            nameIt(context, gsh, "Gate shaft 8 mm (TBD), through both frame plates", color(0.85, 0.85, 0.88, 1), true);
            const gbP = ringZ(context, id + "gbP", Sg, 4 * MM, 8 * MM, zf0, zf1);
            nameIt(context, gbP, "Gate shaft bearing 8x16 in frame plate +Z (TBD)", BRG, true);
            const gbN = ringZ(context, id + "gbN", Sg, 4 * MM, 8 * MM, -zf1, -zf0);
            nameIt(context, gbN, "Gate shaft bearing 8x16 in frame plate -Z (TBD)", BRG, true);
            const gcp = ringZ(context, id + "gcp", Sg, 4 * MM, 7 * MM, zOut, zOut + 6 * MM);
            nameIt(context, gcp, "Servo coupler, gate servo (servo spline to 8 mm shaft, TBD)", HW, true);
            const gsv = servoEnv(context, id + "gsv", Sg, vector(-1, 0), zOut, -zf1);
            nameIt(context, gsv[0], "ENVELOPE gate servo, standard size (model TBD)", ENV, false);
            nameIt(context, gsv[1], "Servo standoffs (4) to frame plate -Z, gate servo (TBD)", HW, true);
        }

        var warn = "";
        if (alpha < A_MIN - 0.01 * degree || alpha > A_MAX + 0.01 * degree)
            warn = warn ~ "alpha " ~ fdg(alpha) ~ " deg is outside the hard stops " ~ fdg(A_MIN) ~ " to " ~ fdg(A_MAX) ~ " deg. ";
        if (g.feed && g.feedSpare < 0 * degree)
            warn = warn ~ "Ramp feed: at the " ~ fdg(A_MAX) ~ " deg stop the head tongue reaches the chute keel (short by " ~ fdg(-g.feedSpare) ~ " deg). Use hood_arc <= " ~ fdg(g.hoodArcMax) ~ " deg or feed_angle <= " ~ fdg(g.betaMax) ~ " deg. ";
        if (g.feed && definition.refs && !swOk)
            warn = warn ~ "Ramp feed: the fixed part of the REF ball sweep could not be built. ";
        if (g.feed && definition.refs && !swHeadOk)
            warn = warn ~ "Ramp feed: the head part of the REF ball sweep could not be built. ";
        if (g.dSet < g.dAdjMin - 0.001 * MM || g.dSet > g.dAdjMax + 0.001 * MM)
            warn = warn ~ "delta_nip " ~ fmm(g.dSet) ~ " is outside the adjuster stops " ~ fmm(g.dAdjMin) ~ " to " ~ fmm(g.dAdjMax) ~ " mm; the fixed hood is not designed for it. ";
        if (act && Rs / Nr < 6 * MM)
            warn = warn ~ "Angle drive: ang_sector_R / ang_ratio is under 6 mm, so the pinion is drawn at 6 mm pitch radius. ";
        if (act && (A_MAX - A_MIN) * Nr > 180 * degree)
            warn = warn ~ "Angle drive: the servo needs " ~ fdg((A_MAX - A_MIN) * Nr) ~ " deg of travel for alpha " ~ fdg(A_MIN) ~ " to " ~ fdg(A_MAX) ~ " deg; check the servo's range (TBD). ";
        if (act && !g.feed)
            warn = warn ~ "Crest gate not built: it needs the ramp feed (feed_handoff = 1). ";
        var msg = "alpha " ~ fdg(alpha) ~ " deg from vertical | C " ~ fmm(g.C) ~ " | setting delta_nip " ~ fmm(g.dSet) ~ " (this ball " ~ fmm(g.dNip) ~ ") | fixed hood ends " ~ fdg(g.dEnd) ~ " deg before nip | release datum " ~ fmm(g.sRel) ~ " mm past nip";
        if (g.feed)
            msg = msg ~ " | ramp feed: chute " ~ fdg(-g.beta) ~ " deg down onto fixed rails R " ~ fmm(g.Rrail) ~ ", tongue lead " ~ fdg(g.leadArc) ~ " deg, spare at the " ~ fdg(A_MAX) ~ " deg stop " ~ fdg(g.feedSpare) ~ " deg";
        if (act)
            msg = msg ~ " | angle drive (TBD): servo -> pinion R " ~ fmm(rp) ~ " -> gear sector R " ~ fmm(Rs) ~ " on head plate -Z, " ~ toString(roundToPrecision(Rs / rp, 2)) ~ ":1, servo turns " ~ fdg((A_MAX - A_MIN) * Rs / rp) ~ " deg for alpha " ~ fdg(A_MIN) ~ " to " ~ fdg(A_MAX) ~ " deg";
        if (Sg != undefined)
            msg = msg ~ " | crest gate " ~ (definition.gateOpen ? "OPEN (swung " ~ fdg(gSwing) ~ " deg)" : "CLOSED (holds the next ball)");
        if (warn != "")
            reportFeatureWarning(context, id, warn ~ msg);
        else
            reportFeatureInfo(context, id, msg);
    });

// Checks every pair of real (non-REF) solids for clashes and measures the actuator clearances at the current
// configuration. ABUT rows are contacts (fastened or bearing faces); every other collision row is an overlap.
// Slow: suppress it after reading the result (feature info, or the FeatureScript console).
annotation { "Feature Type Name" : "POLLEN clearance check", "Feature Type Description" : "Clashes between real parts and actuator clearances at the current configuration (suppress after reading; slow)" }
export const pollenClearanceCheck = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Also list contacts (ABUT)", "Default" : false }
        definition.listAbut is boolean;
    }
    {
        const solids = evaluateQuery(context, qBodyType(qEverything(EntityType.BODY), BodyType.SOLID));
        var nm = [];
        for (var b in solids)
            nm = append(nm, pollenNameOf(context, b));
        var non = [];
        var unnamed = 0;
        for (var i = 0; i < size(solids); i += 1)
        {
            if (nm[i] == "")
                unnamed += 1;
            else if (!match(nm[i], "REF.*").hasMatch)
                non = append(non, i);
        }
        var bad = [];
        var abut = [];
        for (var a = 0; a < size(non); a += 1)
        {
            var tg = [];
            for (var k = a + 1; k < size(non); k += 1)
                tg = append(tg, solids[non[k]]);
            var seen = {};
            if (size(tg) > 0)
            {
                for (var c in evCollision(context, { "tools" : solids[non[a]], "targets" : qUnion(tg) }))
                {
                    const ty = toString(c["type"]);
                    const row = ty ~ ": " ~ nm[non[a]] ~ " <-> " ~ pollenNameOf(context, c.targetBody);
                    if (seen[row] == undefined)
                    {
                        seen[row] = true;
                        if (match(ty, "ABUT.*").hasMatch)
                            abut = append(abut, row);
                        else
                            bad = append(bad, row);
                    }
                }
            }
        }
        // named minimum distances (mm); a side is the union of the solids whose names match any of its patterns
        const pick = function(res is array)
            {
                var q = [];
                for (var i = 0; i < size(solids); i += 1)
                {
                    var hit = false;
                    for (var re in res)
                    {
                        if (match(nm[i], re).hasMatch)
                            hit = true;
                    }
                    if (hit)
                        q = append(q, solids[i]);
                }
                return q;
            };
        const pairs = [
                ["sector-pinion", ["Angle gear sector.*"], ["Angle pinion.*"]],
                ["headPlateN-pinion", ["Head side plate -Z.*"], ["Angle pinion.*"]],
                ["sector-frame", ["Angle gear sector.*"], ["Frame side plate.*", "Pivot hub.*", "Main-wheel guard.*", "Main shaft.*", "Main flywheel.*", "Feed floor.*"]],
                ["flap-guard", ["Crest gate flap.*"], ["Main-wheel guard.*"]],
                ["flap-floor", ["Crest gate flap.*"], ["Feed floor.*"]],
                ["flap-head", ["Crest gate flap.*"], ["Hood.*", "Head side plate.*", "Angle gear sector.*", "Counter.*"]],
                ["flap-REFfixedSweep", ["Crest gate flap.*"], ["REF ball sweep feed, fixed part.*"]],
                ["gateShaft-REFfixedSweep", ["Gate shaft 8.*"], ["REF ball sweep feed, fixed part.*"]],
                ["angleServo-gateServo", ["ENVELOPE angle servo.*"], ["ENVELOPE gate servo.*"]]
            ];
        var dl = [];
        for (var p in pairs)
        {
            const q0 = pick(p[1]);
            const q1 = pick(p[2]);
            if (size(q0) > 0 && size(q1) > 0)
                dl = append(dl, p[0] ~ " " ~ toString(roundToPrecision(evDistance(context, { "side0" : qUnion(q0), "side1" : qUnion(q1) }).distance / millimeter, 2)));
        }
        var msg = "CHECK " ~ toString(size(non)) ~ " real solids (" ~ toString(unnamed) ~ " unnamed ignored), " ~ toString(size(bad)) ~ " clashes, " ~ toString(size(abut)) ~ " contacts";
        for (var d in dl)
            msg = msg ~ " | " ~ d;
        for (var r in bad)
            msg = msg ~ " | CLASH " ~ r;
        println(msg);
        if (definition.listAbut)
        {
            for (var r in abut)
                println("  " ~ r);
        }
        if (size(bad) > 0)
            reportFeatureWarning(context, id, msg);
        else
            reportFeatureInfo(context, id, msg);
    });
