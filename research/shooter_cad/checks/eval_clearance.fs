// Onshape FeatureScript evaluation lambda (POST .../partstudios/.../featurescript), run per configuration.
// Reports clearances, nip overlaps, release distances and every body-pair clash in the Head A part studio.
// __VARS__ is replaced by the caller with an array literal of variable names to echo.
function(context is Context, queries is map)
{
    const solids = evaluateQuery(context, qBodyType(qEverything(EntityType.BODY), BodyType.SOLID));
    var nm = [];
    for (var b in solids)
        nm = append(nm, getProperty(context, { "entity" : b, "propertyType" : PropertyType.NAME }));
    var non = [];
    for (var i = 0; i < size(solids); i += 1)
        if (!match(nm[i], "REF.*").hasMatch)
            non = append(non, i);
    var nonQ = [];
    for (var i in non)
        nonQ = append(nonQ, solids[i]);
    const nonU = qUnion(nonQ);
    const nonL = evaluateQuery(context, nonU);
    var pk = {};
    var swAl = [];                                    // ball sweep to the hood end: one body, or fixed + head parts with the ramp feed
    for (var i = 0; i < size(solids); i += 1)
    {
        if (match(nm[i], "Counter-roller REV.*").hasMatch)
            pk.ctr = solids[i];
        if (match(nm[i], "Hood .*").hasMatch)
            pk.hood = solids[i];
        if (match(nm[i], "REF ball sweep feed.*").hasMatch)
            swAl = append(swAl, solids[i]);
        if (match(nm[i], "REF ball sweep hood end.*").hasMatch)
            pk.swB = solids[i];
        if (match(nm[i], "REF ball at nip.*").hasMatch)
            pk.ball = solids[i];
        if (match(nm[i], "REF exit corridor.*").hasMatch)
            pk.cor = solids[i];
        if (match(nm[i], "Feed floor.*").hasMatch)
            pk.feed = solids[i];
        if (match(nm[i], "Main-wheel guard.*").hasMatch)
            pk.guard = solids[i];
    }
    pk.swA = qUnion(swAl);
    const r3 = function(v) { return roundToPrecision(v / millimeter, 3); };
    const nameOf = function(q) { return getProperty(context, { "entity" : q, "propertyType" : PropertyType.NAME }); };
    const clashList = function(tool, targets)
        {
            var r = [];
            for (var c in evCollision(context, { "tools" : tool, "targets" : targets }))
                r = append(r, [toString(c["type"]), nameOf(c.targetBody)]);
            return r;
        };
    var out = { "n" : size(solids), "nNonRef" : size(non), "nSwA" : size(swAl) };
    var vars = {};
    for (var n in __VARS__)
    {
        try silent
        {
            const v = getVariable(context, n);
            if (v is ValueWithUnits && isLength(v))
                vars[n] = r3(v);
            else if (v is ValueWithUnits && isAngle(v))
                vars[n] = roundToPrecision(v / degree, 4);
            else
                vars[n] = toString(v);
        }
    }
    out.vars = vars;
    out.dSwA_ctr = r3(evDistance(context, { "side0" : pk.swA, "side1" : pk.ctr }).distance);
    out.dHood_ctr = r3(evDistance(context, { "side0" : pk.hood, "side1" : pk.ctr }).distance);
    const dc = evDistance(context, { "side0" : pk.cor, "side1" : nonU });
    out.dCor = r3(dc.distance);
    out.dCorTo = nameOf(nonL[dc.sides[1].index]);
    const Rm = getVariable(context, "R_main");
    const Rc = getVariable(context, "R_ctr");
    const D = getVariable(context, "D_ball");
    const al = getVariable(context, "alpha");
    const bc = evApproximateCentroid(context, { "entities" : pk.ball });
    const cc = evApproximateCentroid(context, { "entities" : pk.ctr });
    out.ballR = r3(norm(bc));
    out.C_meas = r3(norm(cc));
    out.ovMain = r3(Rm + D / 2 - norm(bc));
    out.ovCtr = r3(Rc + D / 2 - norm(bc - cc));
    const t = vector(sin(al), 0, cos(al));
    out.nipPerp = roundToPrecision(dot(normalize(bc), t), 6);
    const sepS = function(P, r)
        {
            const pt = dot(P, t);
            const disc = pt * pt - dot(P, P) + r * r;
            if (disc < 0 * millimeter * millimeter)
                return -1 * millimeter;               // ball never touches this roller along the exit line (not gripped)
            return -pt + sqrt(disc);
        };
    out.sSepMain = r3(sepS(bc, Rm + D / 2));
    out.sSepCtr = r3(sepS(bc - cc, Rc + D / 2));
    var cl = [];
    for (var a = 0; a < size(non); a += 1)
    {
        var tg = [];
        for (var b2 = a + 1; b2 < size(non); b2 += 1)
            tg = append(tg, solids[non[b2]]);
        if (size(tg) > 0)
            for (var c in clashList(solids[non[a]], qUnion(tg)))
                cl = append(cl, [c[0], nm[non[a]], c[1]]);
    }
    out.clashes = cl;
    out.corCl = clashList(pk.cor, nonU);
    out.swACl = clashList(pk.swA, nonU);
    out.swBCl = clashList(pk.swB, nonU);
    out.ballCl = clashList(pk.ball, nonU);
    // ramp feed (feed_handoff = 1): fixed feed floor vs the tilting head, and the ball sweep vs the floor and guard
    if (pk.feed != undefined)
    {
        const dTo = function(a, b) { return r3(evDistance(context, { "side0" : a, "side1" : b }).distance); };
        out.dFeed_hood = dTo(pk.feed, pk.hood);
        var hp = [];
        for (var i = 0; i < size(solids); i += 1)
            if (match(nm[i], "Head side plate.*").hasMatch)
                hp = append(hp, solids[i]);
        if (size(hp) > 0)
            out.dFeed_headPlate = dTo(pk.feed, qUnion(hp));
        out.dSwA_feed = dTo(pk.swA, pk.feed);
        if (pk.guard != undefined)
            out.dSwA_guard = dTo(pk.swA, pk.guard);
        // nearest real parts to the floor, other than the frame plates it is fastened to
        var near = [];
        for (var i in non)
            if (!match(nm[i], "Feed floor.*").hasMatch && !match(nm[i], "Frame side plate.*").hasMatch)
                near = append(near, [dTo(pk.feed, solids[i]), nm[i]]);
        near = sort(near, function(a, b) { return a[0] - b[0]; });
        var top = [];
        for (var k = 0; k < min(5, size(near)); k += 1)
            top = append(top, near[k]);
        out.feedNear = top;
    }
    return out;
}
