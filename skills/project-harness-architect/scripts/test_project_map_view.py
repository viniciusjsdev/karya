"""Exercise viewer grouping and controls in a minimal DOM, without browser or network access."""
from pathlib import Path
import json
import shutil
import subprocess

import pytest


NODE_TEST = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const input=JSON.parse(fs.readFileSync(0,'utf8')),template=input.template;
function run(data){
 const roots=new Map(),all=new Set();let document;
 class Element{
  constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.parentElement=null;this.attrs={};this.dataset={};this.style={};this.listeners={};this.value='';this.hidden=false;this.checked=false;this.disabled=false;this.ownText='';this.classes=new Set();all.add(this);this.classList={toggle:(c,force)=>{const on=force===undefined?!this.classes.has(c):force;on?this.classes.add(c):this.classes.delete(c);},contains:c=>this.classes.has(c)};}
  set className(v){this.classes=new Set(v.split(/\s+/));}get className(){return [...this.classes].join(' ');}
  set textContent(v){this.ownText=String(v??'');this.children=[];}get textContent(){return this.ownText+this.children.map(c=>c.textContent).join('');}
  get childElementCount(){return this.children.length;}
  setAttribute(k,v){this.attrs[k]=String(v);if(k==='class')this.className=v;if(k==='id')this.id=v;}
  getAttribute(k){return this.attrs[k]??null;}removeAttribute(k){delete this.attrs[k];}
  append(...items){for(let c of items){if(typeof c==='string'){const text=new Element('text');text.textContent=c;c=text;}if(c.parentElement)c.parentElement.children=c.parentElement.children.filter(x=>x!==c);c.parentElement=this;this.children.push(c);}}
  replaceChildren(...items){for(const c of this.children)c.parentElement=null;this.children=[];this.ownText='';this.append(...items);}
  addEventListener(k,fn){(this.listeners[k]??=[]).push(fn);}
  fire(k,props={}){for(const fn of this.listeners[k]||[])fn({type:k,target:this,preventDefault(){},stopPropagation(){},...props});}
  matches(s){if(s==='[data-layer]')return this.dataset.layer!==undefined;if(s==='[data-area]')return this.dataset.area!==undefined;if(s.startsWith('.'))return this.classes.has(s.slice(1));if(s.startsWith('option['))return this.tagName==='OPTION'&&this.value==='area';return this.tagName.toLowerCase()===s;}
  querySelectorAll(s){return this.children.flatMap(c=>[...(c.matches(s)?[c]:[]),...c.querySelectorAll(s)]);}
  querySelector(s){return this.querySelectorAll(s)[0]||null;}
  closest(s){return this.matches(s)?this:this.parentElement?.closest(s);}
  focus(){document.activeElement=this;}getBoundingClientRect(){return {width:1200,height:900,left:0,top:0};}get clientWidth(){return 1200;}
  setPointerCapture(){}hasPointerCapture(){return false;}releasePointerCapture(){}
 }
 for(const match of template.matchAll(/<([a-z]+)[^>]*\bid="([^"]+)"[^>]*>/g)){const e=new Element(match[1]);e.id=match[2];roots.set(e.id,e);}
 const get=id=>roots.get(id);
 for(const [id,value] of Object.entries({'color-by':'layer',labels:'auto',separation:'60','node-spread':'35'}))get(id).value=value;
 const option=new Element('option');option.value='area';get('color-by').append(option);
 const canvas=new Element('section');canvas.className='canvas';roots.set('canvas',canvas);const filters=new Element('details');filters.className='filters';roots.set('filters',filters);
 get('map-data').textContent=JSON.stringify({map:data,check:{status:'current',pending:[]},generated_at:'2026-09-06T00:00:00Z',digest:'abc12345'});
 document={activeElement:null,getElementById:get,createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag),querySelector:s=>s==='.canvas'?canvas:filters,
 querySelectorAll:s=>s==='.node-list button'?get('node-list').children:[...roots.values()].flatMap(e=>[...(e.matches(s)?[e]:[]),...e.querySelectorAll(s)])};
 const ctx=vm.createContext({document,ResizeObserver:class{observe(){}},addEventListener(){}});
 const script=template.split('<script>')[1].split('</script>')[0];vm.runInContext(script,ctx);
 return {ctx,get,evaluate:code=>vm.runInContext(code,ctx),change:(id,value)=>{get(id).value=value;get(id).fire('change');}};
}

