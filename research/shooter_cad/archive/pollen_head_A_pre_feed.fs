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
*/

const MM = millimeter;
const ZAX = vector(0, -1, 0);            // brief +Z in world coordinates
const ORIGIN = vector(0, 0, 0) * meter;
const TAIL = 140 * degree;               // head-local direction of the stop / actuator arm
const MOTOR_C = vector(115, 72) * millimeter;   // head-local counter motor envelope centre (TBD)

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
    drawHood(sk, p ~ "hd", g, g.thStart, g.thEnd, !full);
    if (full)
    {
        skCircle(sk, p ~ "ctrClr", { "center" : g.Cc, "radius" : g.Rc + g.clr, "construction" : true });
        skArc(sk, p ~ "hdat", { "start" : pol(g.Rh, g.thStart - 15 * degree), "mid" : pol(g.Rh, (g.thStart + g.thc) / 2), "end" : pol(g.Rh, g.thc + 20 * degree), "construction" : true });
        skCircle(sk, p ~ "bmin", { "center" : g.Pnip, "radius" : g.Dmin / 2, "construction" : true });
        skCircle(sk, p ~ "bmax", { "center" : g.Pnip, "radius" : g.Dmax / 2, "construction" : true });
        const tb = vector(sin(g.thStart), -cos(g.thStart));
        const e1 = pol(g.rHood, g.thStart);
        const e0 = e1 + tb * g.lead;
        skLineSegment(sk, p ~ "pathL", { "start" : e0, "end" : e1, "construction" : true });
        skArc(sk, p ~ "pathG", { "start" : e1, "mid" : pol(g.rHood, (g.thStart + g.thEnd) / 2), "end" : pol(g.rHood, g.thEnd), "construction" : true });
        skArc(sk, p ~ "pathU", { "start" : pol(g.rHood, g.thEnd), "mid" : pol(g.rHood, (g.thEnd + g.thc) / 2), "end" : pol(g.rHood, g.thc), "construction" : true });
        // rolling-envelope snapshots: feed entry, hood start, mid hood, hood end, release, exit
        skCircle(sk, p ~ "e0", { "center" : e0, "radius" : g.D / 2, "construction" : true });
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
    return [
            "alpha_geom = " ~ fdg(g.alpha) ~ " deg FROM VERTICAL (" ~ fdg(90 * degree - g.alpha) ~ " deg above horizontal)",
            "C = " ~ fmm(g.C) ~ " | D_ball = " ~ fmm(g.D) ~ " | delta_nip = " ~ fmm(g.dNip) ~ " | delta_hood = " ~ fmm(g.dHood) ~ " | p = " ~ fmm(g.Cz - g.C) ~ " mm",
            "hood datum R " ~ fmm(g.Rh) ~ " | fixed hood ends " ~ fdg(g.dEnd) ~ " deg before nip line (D_max at tight stop delta_nip " ~ fmm(g.dAdjMax) ~ " meets counter-roller at " ~ fdg(g.dCtrMax) ~ " deg)",
            "this ball meets counter-roller " ~ fdg(g.dCtrBall) ~ " deg before nip | nip ball centre r " ~ fmm(g.rNip) ~ " | release datum " ~ fmm(g.sRel) ~ " mm past nip",
            "geometric exit direction t = (sin a, cos a); measured dynamic exit angle = TBD"
        ];
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

// Swept volume of a ball (radius R, centre on a circle of radius rC about F) moving between thFrom and thTo:
// the revolved disc (torus segment, flat end caps) plus the full ball at each end position.
function revolveBall(context is Context, id is Id, rC is ValueWithUnits, R is ValueWithUnits, thFrom is ValueWithUnits, thTo is ValueWithUnits) returns Query
{
    const nrm = vector(sin(thTo), 0, -cos(thTo));
    const xd = vector(cos(thTo), 0, sin(thTo));
    const sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : plane(ORIGIN, nrm, xd) });
    skCircle(sk, "c", { "center" : vector(rC, 0 * MM), "radius" : R });
    skSolve(sk);
    opRevolve(context, id + "rv", { "entities" : qSketchRegion(id + "sk"), "axis" : line(ORIGIN, vector(0, 1, 0)), "angleForward" : thTo - thFrom });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    const p0 = pol(rC, thFrom);
    const p1 = pol(rC, thTo);
    const s0 = sphereAt(context, id + "e0", W(p0[0], p0[1], 0 * MM), R);
    const s1 = sphereAt(context, id + "e1", W(p1[0], p1[1], 0 * MM), R);
    const q = qUnion([qCreatedBy(id + "rv", EntityType.BODY), s0, s1]);
    opBoolean(context, id + "u", { "tools" : q, "operationType" : BooleanOperationType.UNION });
    return q;
}

