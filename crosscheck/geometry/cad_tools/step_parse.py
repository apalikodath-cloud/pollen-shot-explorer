"""Minimal STEP AP242 assembly parser: world-space vertex clouds per part occurrence.
Usage: python -I step_parse.py <step file> <out.npz/pickle>
"""
import re, sys, pickle
import numpy as np

path, out = sys.argv[1], sys.argv[2]
txt = open(path, 'r', encoding='latin-1').read()
data = txt[txt.index('DATA;') + 5: txt.rindex('ENDSEC;')]
ent_re = re.compile(r"#(\d+)\s*=\s*((?:[^;']|'[^']*')*);", re.S)
E = {}
for m in ent_re.finditer(data):
    E[int(m.group(1))] = ' '.join(m.group(2).split())
print('entities', len(E))

def typ(s):
    s = s.lstrip('(')
    return s[:s.index('(')].strip()

refs_re = re.compile(r"#(\d+)")
num_re = re.compile(r"[-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?")

def args(s):
    # top-level args of simple entity
    i = s.index('(')
    body = s[i + 1: s.rindex(')')]
    out, depth, cur, inq = [], 0, '', False
    for ch in body:
        if ch == "'":
            inq = not inq
        if not inq:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif ch == ',' and depth == 0:
                out.append(cur.strip()); cur = ''; continue
        cur += ch
    out.append(cur.strip())
    return out

def ref(a):
    return int(a.strip().lstrip('#'))

def point(i):
    s = E[i]
    inner = s[s.index('(', s.index('(') + 1) + 1: s.rindex(')')]
    inner = inner[:inner.index(')')]
    return np.array([float(x) for x in inner.split(',')])

def direction(i):
    return point(i)

def placement(i):
    a = args(E[i])
    o = point(ref(a[1]))
    z = direction(ref(a[2])) if a[2] != '$' else np.array([0, 0, 1.])
    x = direction(ref(a[3])) if a[3] != '$' else np.array([1., 0, 0])
    z = z / np.linalg.norm(z)
    x = x - np.dot(x, z) * z; x /= np.linalg.norm(x)
    y = np.cross(z, x)
    T = np.eye(4); T[:3, 0] = x; T[:3, 1] = y; T[:3, 2] = z; T[:3, 3] = o
    return T

# products
prod_name = {}
for k, s in E.items():
    t = typ(s)
    if t == 'PRODUCT':
        prod_name[k] = args(s)[1].strip("'")
pdf_prod = {}
for k, s in E.items():
    if typ(s).startswith('PRODUCT_DEFINITION_FORMATION'):
        pdf_prod[k] = ref(args(s)[2])
pd_name = {}
for k, s in E.items():
    if typ(s) == 'PRODUCT_DEFINITION':
        pd_name[k] = prod_name[pdf_prod[ref(args(s)[2])]]
pds_target = {}
for k, s in E.items():
    if typ(s) == 'PRODUCT_DEFINITION_SHAPE':
        pds_target[k] = ref(args(s)[2])
# SR for each PD
pd_sr = {}
for k, s in E.items():
    if typ(s) == 'SHAPE_DEFINITION_REPRESENTATION':
        a = args(s)
        pd_sr[pds_target[ref(a[0])]] = ref(a[1])
sr_pd = {v: k for k, v in pd_sr.items()}
# SR -> brep reps
sr_breps = {}
for k, s in E.items():
    if s.startswith('SHAPE_REPRESENTATION_RELATIONSHIP('):
        a = args(s)
        r1, r2 = ref(a[2]), ref(a[3])
        if typ(E[r2]) == 'ADVANCED_BREP_SHAPE_REPRESENTATION':
            sr_breps.setdefault(r1, []).append(r2)
        elif typ(E[r1]) == 'ADVANCED_BREP_SHAPE_REPRESENTATION':
            sr_breps.setdefault(r2, []).append(r1)
# assembly relations: complex RRWT entities
rrwt = {}
for k, s in E.items():
    if s.startswith('(') and 'REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION' in s:
        m = re.search(r"REPRESENTATION_RELATIONSHIP\('[^']*','[^']*',#(\d+),#(\d+)\)", s)
        m2 = re.search(r"REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION\(#(\d+)\)", s)
        rrwt[k] = (int(m.group(1)), int(m.group(2)), int(m2.group(1)))