const before=JSON.stringify(input.map),t=run(input.map);
assert.equal(t.evaluate('view'),'atomic');assert.equal(t.get('nodes').children.length,117);
assert.equal(t.evaluate("areaLabel(map.nodes.find(n=>n.path==='site').id)"),'Recursos compartilhados');
const trackedId='area-1-node-1',point=()=>t.evaluate('JSON.stringify(worldPoint(world.get('+JSON.stringify(trackedId)+')))');
assert.equal(t.evaluate("dependency.info.get('area-1-node-0').rank"),2);
assert.equal(t.evaluate("dependency.info.get('area-1-node-3').rank"),0);
assert.equal(t.evaluate("dependency.info.get('root').rank"),null); // Documentation references don't create a dependency level.
assert.equal(t.evaluate("dependency.info.get('area-2-node-0').cycle"),true);
assert.equal(t.evaluate("dependency.info.get('area-2-node-0').rank===dependency.info.get('area-2-node-1').rank"),true);
assert.equal(t.evaluate("dependency.info.get('area-2-node-2').cycle"),true); // self-loop
// The initial placement reduces connection length while retaining each node's content band.
const connectionCost="map.relations.reduce((sum,e)=>sum+['atomic','sphere'].reduce((v,mode)=>{const a=baseWorldPoint(world.get(e.from),mode),b=baseWorldPoint(world.get(e.to),mode);return v+adjacency.get(e.from).get(e.to)*Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);},0),0)";
t.evaluate('const optimizeSlots=arrangeRelatedSlots;arrangeRelatedSlots=()=>{};makeWorld();');
const unoptimized=t.evaluate(connectionCost);t.evaluate('arrangeRelatedSlots=optimizeSlots;makeWorld();');
assert(t.evaluate(connectionCost)<unoptimized);t.evaluate('scene()');
const initial=point();
const modes=['atomic','sphere','exploded','flat'];
const nodeScreen=()=>JSON.parse(t.evaluate('JSON.stringify(positions.get('+JSON.stringify(trackedId)+'))'));
const camera=()=>t.evaluate('JSON.stringify({yaw,pitch,scale,tx,ty})');
const saved=new Map();
for(const mode of modes){
 t.get('view-'+mode).fire('click');assert.equal(t.evaluate('[...positions.values()].every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y))'),true);
 const node=t.get('nodes').children.find(n=>n.dataset.id===trackedId),before=nodeScreen(),cam=camera(),zoom=t.evaluate('scale');
 const untouched=t.evaluate('JSON.stringify(positions.get("area-1-node-3"))');
 const edgeBefore=t.get('edges').children.find(e=>e.dataset.from===trackedId).getAttribute('d');
 node.fire('pointerdown',{button:0,pointerId:1,clientX:300,clientY:350});
 t.get('graph').fire('pointermove',{pointerId:1,clientX:361,clientY:393});
 t.get('graph').fire('pointerup',{pointerId:1});
 const after=nodeScreen();assert(Math.abs((after.x-before.x)*zoom-61)<1e-6,mode+' drag x follows pointer');assert(Math.abs((after.y-before.y)*zoom-43)<1e-6,mode+' drag y follows pointer');
 assert.equal(camera(),cam);assert.equal(t.evaluate('JSON.stringify(positions.get("area-1-node-3"))'),untouched);
 assert.notEqual(t.get('edges').children.find(e=>e.dataset.from===trackedId).getAttribute('d'),edgeBefore);
 assert.equal(t.evaluate('selected'),null);saved.set(mode,t.evaluate('JSON.stringify(manualPositions.get(view).get('+JSON.stringify(trackedId)+'))'));
}
for(const mode of modes){t.get('view-'+mode).fire('click');assert.equal(t.evaluate('JSON.stringify(manualPositions.get(view).get('+JSON.stringify(trackedId)+'))'),saved.get(mode));}
t.get('view-atomic').fire('click');const atomicPoint=point();t.get('view-sphere').fire('click');assert.notEqual(point(),atomicPoint);
t.get('layout').fire('click');assert.equal(t.evaluate('[...manualPositions.values()].every(m=>m.size===0)'),true);
t.get('view-atomic').fire('click');assert.equal(point(),initial);
// Background drag rotates the scene; touching a node without dragging still selects it.
const beforeCamera=camera();t.get('graph').fire('pointerdown',{button:0,pointerId:9,clientX:400,clientY:400});t.get('graph').fire('pointermove',{pointerId:9,clientX:420,clientY:420});t.get('graph').fire('pointerup',{pointerId:9});assert.notEqual(camera(),beforeCamera);
t.get('layout').fire('click');
const clickNode=t.get('nodes').children.find(n=>n.dataset.id===trackedId);clickNode.fire('pointerdown',{button:0,pointerId:10,clientX:100,clientY:100});t.get('graph').fire('pointerup',{pointerId:10});assert.equal(t.evaluate('selected'),trackedId);t.get('close-details').fire('click');
// A slowly accumulated drag must not be mistaken for a click.
clickNode.fire('pointerdown',{button:0,pointerId:11,clientX:100,clientY:100});for(let x=101;x<108;x++)t.get('graph').fire('pointermove',{pointerId:11,clientX:x,clientY:100});t.get('graph').fire('pointerup',{pointerId:11});assert.equal(t.evaluate('selected'),null);assert.equal(t.evaluate('manualPositions.get(view).has('+JSON.stringify(trackedId)+')'),true);
const movedBeforeFilter=point();t.get('no-groups').fire('click');t.get('all-groups').fire('click');assert.equal(point(),movedBeforeFilter);t.get('layout').fire('click');