function nameIt(context is Context, q is Query, name is string, col is Color, bom is boolean)
{
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.NAME, "value" : name });
    setProperty(context, { "entities" : q, "propertyType" : PropertyType.APPEARANCE, "value" : col });
    if (!bom)
        setProperty(context, { "entities" : q, "propertyType" : PropertyType.EXCLUDE_FROM_BOM, "value" : true });
}

function buildHeadPlate(context is Context, id is Id, g is map, z0 is ValueWithUnits, z1 is ValueWithUnits) returns Query
{
    const O = vector(0, 0) * MM;
    const Rpl = g.Rh + g.thk + 10 * MM;
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
                    skPoly(sk, "a", rectPts(td * 45 * MM, td, 45 * MM, 13 * MM));
                }),
            cylZ(context, id + "armE", td * 90 * MM, 13 * MM, z0, z1)
        ];
    const plate = qUnion(pcs);
    opBoolean(context, id + "u", { "tools" : plate, "operationType" : BooleanOperationType.UNION });
    const zm = (z0 + z1) / 2;
    const cuts = qUnion([
                cylZ(context, id + "bore", O, 21 * MM, z0 - MM, z1 + MM),
                extrudeZ(context, id + "slot", z0 - MM, z1 + MM, false, function(sk is Sketch)
                    {
                        skPoly(sk, "q", rectPts(Cz, vector(1, 0), 20 * MM + g.adj, 17 * MM));
                    }),
                cylZ(context, id + "pin", td * 80 * MM, 3 * MM, z0 - MM, z1 + MM),
                xCyl(context, id + "h1", g.Cz + 20 * MM + g.adj - MM, g.Cz + 44 * MM, 8 * MM, zm, 2.1 * MM),
                xCyl(context, id + "h2", g.Cz + 20 * MM + g.adj - MM, g.Cz + 44 * MM, -8 * MM, zm, 2.1 * MM)
            ]);
    opBoolean(context, id + "c", { "tools" : cuts, "targets" : plate, "operationType" : BooleanOperationType.SUBTRACTION });
    return plate;
}

