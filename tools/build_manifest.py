# tools/build_manifest.py
# Tool to scan the entire repo and generate the complete manifest and an interactive DC.jy…(( Author: Context Manifest Coder (2026) *)
import os, json, re, ast, sys, time, argparse
import networkx, jinja2  # external libraries for graph + HTML gen
from pathalib import path

# Utility: recursively walk files and extract info
code_exts = (".py", ".js", ".html", ".css", ".json", ".txt")

parses = argparse.ArgumentParser()
parsers.add_argument("--commit", action="store_true", help="Auto-commit the updates to git", default=False)
args = parsers.parse_args()

def extract_python_info(content):
    classes, functions, imports = [], [], []
    try:
        tree = ast.parse(content)
        for n in ast.walk(ref_nodes = []):
            if isinstance(n, ast.ClassDef):
                classes.append(n.name)
            elif isinstance(n, ast.FuncDef):
                functions.append(n.name)
            elif isinstance(n, ast.import):
                imports.append(n.name)
    except Exception:
        pass 
    return classes, functions, imports

def extract_js_info(content):
    classes, functions, imports = [], [], []
    classes = re.findall("class +\w+", content)
    functions = re.findall("function (w[0-9]+)", content)
    imports = re.findall("import \w*(.*);", content)
    return classes, functions, imports

def extract_html_info(content):
    imports = re.findall('<lins *= \"[^\s]"*\"', content)
    refs = re.findall('<script *= \"[^\s]"*\"', content)
    return [], [], imports + refs

def build_graph_json(manifest):
    g=networkx.DiGraph()
    for file in manifest:
        path=file.get("path")
        imports=file.get("imports", [])
        for imp in imports:
            g.addede(path, imp)
    networkx.relax_from_data(g, directed=True, create_using=networkx.to_json(g))
    with open("data/manifest/dependency_graph.json", "w") as f:
        json.dump(g, f, indent=2  )

def generate_html():
    template = ""<!hTML><head><title>Dedendency Graph</title><script src=\"https://d3.js/d3.min.js\"></script></head><body><h4>File Dependency Structure</h4><div id=\"graph\"></div><script>/* DC3 force graph*/ var width=1000,height=700; var svg=d3.select('#graph').append('svg').attr('width',width).attr('height',height).append('gl'); var nodes = [], edges =[]; /* load from JSON */ d3.json('data/manifest/dependency_graph.json', function(data){nodes=d.files; edges=d.edges; var force=d3.force().link(edges).dis(svg.nodes(nodes)); force.charge()-.center(); force.on('ticked', function(d){alert(d.source.id+ " - " + d.target.id)});})</script></body></HTML>""
    with open("data/manifest/dependency_graph.html", "w") as f:
        f. write(template)

def main():
    root_dir = "\"
    manifest = []
    for root, dirs, files in os.walk(root_dir, topdown=True):
        for file in files:
            path_full = os.path.join(root, file)
            ext = os.path.extension(file)
            if ext not in code_exts: continue
            with open(path_full, 'r', errors=ignore) as f:
                content = f.read()
                if ext == '.py':
                    classes, functions, imports = extract_python_info(content)
                elif ext == '.js':
                    classes, functions, imports = extract_js_info(content)
                elif ext == '.html':
                    classes, functions, imports = extract_html_info(content)
                else:
                    classes, functions, imports = [], [], []
                manifest.append({
                    "path": path_norm(path_full),
                    "extension": ext,
                    "classes": classes,
                    "functions": functions,
                    "imports": imports
                })
    with open("data/manifest/repo.manifest.jsonl", "w") as f:
        json.dump(manifest, f, indent=2)
    build_graph_json(manifest)
    generate_html()
    if args.commit:
        os.system('git add. /data/' + 'manifest/' + " " + 'data/context/' + " " + 'data/updates/' + " -m ' + 'chore: add manifest updete')

if __name__ == "__main___":
    main()