# NAUO -> (parent pd, child pd, name)
nauo = {}
for k, s in E.items():
    if typ(s) == 'NEXT_ASSEMBLY_USAGE_OCCURRENCE':
        a = args(s)
        nauo[k] = (ref(a[3]), ref(a[4]), a[1].strip("'"))
children = {}
for k, s in E.items():
    if typ(s) == 'CONTEXT_DEPENDENT_SHAPE_REPRESENTATION':
        a = args(s)
        rr, pds = ref(a[0]), ref(a[1])
        n = pds_target[pds]
        par, chi, nm = nauo[n]
        r1, r2, idt = rrwt[rr]
        ia = args(E[idt])
        A1, A2 = placement(ref(ia[2])), placement(ref(ia[3]))
        T = A2 @ np.linalg.inv(A1)
        assert r1 == pd_sr[chi] and r2 == pd_sr[par], (k, r1, r2)
        children.setdefault(par, []).append((chi, T, nm))
allchild = {c for v in children.values() for c, _, _ in v}
roots = [p for p in pd_sr if p not in allchild]
print('roots', [pd_name[r] for r in roots])

# vertices of a brep rep (local)
vp_cache = {}
def brep_vertices(absr):
    if absr in vp_cache:
        return vp_cache[absr]
    seen, stack, pts = set(), [absr], []
    while stack:
        i = stack.pop()
        if i in seen:
            continue
        seen.add(i)
        s = E[i]
        t = typ(s)
        if t == 'VERTEX_POINT':
            pts.append(point(ref(args(s)[1])))
            continue
        if t in ('CARTESIAN_POINT', 'DIRECTION', 'AXIS2_PLACEMENT_3D', 'GEOMETRIC_REPRESENTATION_CONTEXT') or s.startswith('('):
            continue
        if t in ('PLANE', 'CYLINDRICAL_SURFACE', 'CONICAL_SURFACE', 'TOROIDAL_SURFACE', 'SPHERICAL_SURFACE',
                 'B_SPLINE_SURFACE_WITH_KNOTS', 'LINE', 'CIRCLE', 'ELLIPSE', 'B_SPLINE_CURVE_WITH_KNOTS',
                 'DEGENERATE_TOROIDAL_SURFACE', 'VECTOR'):
            continue
        for r in refs_re.findall(re.sub(r"'[^']*'", "''", s)):
            stack.append(int(r))
    P = np.array(pts) if pts else np.zeros((0, 3))
    vp_cache[absr] = P
    return P

# also capture circle info in world for round features (pivot axle etc.)
def brep_circles(absr):
    seen, stack, out = set(), [absr], []
    while stack:
        i = stack.pop()
        if i in seen:
            continue
        seen.add(i)
        s = E[i]; t = typ(s)
        if t == 'CIRCLE':
            a = args(s)
            out.append((placement(ref(a[1])), float(a[2])))
            continue
        if t in ('CARTESIAN_POINT', 'DIRECTION', 'VERTEX_POINT', 'AXIS2_PLACEMENT_3D') or s.startswith('('):
            continue
        for r in refs_re.findall(re.sub(r"'[^']*'", "''", s)):
            stack.append(int(r))
    return out

occ = []  # (path names, pd, world T, world verts)
nodes = []
def walk(pd, T, pathn):
    sr = pd_sr[pd]
    nodes.append({'path': pathn, 'T': T, 'name': pd_name[pd], 'nchild': len(children.get(pd, []))})
    for b in sr_breps.get(sr, []):
        V = brep_vertices(b)
        W = (T[:3, :3] @ V.T).T + T[:3, 3] if len(V) else V
        circ = [(T @ P, r) for P, r in brep_circles(b)]
        occ.append({'path': pathn, 'name': pd_name[pd], 'T': T, 'V': W, 'circles': circ, 'brep': b})
    for chi, Tc, nm in children.get(pd, []):
        walk(chi, T @ Tc, pathn + [pd_name[chi]])

for r in roots:
    walk(r, np.eye(4), [pd_name[r]])
print('occurrences with geometry', len(occ))
pickle.dump(occ, open(out, 'wb'))
pickle.dump(nodes, open(out.replace('.pkl','_nodes.pkl'), 'wb'))