t.get('view-atomic').fire('click');t.get('no-groups').fire('click');assert.equal(t.get('nodes').children.length,1);
t.evaluate("enabledAreas.add(areas.find(a=>a.label==='MVP Factory').id);update()");assert.equal(t.get('nodes').children.length,18);assert.equal(point(),initial);
t.get('all-groups').fire('click');assert.equal(t.get('nodes').children.length,117);
t.evaluate("select('area-1-node-0')");assert(t.get('detail-body').textContent.includes('MVP Factory'));assert(t.get('detail-body').textContent.includes('specs/skill-catalog.md'));
assert(t.get('detail-body').textContent.includes('nível 2'));assert(t.get('detail-body').textContent.includes('Dependentes'));
t.evaluate("select('area-2-node-0')");assert(t.get('detail-body').textContent.includes('Ciclo registrado:'));
t.change('color-by','area');const family=t.evaluate("JSON.stringify(colorFamily('area-1-node-0'))");
assert.equal(t.evaluate("JSON.stringify(colorFamily('area-1-node-1'))"),family);
assert.notEqual(t.evaluate("JSON.stringify(colorFamily('area-2-node-0'))"),family);
assert.equal(t.evaluate("nodeColor('area-1-node-1')"),t.evaluate("nodeColor('area-1-node-2')")); // Same folder, same tone.
assert.notEqual(t.evaluate("nodeColor('area-1-node-1')"),t.evaluate("nodeColor('area-1-node-3')"));
assert.equal(point(),initial);
t.get('node-spread').value='100';t.get('node-spread').fire('input');assert.notEqual(point(),initial);
t.get('separation').value='200';t.get('separation').fire('input');
t.get('layout').fire('click');assert.equal(point(),initial);
t.get('search').value='Research Factory';t.get('search').fire('input');assert(t.get('nodes').children.length>=12);
assert.equal(JSON.stringify(input.map),before);
const old=structuredClone(input.map);delete old.navigation;old.schema_version='1.0';const legacy=run(old);assert.equal(legacy.get('nodes').children.length,117);assert(legacy.evaluate("colorFamily('area-1-node-0')[0].startsWith('folder:')"));
const partial=structuredClone(input.map),member=partial.navigation.areas[0].members.pop();partial.navigation.areas[1].members.push(partial.navigation.areas[0].members[0]);const shared=run(partial);assert.equal(shared.evaluate("areaFilters.some(a=>a.label==='Sem área revisada')"),true);assert.equal(shared.evaluate('areaMembership.get('+JSON.stringify(partial.navigation.areas[0].members[0])+').length'),2);assert(shared.evaluate('nodeColor('+JSON.stringify(partial.navigation.areas[0].members[0])+').startsWith("url(#membership-")'));assert.equal(shared.get('nodes').children.length,117);
// Reordering the input and duplicate edges must not change ranks; disconnected/empty maps stay finite.
const reversed=structuredClone(input.map);reversed.nodes.reverse();reversed.relations.reverse();const r=run(reversed);assert.equal(r.evaluate("dependency.info.get('area-1-node-0').rank"),2);
const disconnected=structuredClone(old);disconnected.relations=[];const d=run(disconnected);assert.equal(d.evaluate('dependency.unknown.length'),117);assert(d.get('dependency-summary').textContent.includes('117 sem dependência registrada'));
const empty=run({...old,nodes:[],relations:[]});assert.equal(empty.get('nodes').children.length,0);
// Restore all nodes after search before checking rendered edge semantics.
t.get('clear').fire('click');
assert(t.get('edges').children.find(e=>e.dataset.from==='area-2-node-2'&&e.dataset.to==='area-2-node-2').getAttribute('d').includes('C'));
assert(t.get('edges').children.filter(e=>e.dataset.type==='depends_on').every(e=>e.getAttribute('marker-end')==='url(#arrow)'));
assert.equal(t.get('edges').children.find(e=>e.dataset.type==='references').getAttribute('stroke-dasharray'),'4 5');
const large=structuredClone(old);large.relations=[];
for(let i=0;i<110;i++)large.nodes.push({...large.nodes[0],id:'extra-'+i,path:'extra/'+i+'.py'});
large.relations.push({from:large.nodes[0].id,to:'extra-109',type:'depends_on',rationale:'Beyond-cap fixture'});
const capped=run(large);assert.equal(capped.get('nodes').children.length,200);
capped.evaluate("select('extra-109',true)");assert.equal(capped.get('nodes').children.length,200);assert(capped.get('nodes').children.some(n=>n.dataset.id==='extra-109'));
console.log('Atomic/sphere restoration, free node dragging in four modes, camera isolation, cycles, provenance, colors, stable filters and legacy fallback passed.');
'''


def test_viewer_free_layout_and_navigation_controls() -> None:
    """Run the actual template JS against a test DOM; this does not validate browser layout."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the isolated JavaScript viewer test")
    skill = Path(__file__).resolve().parents[1]
    def make_node(identifier: str, path: str, kind: str = "code") -> dict:
        return {"id": identifier, "label": identifier, "kind": kind, "path": path,
                "summary": "Synthetic viewer fixture", "status": "existing", "authority": "supporting"}
    nodes = [make_node("root", ".", "architecture")]
    areas = []
    for index, (label, count) in enumerate(zip(
        ["Coordenação Karya", "MVP Factory", "Research Factory", "Marketing Factory", "Project Harness Factory", "Recursos compartilhados"],
        [4, 17, 12, 10, 21, 52], strict=True
    )):
        members = [make_node(f"area-{index}-node-{i}", f"sample/{index}/{i}.py") for i in range(count)]
        nodes.extend(members)
        areas.append({"id": str(index), "label": label, "rationale": "Synthetic membership declaration.",
                      "sources": ["area-5-node-1"], "members": [n["id"] for n in members]})
    by_id = {n["id"]: n for n in nodes}
    by_id["area-0-node-0"]["path"] = "skills/karya"
    by_id["area-1-node-0"]["path"] = "skills/karya-frontend-builder"
    by_id["area-1-node-1"]["path"] = "src/checkout/service.py"
    by_id["area-1-node-2"]["path"] = "src/checkout/controller.py"
    by_id["area-1-node-3"]["path"] = "src/payments/repository.py"
    by_id["area-5-node-0"].update(path="site", kind="product")
    by_id["area-5-node-1"].update(path="specs/skill-catalog.md", kind="contract")
    data = {"schema_version": "1.1", "project": {"name": "Synthetic project"}, "nodes": nodes,
            "relations": [
                {"from": a, "to": b, "type": kind, "rationale": "Synthetic explicit edge"}
                for a, b, kind in [
                    ("area-1-node-0", "area-1-node-1", "depends_on"),
                    ("area-1-node-0", "area-1-node-2", "depends_on"),
                    ("area-1-node-1", "area-1-node-3", "depends_on"),
                    ("area-1-node-2", "area-1-node-3", "depends_on"),
                    ("root", "area-1-node-0", "references"),
                    ("area-2-node-0", "area-2-node-1", "depends_on"),
                    ("area-2-node-1", "area-2-node-0", "depends_on"),
                    ("area-2-node-2", "area-2-node-2", "depends_on"),
                ]], "navigation": {"root": "root", "areas": areas}}
    template = (skill / "assets/project-map.html").read_text(encoding="utf-8")
    result = subprocess.run([node, "-e", NODE_TEST], input=json.dumps({"map": data, "template": template}), text=True,
                            encoding="utf-8", capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
