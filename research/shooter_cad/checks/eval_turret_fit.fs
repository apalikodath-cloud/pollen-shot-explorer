FeatureScript 3112;
import(path : "onshape/std/common.fs", version : "3112.0");

// POLLEN turret fit: extents of Head A (Concept A) for fitting it on a robot turret.
// Kept in the Onshape Feature Studio "POLLEN turret fit FS" of the counter-roller document.
// Use: add "POLLEN turret fit" at the end of the "Head A (Concept A)" Part Studio, read the FeatureScript console,
// change the alpha configuration and read again, then suppress the feature.
// Frame: Part Studio world, mm. X = downrange, Z = up, Y = minus the brief's shaft axis (brief +Z side = world -Y).
// Origin = F, the main axle (the head's tilt pivot).
// Counts every solid except REF bodies (ball sweeps, exit corridor, nip ball). ENVELOPE bodies (motors, belts,
// servos, encoder allowance) are counted as space claims. Bodies without a pollenName attribute are counted too.
// Output lines (println):
//   TF box    xmin xmax ymin ymax zmin zmax                 (all counted solids, tight)
//   TF h      h(0) h(5) ... h(355)                          plan-view support function about F: farthest extent
//                                                           along (cos t, sin t, 0), t in degrees, tight boxes
//   TF part   name | xmin xmax ymin ymax zmin zmax          one line per counted solid
annotation { "Feature Type Name" : "POLLEN turret fit", "Feature Type Description" : "Head extents and plan-view reach about F for the turret fit (suppress after reading; slow)" }
export const pollenTurretFit = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Angle step (deg)", "Default" : 5 }
        isInteger(definition.stepDeg, { (unitless) : [1, 5, 90] } as IntegerBoundSpec);
    }
    {
        const solids = evaluateQuery(context, qBodyType(qEverything(EntityType.BODY), BodyType.SOLID));
        var keep = [];
        var names = [];
        var unnamed = 0;
        for (var b in solids)
        {
            const v = getAttribute(context, { "entity" : b, "name" : "pollenName" });
            const n = v is string ? v : "";
            if (n == "")
                unnamed += 1;
            if (!match(n, "REF.*").hasMatch)
            {
                keep = append(keep, b);
                names = append(names, n == "" ? "(unnamed)" : n);
            }
        }
        if (size(keep) == 0)
            throw regenError("POLLEN turret fit: no solids to measure");
        const r1 = function(x) { return toString(roundToPrecision(x / millimeter, 1)); };
        const boxTxt = function(bx is Box3d)
            {
                return r1(bx.minCorner[0]) ~ " " ~ r1(bx.maxCorner[0]) ~ " " ~ r1(bx.minCorner[1]) ~ " " ~ r1(bx.maxCorner[1]) ~ " " ~
                    r1(bx.minCorner[2]) ~ " " ~ r1(bx.maxCorner[2]);
            };
        const all = qUnion(keep);
        const bbox = evBox3d(context, { "topology" : all, "tight" : true });
        println("TF counted " ~ toString(size(keep)) ~ " of " ~ toString(size(solids)) ~ " solids, unnamed " ~ toString(unnamed));
        println("TF box " ~ boxTxt(bbox));
        var h = "";
        for (var t = 0; t < 360; t += definition.stepDeg)
        {
            const a = t * degree;
            const cs = coordSystem(vector(0, 0, 0) * meter, vector(cos(a), sin(a), 0), vector(0, 0, 1));
            const bt = evBox3d(context, { "topology" : all, "tight" : true, "cSys" : cs });
            h = h ~ (t == 0 ? "" : " ") ~ r1(bt.maxCorner[0]);
        }
        println("TF h " ~ h);
        for (var i = 0; i < size(keep); i += 1)
            println("TF part " ~ names[i] ~ " | " ~ boxTxt(evBox3d(context, { "topology" : keep[i], "tight" : true })));
        reportFeatureInfo(context, id, "TURRET FIT box (mm, F origin) " ~ boxTxt(bbox) ~ " | plan reach and per-part boxes in the FeatureScript console");
    });