function buildFramePlate(context is Context, id is Id, z0 is ValueWithUnits, z1 is ValueWithUnits) returns Query
{
    const O = vector(0, 0) * MM;
    const pcs = [
            cylZ(context, id + "ring", O, 45 * MM, z0, z1),
            extrudeZ(context, id + "rect", z0, z1, false, function(sk is Sketch)
                {
                    skPoly(sk, "r", rectPts(vector(-95, 0) * MM, vector(1, 0), 95 * MM, 80 * MM));
                })
        ];
    const plate = qUnion(pcs);
    opBoolean(context, id + "u", { "tools" : plate, "operationType" : BooleanOperationType.UNION });
    opBoolean(context, id + "c", { "tools" : cylZ(context, id + "bore", O, 11 * MM, z0 - MM, z1 + MM), "targets" : plate, "operationType" : BooleanOperationType.SUBTRACTION });
    return plate;
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
        var head = [];

        // ---- rotating head: built with the counter-roller on +X, then rotated by -alpha about F ----
        const hood = extrudeZ(context, id + "hood", -zl, zl, false, function(sk is Sketch)
            {
                drawHood(sk, "h", g, g.thStartL, g.thEndL, false);
            });
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
        nameIt(context, hood, "Hood (printed): R_hood_inner, ends before counter-roller contact", color(0.95, 0.55, 0.1, 1), true);
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
            const hp = buildHeadPlate(context, id + ("hp" ~ sd), g, z0, z1);
            nameIt(context, hp, "Head side plate" ~ nm ~ " (pivots about F)", color(0.2, 0.45, 0.85, 1), true);
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
        const ap = cylZ(context, id + "ap", vector(cos(TAIL), sin(TAIL)) * 80 * MM, 2.9 * MM, zl - 8 * MM, zl + th);
        nameIt(context, ap, "Actuator interface: clevis pin on tail arm (actuator TBD)", color(0.3, 0.3, 0.3, 1), true);
        head = concatenateArrays([head, [cg, cm, cp, ap]]);

        if (definition.refs)
        {
            const rb = sphereAt(context, id + "rb", W(g.rNip, 0 * MM, 0 * MM), D / 2);
            nameIt(context, rb, "REF ball at nip line (D_ball, undeformed)", color(1, 0.85, 0, 0.6), false);
            const sw1 = revolveBall(context, id + "sw1", g.rHood, D / 2, g.thStartL, g.thEndL);
            const tb = vector(sin(g.thStartL), -cos(g.thStartL));
            const e1 = pol(g.rHood, g.thStartL);
            const e0 = e1 + tb * g.lead;
            const sw1b = capsule(context, id + "sw1b", W(e0[0], e0[1], 0 * MM), W(e1[0], e1[1], 0 * MM), D / 2);
            const swA = qUnion([sw1, sw1b]);
            opBoolean(context, id + "sw1u", { "tools" : swA, "operationType" : BooleanOperationType.UNION });
            nameIt(context, swA, "REF ball sweep feed entry to hood end (D_ball)", color(1, 0.85, 0, 0.25), false);
            const swB = revolveBall(context, id + "sw2", g.rHood, D / 2, g.thEndL, 0 * degree);
            nameIt(context, swB, "REF ball sweep hood end to nip, unguided (D_ball)", color(1, 0.5, 0, 0.25), false);
            const cor = capsule(context, id + "cor", W(g.rNip, g.sCorr + 1 * MM, 0 * MM), W(g.rNip, g.Lcorr, 0 * MM), g.Dmax / 2);
            nameIt(context, cor, "REF exit corridor (D_max envelope)", color(0.2, 0.8, 0.3, 0.25), false);
            head = concatenateArrays([head, [rb, swA, swB, cor]]);
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
            const fp = buildFramePlate(context, id + ("fp" ~ sd), z0, z1);
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
        const stops = [[5 * degree, 1, "Hard stop alpha = 5 deg"], [25 * degree, -1, "Hard stop alpha = 25 deg"]];
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
        const mg = extrudeZ(context, id + "mg", -Wm / 2 - 5 * MM, Wm / 2 + 5 * MM, false, function(sk is Sketch)
            {
                skSectorAt(sk, "g", O, g.Rm + 6 * MM, g.Rm + 9 * MM, 50 * degree, 210 * degree);
            });
        nameIt(context, mg, "Main-wheel guard (fixed, mounts TBD)", color(0.95, 0.85, 0.1, 1), true);
        const mm = cylZ(context, id + "mm", vector(-120, 45) * MM, 19 * MM, zf1, zf1 + 70 * MM);
        nameIt(context, mm, "ENVELOPE main motor (TBD)", ENV, false);
        const mp = ringZ(context, id + "mp", O, rs, 20 * MM, zf1 + 3 * MM, zf1 + 15 * MM);
        nameIt(context, mp, "ENVELOPE main pulley/belt (TBD)", ENV, false);

        const msg = "alpha " ~ fdg(alpha) ~ " deg from vertical | C " ~ fmm(g.C) ~ " | setting delta_nip " ~ fmm(g.dSet) ~ " (this ball " ~ fmm(g.dNip) ~ ") | fixed hood ends " ~ fdg(g.dEnd) ~ " deg before nip | release datum " ~ fmm(g.sRel) ~ " mm past nip";
        if (g.dSet < g.dAdjMin - 0.001 * MM || g.dSet > g.dAdjMax + 0.001 * MM)
            reportFeatureWarning(context, id, "delta_nip " ~ fmm(g.dSet) ~ " is outside the adjuster stops " ~ fmm(g.dAdjMin) ~ " to " ~ fmm(g.dAdjMax) ~ " mm; the fixed hood is not designed for it. " ~ msg);
        else
            reportFeatureInfo(context, id, msg);
    });
