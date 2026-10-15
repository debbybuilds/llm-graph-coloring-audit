#!/usr/bin/env python3
"""Audit supplied graph-coloring records. Python >=3.10; no dependencies."""
import argparse, csv, hashlib, json, pathlib, re


def solve(n, edges):
    """Complete deterministic backtracking with DSATUR ordering; no SAT library."""
    neighbors = [set() for _ in range(n)]
    for u, v in edges:
        if u == v:
            return None, 0
        neighbors[u].add(v)
        neighbors[v].add(u)
    colors = [-1] * n
    nodes = 0
    def visit():
        nonlocal nodes
        nodes += 1
        remaining = [v for v in range(n) if colors[v] < 0]
        if not remaining:
            return True
        v = max(remaining, key=lambda v: (len({colors[u] for u in neighbors[v] if colors[u] >= 0}), len(neighbors[v]), -v))
        forbidden = {colors[u] for u in neighbors[v]}
        for c in range(3):
            if c not in forbidden:
                colors[v] = c
                if visit():
                    return True
                colors[v] = -1
        return False
    return ({str(i): c for i, c in enumerate(colors)} if visit() else None), nodes


def parse(raw):
    if raw is None:
        return None, None, None, 'missing response'
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError('duplicate JSON key')
            result[k] = v
        return result
    def decode(text):
        return json.loads(text, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonstandard constant')))
    try:
        obj = decode(raw)
        json_only = True
    except (ValueError, TypeError):
        json_only = False
        # Recover only a single fenced response, preserving format failure.
        match = re.fullmatch(r'\s*```(?:json)?\s*(.*?)\s*```\s*', raw, re.S)
        try:
            obj = decode(match.group(1)) if match else None
        except ValueError:
            obj = None
    schema = (type(obj) is dict and set(obj) == {'status', 'assignment'}
              and obj['status'] in ('SAT', 'UNSAT') and type(obj['assignment']) is dict)
    if schema:
        schema = all(type(k) is str and type(v) is int and v in range(3) for k, v in obj['assignment'].items())
        schema = schema and (obj['status'] != 'UNSAT' or obj['assignment'] == {})
    return obj, json_only, schema, None


def validate_graph(n, edges):
    assert type(n) is int and n >= 0, 'n must be a nonnegative integer'
    assert type(edges) is list, 'edges must be a list'
    for edge in edges:
        assert type(edge) is list and len(edge) == 2
        assert all(type(v) is int and 0 <= v < n for v in edge), 'invalid endpoint'


def audit(data):
    rows = []
    for record in data['experiments']:
        n, edges = record['n'], record['edges']
        graph_available = n is not None and edges is not None
        truth, witness, nodes = None, None, None
        if graph_available:
            validate_graph(n, edges)
            witness, nodes = solve(n, edges)
            truth = 'SAT' if witness is not None else 'UNSAT'
            if witness is not None:
                assert set(witness) == {str(v) for v in range(n)}
                assert all(witness[str(u)] != witness[str(v)] for u,v in edges)
        for model, response in record['responses'].items():
            obj, json_only, schema, error = parse(response['raw'] or response.get('payload_json'))
            if response['raw'] is None:
                json_only = None
            observed_format = (json_only and schema) if json_only is not None else None
            effective_format = observed_format if observed_format is not None else response.get('format_reported')
            predicted = obj.get('status') if type(obj) is dict else None
            classification = predicted == truth if truth and predicted in ('SAT','UNSAT') else None
            valid, violations, complete = None, None, None
            if graph_available and type(obj) is dict and predicted == 'SAT' and type(obj.get('assignment')) is dict:
                a = obj['assignment']
                complete = set(a) == {str(v) for v in range(n)}
                domain = all(type(c) is int and c in range(3) for c in a.values())
                if complete and domain:
                    violations = [edge for edge in edges if a[str(edge[0])] == a[str(edge[1])]]
                    valid = not violations
                else:
                    valid = False
            math = None
            if graph_available and obj is not None:
                math = bool(classification and ((predicted == 'UNSAT' and schema) or (predicted == 'SAT' and valid)))
            rows.append(dict(test_id=record['test_id'],model=model,excluded_from_primary=record['excluded_from_primary'],graph_available=graph_available,n=n,edge_count=len(edges) if graph_available else None,unique_undirected_edges=len({tuple(sorted(e)) for e in edges}) if graph_available else None,truth=truth,witness=witness,search_nodes=nodes,predicted_status=predicted,json_only=json_only,schema_compliant=schema,format_compliant=observed_format,format_including_reported=effective_format,format_evidence='observed pasted response' if response['raw'] is not None else 'reported reconstruction',classification_correct=classification,complete_assignment=complete,valid_coloring=valid,violating_edges=violations,mathematically_correct=math,error=error))
    metrics = {}
    for model in ('ChatGPT','Claude'):
        selected = [r for r in rows if r['model']==model and not r['excluded_from_primary']]
        metrics[model] = {'planned_tests':len(selected)}
        for field in ('json_only','format_compliant','format_including_reported','classification_correct','mathematically_correct'):
            vals = [r[field] for r in selected if r[field] is not None]
            metrics[model][field] = dict(passed=sum(vals),evaluated=len(vals),missing=len(selected)-len(vals),rate=sum(vals)/len(vals) if vals else None)
    return dict(method='Complete deterministic DSATUR-ordered Python backtracking; not PySAT',rows=rows,primary_metrics_excluding_test_1=metrics)


def main():
    root = pathlib.Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=pathlib.Path, default=root/'data/experiments.json')
    parser.add_argument('--output', type=pathlib.Path, default=root/'results/audit.json')
    args = parser.parse_args()
    raw = args.data.read_bytes()
    output = audit(json.loads(raw))
    output['dataset_sha256'] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2)+'\n')
    fields = ['test_id','model','excluded_from_primary','n','edge_count','truth','predicted_status','classification_correct','mathematically_correct','format_compliant','format_including_reported','format_evidence']
    with args.output.with_suffix('.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(output['rows'])
    print(json.dumps(output['primary_metrics_excluding_test_1'], indent=2))

if __name__ == '__main__':
    main()
