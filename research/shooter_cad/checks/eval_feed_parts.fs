// Onshape FeatureScript evaluation lambda (POST .../partstudios/.../featurescript), run per configuration.
// Ramp feed (feed_handoff = 1): checks the two REF ball sweep parts separately.
//   fixed part: ramp, crest, chute, rails up to the latest tongue lift (frame coordinates, same at every alpha)
//   head part:  tongue lift to hood end (rotates with the head)
// Expected contacts: fixed part rests on the feed floor rails (ABUT) and, for alpha above the 5 deg stop, overlaps
// the tongue where the tongue already lifts the ball (the fixed part is the alpha = 5 path there); head part rides
// the tongue, is squeezed into the hood and the main flywheel. Any other INTERFERE is a real clash.
function(context is Context, queries is map)
{
    const solids = evaluateQuery(context, qBodyType(qEverything(EntityType.BODY), BodyType.SOLID));
    var nm = [];
    for (var b in solids)
        nm = append(nm, getProperty(context, { "entity" : b, "propertyType" : PropertyType.NAME }));
    var nonQ = [];
    var pk = {};
    for (var i = 0; i < size(solids); i += 1)
    {
        if (!match(nm[i], "REF.*").hasMatch)
            nonQ = append(nonQ, solids[i]);
        if (match(nm[i], "REF ball sweep feed, fixed part.*").hasMatch)
            pk.fix = solids[i];
        if (match(nm[i], "REF ball sweep feed, head part.*").hasMatch)
            pk.head = solids[i];
        if (match(nm[i], "Main flywheel.*").hasMatch)
            pk.main = solids[i];
        if (match(nm[i], "Feed floor.*").hasMatch)
            pk.floor = solids[i];
        if (match(nm[i], "Main-wheel guard.*").hasMatch)
            pk.guard = solids[i];
        if (match(nm[i], "Counter-roller REV.*").hasMatch)
            pk.ctr = solids[i];
    }
    const nonU = qUnion(nonQ);
    const r3 = function(v) { return roundToPrecision(v / millimeter, 3); };
    const dTo = function(a, b) { return r3(evDistance(context, { "side0" : a, "side1" : b }).distance); };
    const nameOf = function(q) { return getProperty(context, { "entity" : q, "propertyType" : PropertyType.NAME }); };
    // unique "TYPE name" strings (evCollision returns one row per face pair)
    const clashSet = function(tool)
        {
            var seen = {};
            for (var c in evCollision(context, { "tools" : tool, "targets" : nonU }))
                seen[toString(c["type"]) ~ " " ~ nameOf(c.targetBody)] = true;
            return keys(seen);
        };
    var out = { "hasFix" : pk.fix != undefined, "hasHead" : pk.head != undefined, "hasFloor" : pk.floor != undefined };
    if (pk.fix != undefined)
    {
        out.fixCl = clashSet(pk.fix);
        out.fix_main = dTo(pk.fix, pk.main);
        if (pk.floor != undefined)
            out.fix_floor = dTo(pk.fix, pk.floor);
        if (pk.guard != undefined)
            out.fix_guard = dTo(pk.fix, pk.guard);
    }
    if (pk.head != undefined)
    {
        out.headCl = clashSet(pk.head);
        out.head_ctr = dTo(pk.head, pk.ctr);
        if (pk.floor != undefined)
            out.head_floor = dTo(pk.head, pk.floor);
        if (pk.guard != undefined)
            out.head_guard = dTo(pk.head, pk.guard);
    }
    return out;
}
